# Campus Customs HW5

Campus Customs is a FastMCP + PydanticAI + FastAPI + React/Vite assignment. The five agents (boss, inventory, accounting, facilities, and customer service) use MCP tools for all shop data. Payments require a named human approval and the MCP guards prevent duplicate payments and negative checking balances.

## Repository layout

- `data/campus_customs.db` is the untouched source database.
- `data/campus_customs_new.db` is the working database and contains the recorded final run.
- `mcp_server/` contains the FastMCP server and tool documentation.
- `backend/` contains the agents, prompts, models, and FastAPI app.
- `frontend/` contains the React/Vite dashboard.
- `output/` contains the harness, plans, audit trail, JSON results, and standalone HTML reports.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install
```

Set `PORTKEY_API_KEY` in a local `.env` (never commit it). `.env.example` is only a placeholder. The agents are configured for Portkey and `gpt-6-luna`.

## Run the MCP server

From the project root:

```bash
python3 mcp_server/server.py
```

The server uses stdio transport. The project-local `.mcp.json` uses the relative server path and contains no secret or machine-specific path.

## Run the FastAPI backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API is available at `http://localhost:8000`.

## Run the React dashboard

In another terminal:

```bash
cd frontend
npm run dev
```

The dashboard is available at `http://localhost:5173`.

## Clean reset and rerun

The original database is preserved. To make a fresh working copy before rerunning all three tickets, call the guarded reset route while the backend is running:

```bash
curl -X POST http://localhost:8000/api/reset
```

This copies `data/campus_customs.db` over `data/campus_customs_new.db` and does not modify the original. Then use the dashboard to run tickets 101, 102, and 103. Approve payments only through the dashboard approval flow.

## Evidence

Open `output/desk_tickets.html` and `output/resolved_board.html` directly in a browser. The board report uses relative paths under `output/board_screens/`. `output/resolved_tickets.json` and the append-only `output/audit_trail.json` record the actual run. Ticket 103 is resolved as a Boss pricing decision at the authoritative $58 list price. No replenishment purchase or cash movement was required; ending checking is $160 after the approved $840 invoice and $2,400 rent payments.
