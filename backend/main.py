"""FastAPI dashboard routes for the Campus Customs agent team."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent import run_team
from mcp_server.server import (
    approve_payment,
    get_accounting_snapshot,
    get_ticket_statuses,
    receive_restock,
    reset_working_database,
    resolve_ticket,
)


ROOT = Path(__file__).resolve().parent.parent
AUDIT_PATH = ROOT / "output" / "audit_trail.json"
TICKET_IDS = {101, 102, 103}

app = FastAPI(title="Campus Customs Agent Dashboard API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ApprovalRequest(BaseModel):
    kind: str = Field(description="rent, invoice, or purchase_order")
    ref_id: int | None = None
    amount: float = Field(gt=0)
    account: str = "checking"
    approved_by: str = Field(min_length=1)
    description: str = ""


class RestockRequest(BaseModel):
    sku: str
    size: str
    qty: int = Field(gt=0)
    source_payment_id: int = Field(gt=0)


class ResolutionRequest(BaseModel):
    resolution: str = Field(min_length=1)


def _recent_events(limit: int) -> list[dict[str, Any]]:
    if not AUDIT_PATH.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in AUDIT_PATH.read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events[-limit:]


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model": "gpt-6-luna", "data_boundary": "MCP"}


@app.get("/api/tickets")
def tickets() -> dict[str, Any]:
    """Return tickets 101–103 with their current open/resolved status."""
    return get_ticket_statuses()


@app.post("/api/tickets/{ticket_id}/run")
async def run_ticket(ticket_id: int) -> dict[str, Any]:
    """Run the bounded boss-led team for one ticket and return its latest events."""
    if ticket_id not in TICKET_IDS:
        raise HTTPException(status_code=404, detail="Ticket must be 101, 102, or 103")
    try:
        result = await run_team(
            f"Work only on Campus Customs ticket {ticket_id}. Triage it, delegate only to relevant specialists, and return the final recommendation. Do not execute payments or send messages."
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent run failed: {type(exc).__name__}: {exc}") from exc
    return {
        "ticket_id": ticket_id,
        "decision": result.boss_decision.model_dump(),
        "events": _recent_events(100),
    }


@app.get("/api/events")
def events(limit: int = Query(50, ge=1, le=500)) -> dict[str, Any]:
    """Return recent append-only agent events for dashboard refreshes."""
    return {"events": _recent_events(limit)}


@app.post("/api/approvals")
def approve(request: ApprovalRequest) -> dict[str, Any]:
    """Apply a human-approved payment or purchase through the guarded MCP tool."""
    try:
        return approve_payment(**request.model_dump())
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/cash")
def cash() -> dict[str, Any]:
    """Return the current checking balance through the accounting MCP tool."""
    snapshot = get_accounting_snapshot()
    checking = next((row for row in snapshot["cash_accounts"] if row["name"] == "checking"), None)
    if checking is None:
        raise HTTPException(status_code=404, detail="Checking account not found")
    return checking


@app.post("/api/reset")
def reset() -> dict[str, Any]:
    """Restore the working database from the untouched original via MCP."""
    try:
        return reset_working_database()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/restock")
def restock(request: RestockRequest) -> dict[str, Any]:
    try:
        return receive_restock(**request.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/tickets/{ticket_id}/resolve")
def resolve(ticket_id: int, request: ResolutionRequest) -> dict[str, Any]:
    if ticket_id not in TICKET_IDS:
        raise HTTPException(status_code=404, detail="Ticket must be 101, 102, or 103")
    try:
        return resolve_ticket(ticket_id, request.resolution)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
