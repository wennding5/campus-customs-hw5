"""Read-only MCP tools for resolving the Campus Customs desk tickets."""

from __future__ import annotations

import sqlite3
import shutil
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


DB_PATH = Path(__file__).resolve().parents[1] / "data" / "campus_customs_new.db"
ORIGINAL_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "campus_customs.db"
mcp = FastMCP("campus-customs")


def _connect() -> sqlite3.Connection:
    """Open the designated working copy in read-only SQLite mode."""
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"Working database not found: {DB_PATH}")
    connection = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _one(connection: sqlite3.Connection, query: str, params: tuple[Any, ...]) -> dict[str, Any]:
    row = connection.execute(query, params).fetchone()
    if row is None:
        raise ValueError("Requested ticket or related record was not found")
    return dict(row)


def _many(connection: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(query, params).fetchall()]


def _write_connect() -> sqlite3.Connection:
    """Open only the working database for guarded, transactional writes."""
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"Working database not found: {DB_PATH}")
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@mcp.tool()
def list_open_tickets() -> dict[str, Any]:
    """List all open desk tickets for the boss agent."""
    with _connect() as connection:
        desk = _one(connection, "SELECT * FROM desk LIMIT 1", ())
        tickets = _many(connection, "SELECT * FROM tickets WHERE status = 'open' ORDER BY id")
        return {"desk": desk, "tickets": tickets}


@mcp.tool()
def get_inventory_status(sku: str, size: str | None = None) -> dict[str, Any]:
    """Read inventory, price, and replenishment context for a SKU and optional size."""
    with _connect() as connection:
        stock = _many(
            connection,
            "SELECT * FROM inventory WHERE sku = ? AND (? IS NULL OR size = ?) ORDER BY size",
            (sku, size, size),
        )
        pricing = _one(connection, "SELECT * FROM pricing WHERE sku = ?", (sku,))
        vendors = _many(
            connection,
            "SELECT * FROM vendors WHERE specialty LIKE '%apparel%' OR specialty LIKE '%mug%' ORDER BY id",
        )
        open_invoices = _many(connection, "SELECT * FROM invoices WHERE status <> 'paid' ORDER BY id")
        return {
            "sku": sku,
            "size": size,
            "inventory": stock,
            "pricing": pricing,
            "candidate_vendors": vendors,
            "open_invoices": open_invoices,
        }


@mcp.tool()
def get_accounting_snapshot() -> dict[str, Any]:
    """Read cash, invoices, payments, and pricing needed for accounting decisions."""
    with _connect() as connection:
        return {
            "desk": _one(connection, "SELECT * FROM desk LIMIT 1", ()),
            "cash_accounts": _many(connection, "SELECT * FROM cash_accounts ORDER BY name"),
            "invoices": _many(connection, "SELECT * FROM invoices ORDER BY id"),
            "payments": _many(connection, "SELECT * FROM payments ORDER BY id"),
            "pricing": _many(connection, "SELECT * FROM pricing ORDER BY sku"),
            "vendors": _many(connection, "SELECT * FROM vendors ORDER BY id"),
        }


@mcp.tool()
def get_facilities_snapshot() -> dict[str, Any]:
    """Read shop date, leases, cash, and rent payment history for facilities."""
    with _connect() as connection:
        return {
            "desk": _one(connection, "SELECT * FROM desk LIMIT 1", ()),
            "leases": _many(connection, "SELECT * FROM leases ORDER BY id"),
            "cash_accounts": _many(connection, "SELECT * FROM cash_accounts ORDER BY name"),
            "rent_payments": _many(connection, "SELECT * FROM payments WHERE kind = 'rent' ORDER BY id"),
        }


