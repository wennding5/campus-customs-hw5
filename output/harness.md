# Campus Customs Database Harness

## Working database

All future database operations for HW 5 use `data/campus_customs_new.db`. The original `data/campus_customs.db` is preserved as the untouched source copy. The working copy was created from the original before any operations.

`desk.date_today` is the shop's current date (`2026-08-31`). Vendor lead times come from `vendors.lead_days`. Vendors cannot ship while their invoices are unpaid, payments require human approval, and cash balances must never become negative.

## Tables and fields

### `desk`

- `date_today` — current shop date used for due dates, ticket timing, and operating decisions.
- `notes` — shop-wide notes for agents.

Why it matters: Agents use the desk date as the authoritative current date instead of the system clock.

### `inventory`

- `sku` — product identifier; part of the composite primary key.
- `name` — product name.
- `size` — size or option for the SKU; part of the composite primary key.
- `qty` — units currently available.
- `location` — storage location.

Why it matters: Agents check real availability by product and size before promising or fulfilling orders.

### `pricing`

- `sku` — product identifier and primary key.
- `unit_cost` — vendor cost per unit.
- `list_price` — standard customer price.

Why it matters: Agents use authoritative costs and prices for customer answers and pricing decisions.

### `vendors`

- `id` — vendor identifier and primary key.
- `name` — vendor name.
- `specialty` — goods or service supplied.
- `lead_days` — expected shipping or fulfillment lead time.

Why it matters: Agents identify the supplier, calculate expected arrival using lead time, and check vendor constraints.

### `leases`

- `id` — lease identifier and primary key.
- `space_name` — rented space.
- `landlord` — landlord or payee.
- `monthly_rent` — recurring rent amount.
- `next_due` — next rent due date.
- `notes` — lease notes.

Why it matters: Agents use lease terms to resolve rent notices and schedule approved payments.

### `cash_accounts`

- `name` — account name and primary key.
- `balance` — current account balance.
- `date` — date of the recorded balance.

Why it matters: Agents verify available cash before proposing or recording a payment and must avoid negative balances.

### `payments`

- `id` — payment identifier and primary key.
- `kind` — payment category.
- `ref_id` — related lease, invoice, or other record identifier when applicable.
- `amount` — payment amount.
- `account` — cash account used.
- `paid_at` — payment timestamp.
- `approved_by` — human approver.

Why it matters: Agents use payment history to avoid duplicate payments and must not create a payment without human approval.

### `invoices`

- `id` — invoice identifier and primary key.
- `vendor_id` — foreign key to `vendors.id`.
- `amount` — amount owed.
- `due_date` — invoice due date.
- `status` — invoice state, such as open or paid.
- `description` — invoice details.

Why it matters: Agents determine whether a vendor can ship, connect bills to vendors, and route invoice payment for approval.

### `tickets`

- `id` — ticket identifier and primary key.
- `type` — ticket category.
- `requester` — person or organization requesting help.
- `subject` — short ticket subject.
- `sku` — related product SKU when applicable.
- `size` — related product size when applicable.
- `qty` — requested quantity when applicable.
- `lease_id` — foreign key to `leases.id` when the ticket concerns rent.
- `invoice_id` — foreign key to `invoices.id` when the ticket concerns a vendor invoice.
- `status` — ticket state, such as open.
- `notes` — operational details.
- `created_at` — ticket creation timestamp.

Why it matters: Agents start with tickets, follow their product, lease, and invoice references, and record the information needed to resolve each request.

## Relationships and open tickets

- `tickets.invoice_id → invoices.id → invoices.vendor_id → vendors.id`: ticket 101 points to invoice 501, which belongs to Bulldog Print Co. The invoice is open and unpaid, so the vendor cannot ship. Ticket 101 requests one `CC-TEE-WHITE` in size S, but inventory has quantity 0. An agent should explain the stockout, keep the vendor shipment blocked until the invoice is human-approved and paid, and use the vendor's 5-day lead time when communicating a possible replenishment timeline.
- `tickets.lease_id → leases.id`: ticket 102 points to lease 1 for the Chapel Street shop. Rent of $2,400 is due 2026-09-02. An agent should verify the checking balance ($3,400), obtain human approval, and ensure the approved payment leaves a non-negative balance.
- `tickets.sku/size/qty → inventory.sku/size` and `tickets.sku → pricing.sku`: ticket 103 requests 20 `CC-HOOD-NAVY` hoodies in size M. Inventory has 8, so 12 more are needed. Pricing lists a $22 unit cost and $58 list price. An agent should not invent a discount; it should calculate or propose terms from these authoritative values and confirm any vendor replenishment using the relevant vendor lead time.

