"""Shared structured types for the Campus Customs agent team."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


AgentName = Literal["boss", "inventory", "accounting", "facilities", "customer_service"]


class Delegation(BaseModel):
    agent: AgentName
    task: str = Field(min_length=1, max_length=1200)
    reason: str = Field(min_length=1, max_length=500)


class AgentDecision(BaseModel):
    agent: AgentName
    summary: str = Field(max_length=2000)
    actions: list[str] = Field(default_factory=list, max_length=12)
    needs_human_approval: bool = False
    customer_response_draft: str | None = None
    delegations: list[Delegation] = Field(default_factory=list, max_length=8)
    stop_reason: str = Field(default="completed", max_length=300)


class TeamRunResult(BaseModel):
    boss_decision: AgentDecision
    supporting_decisions: list[AgentDecision] = Field(default_factory=list)
    audit_records_written: int = 0


class TicketAssignment(BaseModel):
    ticket_id: int
    assigned_agent: AgentName
    task: str


def json_preview(value: Any, limit: int = 800) -> str:
    text = str(value).replace("\n", " ")
    return text if len(text) <= limit else text[: limit - 1] + "…"
