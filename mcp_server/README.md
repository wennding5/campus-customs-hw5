# Campus Customs MCP Server

This directory contains a read-only [FastMCP](https://github.com/modelcontextprotocol/python-sdk) server for the five agents used in later HW 5 problems. It reads only the working database at `../data/campus_customs_new.db`; the original `../data/campus_customs.db` is never opened for operations and is not modified.

## Tools

The complete tool list is:

`list_open_tickets()` reads `desk` and all open `tickets` for the boss agent's triage.

`get_inventory_status(sku, size=None)` reads matching `inventory`, `pricing`, candidate `vendors`, and open `invoices` for stock and replenishment decisions.

`inspect_customer_order_ticket(ticket_id=101)` reads the ticket, the requested SKU and size from `inventory`, its price from `pricing`, and the linked `invoices` and `vendors` rows. It gives an agent the stock shortfall, price, invoice status, vendor, and lead time needed to resolve the out-of-stock Bulldog tee request.

`inspect_rent_ticket(ticket_id=102)` reads the ticket, linked `leases` row, all `cash_accounts`, and related `payments`. It gives an agent the rent amount and due date, available cash, payment history, and the human-approval/non-negative-balance constraints.

`inspect_bulk_pricing_ticket(ticket_id=103)` reads the ticket, all size rows for the requested SKU from `inventory`, the SKU's `pricing`, apparel/reprint `vendors`, open `invoices`, and `cash_accounts`. It gives an agent the available quantity, replenishment amount, authoritative cost and list price, vendor lead-time options, unpaid-invoice blocks, and cash context needed for the bulk hoodie request.

`get_accounting_snapshot()` reads `desk`, `cash_accounts`, `invoices`, `payments`, `pricing`, and `vendors` for cash, invoice, margin, and purchase-order preparation.

`get_facilities_snapshot()` reads `desk`, `leases`, `cash_accounts`, and rent `payments` for lease and shop-expense decisions.

`get_customer_service_context(ticket_id)` reads a ticket and, when present, its SKU's `inventory` and `pricing` for a factual draft response.

`get_ticket_statuses()` reads the three assignment ticket IDs, subjects, types, statuses, requesters, creation times, and the shop date for the dashboard.

`approve_payment(kind, ref_id, amount, account, approved_by, description)` is the only guarded write tool. It records a human-approved rent, invoice, or purchase-order payment on `campus_customs_new.db`, rejects duplicates, requires positive amounts and a named approver, blocks negative balances, and marks an invoice paid when appropriate.

`reset_working_database()` copies the untouched original database over the working copy for a fresh run. It never writes to the original.

`receive_restock(sku, size, qty, source_payment_id)` records an idempotent stock receipt only when the source payment was human-approved as an invoice or purchase order.

`resolve_ticket(ticket_id, resolution)` records a real resolution summary and changes that ticket's status to `resolved` in the working copy.

All tools return JSON-serializable structured dictionaries and perform `SELECT` queries through SQLite read-only mode. They do not insert, update, delete, or alter either database.

## Later connection

Install the Python MCP SDK in the agent environment, then run `python3 mcp_server/server.py` from the HW 5 folder when the agents are ready to connect. The server uses stdio transport through FastMCP's default `run()` behavior.