No payments exist yet, so all payment actions remain pending human approval.

## MCP tools (Problem 3)

The read-only FastMCP server in `mcp_server/server.py` connects to `data/campus_customs_new.db`. It never opens or modifies the original database. Each tool returns a structured dictionary made from real SQLite rows and calculated resolution facts.

### `inspect_customer_order_ticket(ticket_id=101)`

- Reads `tickets.id`, `type`, `requester`, `subject`, `sku`, `size`, `qty`, `invoice_id`, `status`, `notes`, and `created_at` for the customer-order ticket.
- Reads `inventory.sku`, `name`, `size`, `qty`, and `location` for the requested SKU and size.
- Reads `pricing.sku`, `unit_cost`, and `list_price` for the requested SKU.
- Reads `invoices.id`, `vendor_id`, `amount`, `due_date`, `status`, and `description`, plus `vendors.id`, `name`, `specialty`, and `lead_days` through the invoice relationship.

Why it helps ticket 101: The agent needs the real size-level stock, customer price, invoice status, vendor identity, and lead time to explain the tee stockout and whether replenishment can ship.

### `inspect_rent_ticket(ticket_id=102)`

- Reads the ticket's `id`, `type`, `requester`, `subject`, `lease_id`, `status`, `notes`, and `created_at`.
- Reads the linked `leases.id`, `space_name`, `landlord`, `monthly_rent`, `next_due`, and `notes`.
- Reads every `cash_accounts.name`, `balance`, and `date`.
- Reads related `payments.id`, `kind`, `ref_id`, `amount`, `account`, `paid_at`, and `approved_by`.

Why it helps ticket 102: The agent needs the lease amount and due date, available cash, and payment history before requesting human approval for rent without risking a negative balance or duplicate payment.

### `inspect_bulk_pricing_ticket(ticket_id=103)`

- Reads the ticket's `id`, `type`, `requester`, `subject`, `sku`, `size`, `qty`, `status`, `notes`, and `created_at`.
- Reads all matching `inventory.sku`, `name`, `size`, `qty`, and `location` rows for the SKU.
- Reads `pricing.sku`, `unit_cost`, and `list_price`.
- Reads apparel or reprint candidates from `vendors.id`, `name`, `specialty`, and `lead_days`.
- Reads unpaid `invoices.id`, `vendor_id`, `amount`, `due_date`, `status`, and `description`.
- Reads `cash_accounts.name`, `balance`, and `date`.

Why it helps ticket 103: The agent needs size-M availability, the replenishment quantity, authoritative cost and list price, vendor lead times, unpaid-invoice shipping blocks, and cash context before proposing a bulk discount or replenishment plan.

## MCP connection and smoke test (Problem 4)

The Codex MCP configuration is in the workspace-root `.mcp.json` under the `campus_customs` server entry. It launches the local FastMCP server at `HW 5/mcp_server/server.py` with the MCP SDK environment and uses the absolute working-database path resolved by the server to `HW 5/data/campus_customs_new.db`.

All three tools were called through a real stdio MCP connection. The exact prompts, tool names, arguments, and returned values are recorded in `output/mcp_smoke.json`. The returned values match the working database: ticket 101 has zero size-S tees and an open invoice, ticket 102 has $2,400 rent due against $3,400 checking cash with no prior payment, and ticket 103 has 8 of 20 requested size-M hoodies with $22 cost and $58 list price.

## Multi-agent team (Problem 5)

The team is implemented in `backend/agent.py` with shared types in `backend/models.py`. Every agent uses the fixed `gpt-6-luna` model through Portkey using `PORTKEY_API_KEY`; no other model is selected. The agent layer never opens SQLite. Every shop-data fact comes from the read-only MCP server.

