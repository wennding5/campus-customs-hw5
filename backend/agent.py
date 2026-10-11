"""PydanticAI multi-agent team for Campus Customs.

Every shop-data lookup is supplied by the read-only FastMCP server. This
module never opens SQLite directly.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from models import AgentDecision, AgentName, TeamRunResult, json_preview
load_dotenv(ROOT.parent / ".env")
load_dotenv(ROOT / ".env")

MODEL_NAME = "gpt-6-luna"
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1").rstrip("/")
MAX_AGENT_LOOPS = 5
MAX_TOOL_CALLS = 20
MAX_MODEL_REQUESTS = 12
AUDIT_PATH = ROOT / "output" / "audit_trail.json"
PROMPT_DIR = HERE / "prompts"

_audit_lock = threading.Lock()


def _mcp_toolset() -> MCPToolset:
    from mcp_server.server import mcp

    return MCPToolset(mcp)


def _model() -> OpenAIResponsesModel:
    api_key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not set in the workspace .env file")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": api_key},
    )
    return OpenAIResponsesModel(
        MODEL_NAME,
        provider=OpenAIProvider(openai_client=client),
    )


def _append_audit(record: dict[str, Any]) -> None:
    """Append one JSON object per line; existing records are never rewritten."""
    with _audit_lock:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _audit(agent_name: AgentName, action: str, **data: Any) -> None:
    _append_audit(
        {
            "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "agent_name": agent_name,
            "action": action,
            **data,
        }
    )


def _build_agents() -> dict[AgentName, Agent[Any, AgentDecision]]:
    agents: dict[AgentName, Agent[Any, AgentDecision]] = {}
    for name in ("boss", "inventory", "accounting", "facilities", "customer_service"):
        prompt = (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")
        agent = Agent(
            _model(),
            instructions=prompt,
            output_type=AgentDecision,
            toolsets=[_mcp_toolset()],
            model_settings=OpenAIResponsesModelSettings(openai_reasoning_summary="auto"),
        )
        agents[name] = agent

    async def delegate_to_agent(
        ctx: RunContext[dict[str, Any]], agent_name: AgentName, task: str
    ) -> dict[str, Any]:
        """Delegate a bounded factual task to any other team member."""
        current = str(ctx.deps.get("current_agent", "unknown"))
        if agent_name == current:
            return {"error": "An agent cannot delegate to itself."}
        depth = int(ctx.deps.get("depth", 0))
        if depth >= MAX_AGENT_LOOPS:
            return {"error": "Delegation limit reached; make a decision from available facts."}
        _audit(current, "delegation", delegated_to=agent_name, task=task, depth=depth)
        result = await agents[agent_name].run(
            task,
            deps={"current_agent": agent_name, "depth": depth + 1},
            usage_limits=UsageLimits(
                request_limit=MAX_MODEL_REQUESTS,
                tool_calls_limit=MAX_TOOL_CALLS,
            ),
        )
        calls, delegated = _message_facts(result.new_messages())
        _audit(
            agent_name,
            "run_complete",
            actions=result.output.actions,
            tool_calls=calls,
            delegation=delegated,
            result=result.output.model_dump(),
            stop_reason=result.output.stop_reason,
        )
        return {
            "agent": agent_name,
            "summary": result.output.summary,
            "actions": result.output.actions,
            "needs_human_approval": result.output.needs_human_approval,
        }

    for agent in agents.values():
        agent.tool(delegate_to_agent)
    return agents


def _message_facts(messages: list[Any]) -> tuple[list[dict[str, Any]], list[str]]:
    calls: list[dict[str, Any]] = []
    delegations: list[str] = []
    for message in messages:
        for part in getattr(message, "parts", []):
            tool_name = getattr(part, "tool_name", None)
            if tool_name:
                args = getattr(part, "args_as_dict", lambda: {})()
                calls.append({"tool": tool_name, "args": args})
                if tool_name == "delegate_to_agent":
                    delegations.append(str(args.get("agent_name", "unknown")))
            if part.__class__.__name__ == "ToolReturnPart":
                if calls:
                    calls[-1]["result"] = json_preview(getattr(part, "content", ""))
    return calls, delegations


async def run_team(task: str) -> TeamRunResult:
    """Run the boss with bounded delegation and append-only loop records."""
    agents = _build_agents()
    _audit("boss", "run_start", task=task, model=MODEL_NAME, max_loops=MAX_AGENT_LOOPS)
    try:
        result = await agents["boss"].run(
            task,
            deps={"current_agent": "boss", "depth": 0},
            usage_limits=UsageLimits(
                request_limit=MAX_MODEL_REQUESTS,
                tool_calls_limit=MAX_TOOL_CALLS,
            ),
        )
        calls, delegations = _message_facts(result.new_messages())
        _audit(
            "boss",
            "run_complete",
            actions=result.output.actions,
            tool_calls=calls,
            delegation=delegations,
            result=result.output.model_dump(),
            stop_reason=result.output.stop_reason,
        )
        return TeamRunResult(boss_decision=result.output, audit_records_written=2)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"[:500]
        _audit("boss", "run_error", tool_calls=[], delegation=[], result=None, stop_reason=detail)
        raise


if __name__ == "__main__":
    import asyncio

    print(asyncio.run(run_team("Triage all open Campus Customs tickets and recommend next steps.")))