@mcp.tool()
def get_customer_service_context(ticket_id: int) -> dict[str, Any]:
    """Read only the ticket and factual product context needed to draft a response."""
    with _connect() as connection:
        ticket = _one(connection, "SELECT * FROM tickets WHERE id = ?", (ticket_id,))
        product: dict[str, Any] | None = None
        if ticket["sku"]:
            product = {
                "inventory": _many(
                    connection,
                    "SELECT * FROM inventory WHERE sku = ? ORDER BY size",
                    (ticket["sku"],),
                ),
                "pricing": _one(connection, "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],)),
            }
        return {"ticket": ticket, "product": product}


@mcp.tool()
def get_ticket_statuses() -> dict[str, Any]:
    """Return the three assignment tickets and their current statuses."""
    with _connect() as connection:
        tickets = _many(
            connection,
            "SELECT id, type, requester, subject, status, created_at FROM tickets WHERE id IN (101, 102, 103) ORDER BY id",
        )
        return {"tickets": tickets, "desk": _one(connection, "SELECT * FROM desk LIMIT 1", ())}


@mcp.tool()
def approve_payment(
    kind: str,
    ref_id: int | None,
    amount: float,
    account: str,
    approved_by: str,
    description: str = "",
) -> dict[str, Any]:
    """Record a human-approved payment on the working DB with duplicate and cash guards."""
    if not approved_by.strip():
        raise ValueError("Human approver is required")
    if amount <= 0:
        raise ValueError("Payment amount must be positive")
    if kind not in {"rent", "invoice", "purchase_order"}:
        raise ValueError("kind must be rent, invoice, or purchase_order")
    with _write_connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        account_row = connection.execute(
            "SELECT name, balance FROM cash_accounts WHERE name = ?", (account,)
        ).fetchone()
        if account_row is None:
            raise ValueError("Cash account does not exist")
        duplicate = connection.execute(
            "SELECT id FROM payments WHERE kind = ? AND ref_id IS ? AND amount = ? LIMIT 1",
            (kind, ref_id, amount),
        ).fetchone()
        if duplicate is not None:
            raise ValueError(f"Duplicate payment already exists as payment {duplicate['id']}")
        new_balance = account_row["balance"] - amount
        if new_balance < 0:
            raise ValueError("Payment would create a negative cash balance")
        now = connection.execute("SELECT date_today FROM desk LIMIT 1").fetchone()[0]
        cursor = connection.execute(
            """INSERT INTO payments(kind, ref_id, amount, account, paid_at, approved_by)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (kind, ref_id, amount, account, now, approved_by.strip()),
        )
        connection.execute(
            "UPDATE cash_accounts SET balance = ?, date = ? WHERE name = ?",
            (new_balance, now, account),
        )
        if kind == "invoice" and ref_id is not None:
            connection.execute("UPDATE invoices SET status = 'paid' WHERE id = ?", (ref_id,))
        return {
            "payment_id": cursor.lastrowid,
            "kind": kind,
            "ref_id": ref_id,
            "amount": amount,
            "account": account,
            "approved_by": approved_by.strip(),
            "new_balance": new_balance,
            "description": description,
        }


@mcp.tool()
def receive_restock(sku: str, size: str, qty: int, source_payment_id: int) -> dict[str, Any]:
    """Receive stock only against an existing approved invoice or purchase payment."""
    if qty <= 0:
        raise ValueError("Restock quantity must be positive")
    with _write_connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        payment = connection.execute(
            "SELECT id, kind, approved_by FROM payments WHERE id = ?", (source_payment_id,)
        ).fetchone()
        if payment is None or not payment["approved_by"] or payment["kind"] not in {"invoice", "purchase_order"}:
            raise ValueError("Restock requires an existing human-approved invoice or purchase payment")
        connection.execute(
            """CREATE TABLE IF NOT EXISTS restock_receipts (
                payment_id INTEGER NOT NULL,
                sku TEXT NOT NULL,
                size TEXT NOT NULL,
                qty INTEGER NOT NULL,
                received_at TEXT NOT NULL,
                PRIMARY KEY (payment_id, sku, size)
            )"""
        )
        try:
            connection.execute(
                "INSERT INTO restock_receipts(payment_id, sku, size, qty, received_at) VALUES (?, ?, ?, ?, (SELECT date_today FROM desk LIMIT 1))",
                (source_payment_id, sku, size, qty),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("This approved payment has already received this SKU and size") from exc
        inventory = connection.execute(
            "SELECT qty FROM inventory WHERE sku = ? AND size = ?", (sku, size)
        ).fetchone()
        if inventory is None:
            raise ValueError("SKU and size are not present in inventory")
        connection.execute("UPDATE inventory SET qty = qty + ? WHERE sku = ? AND size = ?", (qty, sku, size))
        updated = connection.execute("SELECT * FROM inventory WHERE sku = ? AND size = ?", (sku, size)).fetchone()
        return {"received": qty, "source_payment_id": source_payment_id, "inventory": dict(updated)}


@mcp.tool()
def resolve_ticket(ticket_id: int, resolution: str) -> dict[str, Any]:
    """Mark a ticket resolved after its real operational work is complete."""
    if not resolution.strip():
        raise ValueError("Resolution summary is required")
    with _write_connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        ticket = connection.execute("SELECT id, notes FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if ticket is None:
            raise ValueError("Ticket does not exist")
        connection.execute(
            "UPDATE tickets SET status = 'resolved', notes = ? WHERE id = ?",
            (f"{ticket['notes'] or ''} Resolution: {resolution.strip()}", ticket_id),
        )
        updated = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return {"ticket": dict(updated)}


@mcp.tool()
def record_price_decision(ticket_id: int, unit_price: float, rationale: str, decided_by: str = "boss") -> dict[str, Any]:
    """Record an authorized price_override decision and resolve it without moving cash."""
    if unit_price <= 0 or not rationale.strip() or not decided_by.strip():
        raise ValueError("A positive price, rationale, and decision maker are required")
    with _write_connect() as connection:
        connection.execute("BEGIN IMMEDIATE")
        ticket = connection.execute("SELECT * FROM tickets WHERE id = ? AND type = 'price_override'", (ticket_id,)).fetchone()
        if ticket is None:
            raise ValueError("Price-override ticket does not exist")
        pricing = connection.execute("SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],)).fetchone()
        if pricing is None:
            raise ValueError("Pricing record does not exist")
        if unit_price < pricing["unit_cost"] or unit_price > pricing["list_price"]:
            raise ValueError("Decision price must be between unit cost and list price")
        connection.execute("""CREATE TABLE IF NOT EXISTS pricing_decisions (
            ticket_id INTEGER PRIMARY KEY, unit_price REAL NOT NULL, rationale TEXT NOT NULL,
            decided_by TEXT NOT NULL, decided_at TEXT NOT NULL
        )""")
        try:
            connection.execute("INSERT INTO pricing_decisions VALUES (?, ?, ?, ?, (SELECT date_today FROM desk LIMIT 1))", (ticket_id, unit_price, rationale.strip(), decided_by.strip()))
        except sqlite3.IntegrityError as exc:
            raise ValueError("A pricing decision already exists for this ticket") from exc
        resolution = f"Pricing decision recorded at ${unit_price:.2f} per unit by {decided_by.strip()}: {rationale.strip()}"
        connection.execute("UPDATE tickets SET status = 'resolved', notes = ? WHERE id = ?", (f"{ticket['notes'] or ''} Resolution: {resolution}", ticket_id))
        return {"ticket_id": ticket_id, "unit_price": unit_price, "decided_by": decided_by.strip(), "resolution": resolution, "cash_change": 0.0, "status": "resolved"}


@mcp.tool()
def reset_working_database() -> dict[str, Any]:
    """Reset the working DB from the untouched original and return both file paths."""
    if not ORIGINAL_DB_PATH.is_file():
        raise FileNotFoundError(f"Original database not found: {ORIGINAL_DB_PATH}")
    shutil.copy2(ORIGINAL_DB_PATH, DB_PATH)
    return {"reset": True, "original": str(ORIGINAL_DB_PATH), "working": str(DB_PATH)}


@mcp.tool()
def inspect_customer_order_ticket(ticket_id: int = 101) -> dict[str, Any]:
    """Return stock, price, vendor, and invoice facts needed for customer order ticket 101."""
    with _connect() as connection:
        ticket = _one(
            connection,
            "SELECT * FROM tickets WHERE id = ? AND type = 'customer_order'",
            (ticket_id,),
        )
        inventory = _one(
            connection,
            "SELECT * FROM inventory WHERE sku = ? AND size = ?",
            (ticket["sku"], ticket["size"]),
        )
        pricing = _one(connection, "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],))
        invoice = _one(
            connection,
            """SELECT i.*, v.name AS vendor_name, v.specialty, v.lead_days
               FROM invoices AS i JOIN vendors AS v ON v.id = i.vendor_id
               WHERE i.id = ?""",
            (ticket["invoice_id"],),
        )
        return {
            "ticket": ticket,
            "inventory": inventory,
            "pricing": pricing,
            "invoice_and_vendor": invoice,
            "resolution_facts": {
                "requested_qty": ticket["qty"],
                "available_qty": inventory["qty"],
                "shortfall": max(ticket["qty"] - inventory["qty"], 0),
                "vendor_can_ship": invoice["status"].lower() == "paid",
            },
        }


@mcp.tool()
def prepare_price_override(ticket_id: int = 103) -> dict[str, Any]:
    """Prepare a pricing recommendation for a price_override ticket without purchasing stock or changing data."""
    with _connect() as connection:
        ticket = _one(connection, "SELECT * FROM tickets WHERE id = ? AND type = 'price_override'", (ticket_id,))
        pricing = _one(connection, "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],))
        requested = _one(connection, "SELECT * FROM inventory WHERE sku = ? AND size = ?", (ticket["sku"], ticket["size"]))
        approved_discount = _many(connection, "SELECT date_today, notes FROM desk WHERE notes LIKE '%discount%' OR notes LIKE '%pricing%'")
        return {
            "ticket": ticket,
            "pricing": pricing,
            "requested_size_stock": requested,
            "pricing_authorization_records": approved_discount,
            "recommendation": {
                "list_price": pricing["list_price"],
                "unit_cost_floor": pricing["unit_cost"],
                "discount_rate": None,
                "discount_amount": None,
                "reason": "No authorized discount rate is stored; preserve list price until a human approves a specific discount.",
                "stock_note": f"{requested['qty']} of {ticket['qty']} requested units are currently available; pricing analysis does not create a purchase obligation."
            },
            "needs_human_approval": True,
            "changes_made": False,
        }


@mcp.tool()
def inspect_rent_ticket(ticket_id: int = 102) -> dict[str, Any]:
    """Return lease, cash, and payment facts needed for rent ticket 102."""
    with _connect() as connection:
        ticket = _one(
            connection,
            "SELECT * FROM tickets WHERE id = ? AND type = 'rent_notice'",
            (ticket_id,),
        )
        lease = _one(connection, "SELECT * FROM leases WHERE id = ?", (ticket["lease_id"],))
        accounts = _many(connection, "SELECT * FROM cash_accounts ORDER BY name")
        related_payments = _many(
            connection,
            """SELECT * FROM payments
               WHERE (kind = 'rent' AND ref_id = ?) OR ref_id = ?
               ORDER BY id""",
            (lease["id"], ticket["id"]),
        )
        return {
            "ticket": ticket,
            "lease": lease,
            "cash_accounts": accounts,
            "related_payments": related_payments,
            "resolution_facts": {
                "rent_due": lease["monthly_rent"],
                "due_date": lease["next_due"],
                "human_approval_required": True,
                "negative_balance_allowed": False,
            },
        }


@mcp.tool()
def inspect_bulk_pricing_ticket(ticket_id: int = 103) -> dict[str, Any]:
    """Return stock, pricing, replenishment, and cash facts needed for bulk ticket 103."""
    with _connect() as connection:
        ticket = _one(
            connection,
            "SELECT * FROM tickets WHERE id = ? AND type = 'price_override'",
            (ticket_id,),
        )
        stock = _many(
            connection,
            "SELECT * FROM inventory WHERE sku = ? ORDER BY size",
            (ticket["sku"],),
        )
        pricing = _one(connection, "SELECT * FROM pricing WHERE sku = ?", (ticket["sku"],))
        vendors = _many(
            connection,
            "SELECT * FROM vendors WHERE specialty LIKE '%apparel%' OR specialty LIKE '%reprint%' ORDER BY id",
        )
        open_invoices = _many(
            connection,
            "SELECT * FROM invoices WHERE status <> 'paid' ORDER BY id",
        )
        cash_accounts = _many(connection, "SELECT * FROM cash_accounts ORDER BY name")
        requested_row = next((row for row in stock if row["size"] == ticket["size"]), None)
        available = requested_row["qty"] if requested_row else 0
        return {
            "ticket": ticket,
            "requested_size_stock": requested_row,
            "all_sku_stock": stock,
            "pricing": pricing,
            "candidate_vendors": vendors,
            "open_invoices": open_invoices,
            "cash_accounts": cash_accounts,
            "resolution_facts": {
                "requested_qty": ticket["qty"],
                "available_requested_size_qty": available,
                "replenishment_qty": max(ticket["qty"] - available, 0),
                "list_total": ticket["qty"] * pricing["list_price"],
                "unit_cost_total": ticket["qty"] * pricing["unit_cost"],
                "human_approval_required_for_payment": True,
            },
        }


if __name__ == "__main__":
    mcp.run()