- **boss** — calls `list_open_tickets`, triages work, delegates to specialists, and makes the final decision.
- **inventory** — calls inventory tools to check SKU and size stock, calculate replenishment, and enforce vendor lead-time and unpaid-invoice restrictions.
- **accounting** — calls accounting and ticket tools to review cash, invoices, payments, costs, prices, and margins, then prepares payment or purchase-order recommendations for human approval.
- **facilities** — calls facilities and rent tools to handle leases, rent due dates, shop expenses, cash availability, and payment history using `desk.date_today` for overdue checks.
- **customer_service** — calls customer-service context and ticket tools to draft factual responses; it never sends them.

Every agent has a bounded `delegate_to_agent` tool that can delegate to any of the other four agents. Delegation depth is capped at 5 loops. Model requests are capped at 12 per run and tool calls at 20 per run.

### Complete MCP tool list

1. `list_open_tickets()` — reads `desk` and open `tickets`; boss triage.
2. `get_inventory_status(sku, size=None)` — reads `inventory`, `pricing`, candidate `vendors`, and open `invoices`; inventory and replenishment decisions.
3. `get_accounting_snapshot()` — reads `desk`, `cash_accounts`, `invoices`, `payments`, `pricing`, and `vendors`; accounting decisions.
4. `get_facilities_snapshot()` — reads `desk`, `leases`, `cash_accounts`, and rent `payments`; facilities decisions.
5. `get_customer_service_context(ticket_id)` — reads `tickets` and, when a SKU exists, its `inventory` and `pricing`; factual response drafts.
6. `inspect_customer_order_ticket(ticket_id=101)` — reads ticket 101, requested `inventory`, `pricing`, linked `invoices`, and `vendors`; resolves the out-of-stock tee.
7. `inspect_rent_ticket(ticket_id=102)` — reads ticket 102, linked `leases`, `cash_accounts`, and related `payments`; resolves rent review.
8. `inspect_bulk_pricing_ticket(ticket_id=103)` — reads ticket 103, SKU `inventory`, `pricing`, apparel/reprint `vendors`, open `invoices`, and `cash_accounts`; resolves the bulk hoodie request.

The added tools read these fields:

- `list_open_tickets`: `desk.date_today`, `desk.notes`; all `tickets` fields for rows with `status = 'open'`.
- `get_inventory_status`: `inventory.sku`, `name`, `size`, `qty`, `location`; `pricing.sku`, `unit_cost`, `list_price`; `vendors.id`, `name`, `specialty`, `lead_days`; and open `invoices.id`, `vendor_id`, `amount`, `due_date`, `status`, `description`.
- `get_accounting_snapshot`: all fields from `desk`, `cash_accounts`, `invoices`, `payments`, `pricing`, and `vendors`.
- `get_facilities_snapshot`: all fields from `desk`, `leases`, `cash_accounts`, and rent `payments`.
- `get_customer_service_context`: all fields from the selected `tickets` row, plus all `inventory` fields for its SKU and all `pricing` fields for that SKU when present.

### Safety and operating limits

- Customer data is limited to the ticket context needed for a draft; agents do not expose unrelated records.
- Payments, purchase orders, shipments, and outbound messages are recommendations only and require human approval. The customer-service agent drafts but never sends.
- MCP opens `campus_customs_new.db` in SQLite read-only mode. The original database is untouched, and agents cannot bypass MCP to query or modify the database.
- Agents must use `desk.date_today`, real vendor lead days, real invoice status, and real cash balances. They must not invent stock, prices, margins, dates, or shipment promises.
- Vendor shipments stay blocked for unpaid invoices; payments cannot create negative cash balances.
- Each run is bounded by 5 delegation loops, 12 model requests, and 20 tool calls. Every start, delegation, tool-call summary, result, and stop/error reason is appended as one JSON record to `output/audit_trail.json` without rewriting prior records.

## FastAPI backend routes (Problem 7)

The backend lives in `backend/main.py`. From the `backend` folder run exactly `uvicorn main:app --reload --port 8000`; the API is available at `http://localhost:8000`. Database reads and guarded writes are delegated to MCP tools; `main.py` never opens SQLite.

| Method and URL | Purpose |
|---|---|
| `GET /api/health` | Confirms the API is running and reports the fixed `gpt-6-luna` model and MCP data boundary. |
| `GET /api/tickets` | Returns tickets 101, 102, and 103 with their current open/resolved status through `get_ticket_statuses`. |
| `POST /api/tickets/{ticket_id}/run` | Runs the bounded boss-led team for one ticket ID and returns the structured decision plus recent per-agent events, statements, delegations, results, and MCP tool calls. |
| `GET /api/events?limit=50` | Returns recent append-only audit events so the dashboard can refresh agent activity. |
| `POST /api/approvals` | Applies a human-approved rent, invoice, or purchase-order payment through MCP `approve_payment`; duplicate payments, missing approvers, unpaid-shipment violations, and negative balances are rejected. |
| `GET /api/cash` | Returns the current checking account row through MCP `get_accounting_snapshot`. |
| `POST /api/reset` | Calls MCP `reset_working_database` to copy the untouched original database over the working copy for a fresh run. |
| `POST /api/restock` | Records an approved stock receipt through MCP and updates working-copy inventory idempotently. |
| `POST /api/tickets/{ticket_id}/resolve` | Records a resolution summary and marks the selected ticket resolved through MCP. |

Agent runs only prepare recommendations. Actual payment rows, cash updates, and invoice status changes occur only after `POST /api/approvals` passes the MCP transaction guards.

The route-facing MCP additions are `get_ticket_statuses()` (reads ticket status fields and desk date), `approve_payment()` (writes only the working database's `payments`, `cash_accounts`, and, for invoice payments, `invoices.status` after validating approver, duplicate, amount, and balance), `receive_restock()` (records an idempotent receipt against a human-approved invoice or purchase payment and updates `inventory`), `resolve_ticket()` (updates a ticket's status and resolution notes), and `reset_working_database()` (copies the untouched original file over the working copy without opening or changing the original for writes).

## Agent dashboard (Problem 8)

The React/Vite/TypeScript dashboard is in `frontend/` and runs with `npm run dev` at `http://localhost:5173`. It calls the FastAPI routes at `http://localhost:8000`, uses live ticket, event, and checking data, and documents its visual system in `output/design.md`.

## Problem 9 run verification

- The working copy was reset from `data/campus_customs.db` before the run. Starting `cash_accounts.checking` was **$3,400.00**; the original database remained untouched.
- Ticket 101 resolved with boss, accounting, and customer service. Human approval paid invoice 501 for **$840.00** (payment 1), then `receive_restock` recorded one CC-TEE-WHITE size-S unit and `resolve_ticket` closed the ticket.
- Ticket 102 resolved with boss, facilities, and accounting. Human approval paid lease 1 rent for **$2,400.00** (payment 2), then `resolve_ticket` closed the ticket.
- Ticket 103 remains **open**. Inventory found 8 of 20 CC-HOOD-NAVY size-M units; 12 units would cost **$264.00** with a 5-day vendor lead time. Checking was **$160.00**, creating a **$104.00** funding shortfall. No purchase, payment, receipt, discount, or customer message was fabricated.
- Cash reconciliation: `$3,400.00 - $840.00 - $2,400.00 = $160.00`. The ending value matches `cash_accounts`; only payments 1 and 2 exist, and no negative or duplicate payment occurred.
- Real agent/MCP activity was appended to `output/audit_trail.json`; the log is append-only. Ticket 103's unresolved funding and pricing-authority issue is intentionally flagged.

## Problem 9 follow-up investigation: Ticket 103

The current working database was inspected without reset. Ticket 103 still requests 20 `CC-HOOD-NAVY` size-M hoodies. `inventory` has 8 size-M units; `pricing` records a $22 unit cost and $58 list price; the 12-unit shortage costs $264. `vendors` contains only Bulldog Print Co for apparel reprint (5 days), Elm City Gifts for mugs/small goods, and QuickShip CT for local courier, so there is no qualified alternate apparel vendor. Invoice 501 is paid, and `payments` contains only the approved $840 invoice payment and $2,400 rent payment. `cash_accounts.checking` is $160.

A smaller order or partial fulfillment was not treated as a resolution because the ticket explicitly requests 20 units and no customer authorization or changed requirement is stored. Paying $264 would make checking negative by $104, and no customer-revenue, financing, or other funding record exists. The existing agent workflow therefore correctly keeps ticket 103 open. Tickets 101 and 102 remain resolved; `$3,400 - $840 - $2,400 = $160`, matching the database.
