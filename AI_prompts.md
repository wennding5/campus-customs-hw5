## Problem 1 — Vibe coder prompts

1. Prompt typed: “Create an `AI_prompts.md` file at the root of my HW 5 project as a running log of every prompt I give for this assignment. Organize it with one section per problem, labeled with the problem number and title. Start with Problem 1, preserve earlier entries, add follow-up prompts in order, explain what was missing after each previous prompt when applicable, and keep updating the file automatically under the correct problem section.”
2. Follow-up prompts: “Add a follow-up prompt section and include every follow-up prompt I give. Record this follow-up, and add sentence(s) explaining what was lacking after the previous prompt.” and “Follow the format of HW 4 AI_prompts.md.”
3. The first version did not use the requested HW 4 format, which includes a `Prompt typed:` entry, a `Follow-up prompts:` entry, and a numbered explanation of what was lacking after the previous prompt.

## Problem 2 — Study the Campus Customs database

1. Prompt typed: “Study `data/campus_customs.db` in full: understand every table, field, and relationship, including desk tickets, inventory, pricing, vendors, leases, cash accounts, payments, and invoices. Analyze the three open tickets and determine how they connect to the other tables and what agents need to do to resolve them. Copy the original database to `data/campus_customs_new.db`, use the copy for all future operations, and leave the original untouched. Treat `desk.date_today` as the shop's current date, use vendor lead times from `vendors`, prevent vendors from shipping against unpaid invoices, require human approval for payments, and never allow negative cash balances. Create `output/harness.md` listing every table, every field, and why each table matters to agents, keep updating it in later problems, and add this prompt to `AI_prompts.md` under Problem 2.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 3 — Build the MCP server

1. Prompt typed: “Build a FastMCP server in `mcp_server/` that reads the working database `data/campus_customs_new.db` for the five agents that will use it later. First inspect tickets 101, 102, and 103 and their related tables, then create three clearly named read-only tools that return useful structured real data for resolving those tickets. Do not invent data, modify either database, or run the server yet. Document all three tools in `output/harness.md`, including every table and field each tool reads, the ticket it supports, and why the information matters. Add `mcp_server/README.md` explaining the server, database, and tools, make the code ready for later agent connections, and log this prompt under Problem 3.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 4 — Add the MCP server to vibe coder and test each tool

1. Prompt typed: “Connect the Problem 3 MCP server to this Codex project so its tools can be called directly. Save the connection in the project’s `.mcp.json` or the correct local Codex MCP configuration, point it at `data/campus_customs_new.db` and the correct server path, and call all three tools through the MCP connection using real ticket data. Create `output/mcp_smoke.json` containing each test prompt, tool name, arguments, and actual output. Verify those outputs against the working database, fix any connection or tool failures, do not invent results, and log this prompt under Problem 4.”
2. Follow-up prompts: “Why is Problem 4 before Problem 3 in AI prompts?”
3. The Problem 4 section had been inserted before Problem 3, so the problem sections were out of numerical order.

## Problem 5 — Build the agent team and grow the MCP tools

1. Prompt typed: “Build the Campus Customs PydanticAI multi-agent team with five agents named boss, inventory, accounting, facilities, and customer service. Give each agent a detailed prompt in `backend/prompts/`, shared structured types in `backend/models.py`, and agent code in `backend/`. The boss must triage and decide, specialists must handle their domains, and every agent must be able to delegate to any teammate. Route every AI call through Portkey with `PORTKEY_API_KEY` and only `gpt-6-luna`. Expand the read-only MCP server with all tools needed for tickets 101–103; agents must use MCP for all shop data and never query the database directly or invent facts. Enforce shop date, lead-time, unpaid-invoice, human-approval, and non-negative-cash rules, and do not contact customers or vendors. Add append-only per-step agent audit records to `output/audit_trail.json`, including actions, tools, results, delegation, and stop reasons. Update `output/harness.md` with all agents, tools, tables, safety rules, and loop/tool/token limits, update the MCP README with the complete tool list, keep everything connected and ready for later problems, and log this prompt under Problem 5.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 6 — Plan the three tickets

1. Prompt typed: “Before building the backend, create a standalone `output/desk_tickets.html` page with working tabs for tickets 101, 102, 103, cash, and reflection. Read the real ticket and related records from `data/campus_customs_new.db` through the existing MCP tools. For each ticket, document a detailed expected resolution plan, the first agent boss should contact and why, every relevant delegation in order with its reason, the exact MCP tools and needed information, and the shop rules around cash, unpaid invoices, vendor lead times, and human approvals. Use only agents relevant to that ticket, leave an empty actual section for later comparison, leave cash and reflection blank or marked coming later, make the page clean and directly openable, and log this prompt under Problem 6.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 7 — Backend routes

1. Prompt typed: “Build `backend/main.py` as the FastAPI backend for the React dashboard and connect it to the agent team and MCP server. Add routes for the three ticket statuses, running the team for one ticket ID, recent agent events with each agent’s statements and MCP tools, human approval of prepared payments or purchases, current checking balance, and resetting `data/campus_customs_new.db` from the untouched original. Keep all database access behind MCP, enforce duplicate-payment and non-negative-cash guards, keep the original database unchanged, use only Portkey `gpt-6-luna`, preserve audit logging, test every route, run from the backend folder with `uvicorn main:app --reload --port 8000` at localhost:8000, document every route in `output/harness.md`, and log this prompt under Problem 7.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 8 — Agent dashboard

1. Prompt typed: “Build the React Vite TypeScript dashboard in `frontend/` and connect it to the FastAPI backend at `http://localhost:8000`. Use a sophisticated pink bow and white pearl boutique design with blush pink, ivory, champagne, and rose gold, pearl accents, serif headings, rounded cards, satin ribbons, CSS Labubu-style bunny mascots, and responsive polish. Add sidebar navigation for tickets, agent team, approvals, cash, and activity; summary cards; all three live tickets with status and team-run buttons; per-agent activity with distinct pastel accents and icons; resolution summaries; human approval controls that update the checking balance; and empty states. Keep the data live from the backend, allow `http://localhost:5173` through CORS, run with `npm run dev`, create `output/design.md` explaining the visual and functional choices, and log this prompt under Problem 8.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 9 — Resolve the tickets

1. Prompt typed: “Reset `data/campus_customs_new.db` from the untouched original and record the starting checking balance. Use the real React dashboard and FastAPI backend to run the multi-agent team on tickets 101, 102, and 103 until they are resolved, using real MCP tools, Portkey `gpt-6-luna`, human approval only for payments or purchases, and no duplicate or negative cash changes. After each ticket, preserve the expected plan and fill its Actual section in `output/desk_tickets.html` with real agents, delegations, tools, and outcomes. Fill the Cash tab with the starting balance, every exact cash change and reason, the ending balance, and a reconciliation to the working database. Create `output/resolved_tickets.json` with real statuses, outcomes, contributions, and approvals; create `output/resolved_board.html` with local relative-path screenshots of the actual dashboard; append real activity to `output/audit_trail.json`; finish `output/harness.md` with the complete system; and flag any unresolved ticket honestly instead of inventing success.”

2. Follow-up prompts:
   1. “Investigate and fix unresolved Ticket 103. Inspect the actual ticket and inventory, pricing, vendors, invoices, payments, and cash_accounts. Determine whether an alternative vendor, smaller valid order, partial fulfillment, or another database-supported solution can resolve the explicit 20-unit hoodie request. If a valid solution exists, use existing MCP tools and agent workflows with human approval and no negative cash, invented money, vendor terms, or bypassed MCP. Otherwise keep it open and document the blocker in `resolved_tickets.json`, `desk_tickets.html`, and the reflection. Verify all ticket statuses and cash against payment records, update `audit_trail.json`, `harness.md`, and `AI_prompts.md`, preserve the dashboard and Git history, do not reset or duplicate payments, test and commit, and push if authenticated.”
   2. “Investigate why Problem 9 requires all three tickets resolved while Ticket 103 remains open. Read the complete available assignment instructions, original and working databases, ticket descriptions, shop rules, and current implementation. Verify whether 103 requires all 12 hoodies immediately, whether 101/102 require full immediate payment, whether vendor credit, payment terms, scheduling, or other authorized workflows exist, whether all cash/prices/quantities/invoices were interpreted correctly, and whether the agents unnecessarily restrict valid actions. Do not fabricate funds, alter the original database, bypass approval, falsely resolve tickets, change payment records, or reset without explanation. If no valid solution exists, provide a concise mathematical proof and identify the incompatible requirements. Record this prompt in `AI_prompts.md`, update the accurate Problem 9 artifacts, test, commit, and report statuses and cash.”
   3. “Fix the root cause of Ticket 103. The ticket is type `price_override` with subject Bulk hoodie discount; it asks Yale AI Club for a bulk discount on 20 navy medium hoodies. Review the complete instructions and Boss, Accounting, Inventory, and Customer Service agents. Treat price_override tickets as pricing decisions rather than automatic purchase orders. Inspect actual stock and pricing, determine a defensible recommendation without inventing a discount rate, record the need for human authorization, reset the working database as Problem 9 requires, rerun all three tickets, preserve approvals and cash guards, update all dashboard/report/audit/harness/reflection artifacts, test, commit, and explain the root cause and final balance. Do not falsely resolve a ticket without pricing authorization.”
   4. “Review the assignment rules and distinguish mandatory human approval for payments from approval requirements for pricing decisions. Do not invent a discount approval requirement. If Boss and Accounting are authorized to decide pricing, evaluate $58 list price, $22 unit cost, 20 requested units, and 8 in stock, make and record a defensible pricing decision through MCP, and resolve ticket 103 without cash movement. If approval is genuinely required, implement it. Update all Problem 9 artifacts, screenshots, audit trail, and prompt log based on actual execution, verify all three statuses and cash, and commit.”

3. Why I needed each follow-up:
   1. Ticket 103 was still open after the first run, so I needed to check whether an alternate vendor, partial order, or other real database path had been missed.

   2. The first investigation treated the request as a purchase and exposed a $104 contradiction, so I needed to verify the complete rules and implementation before accepting that blocker.

   3. The contradiction review showed the ticket type was `price_override`, so I needed to correct the workflow instead of treating a pricing request as an automatic replenishment.

   4. After correcting the workflow, I needed to distinguish payment approval from pricing authority and determine whether Boss could record a valid list-price decision without moving cash.

## Problem 10 — Reflection

1. Prompt typed: “Open `output/desk_tickets.html` and complete the Reflection tab with a detailed first-person reflection grounded in what actually happened on tickets 101, 102, and 103. Use the expected and actual sections, Cash tab, `resolved_tickets.json`, and `audit_trail.json` as evidence. Evaluate each agent’s performance, delegations, MCP tool calls, approvals, cash changes, outcomes, differences from the expected workflow, and whether those differences helped or hurt. Discuss which tasks could have been simpler with one agent and the tradeoffs in speed, complexity, and coordination. Propose three new problems the current agents and MCP tools can solve, and three problems the current system cannot solve, identifying the additional tools, data, or agents needed. Keep the existing ticket and Cash tabs unchanged, write naturally and critically, avoid unsupported claims, make the Reflection tab readable in a standalone HTML file, and log this prompt under Problem 10.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

## Problem 11 — Submit to GitHub

1. Prompt typed: “Prepare the entire HW5 project for final submission and push it to a public GitHub repository named `campus-customs-hw5` under `wennding5`. Audit the expected files and folders, include both database files and all MCP, backend, frontend, and output evidence, protect `.env` and API keys, keep `.mcp.json` portable and secret-free, update `README.md` with install/run/reset instructions, verify the original database is unchanged and the working copy and reports match the actual run, add `output/github_url.txt`, commit and push, verify public accessibility, and report the exact URL plus any missing requirements or issues. Do not reset the working database during the final check, do not claim unverified results, and log this prompt under Problem 11.”
2. Follow-up prompt: Not needed yet.
3. Nothing was lacking from the prompt given before.

### Problem 11 follow-up — Fix GitHub submission and ticket 103

1. Follow-up prompt typed: “Check why ticket 103 is still open by tracing the $104 cash shortfall through the real database payment records and audit logs. Determine whether the existing shop rules and agent workflows offer a legitimate resolution without invented money, negative cash, unpaid-vendor shipment, or bypassed human approval. If not, keep it open and document the blocker in `resolved_tickets.json`, `desk_tickets.html`, and the reflection. Verify tickets 101 and 102 and reconcile cash. Check GitHub authentication with `gh auth status`, guide authentication if necessary, create the public `wennding5/campus-customs-hw5` repository with `gh repo create` if absent, push the existing commit to `main`, verify the repository is public and contains all files, update `output/github_url.txt`, commit final changes, do not expose tokens or keys, and log this follow-up under Problem 11.”
2. What was missing from the first attempt: GitHub CLI authentication and repository creation/push were not available in the environment, so the commit and remote were prepared but public accessibility could not be verified. The first attempt also needed an explicit follow-up audit of ticket 103’s blocker and the authentication state.

### Problem 11 follow-up — Publish after Mac authentication

1. Follow-up prompt typed: “Now that GitHub authentication is complete on my Mac as `wennding5`, check whether Codex can access `gh` and the credentials. If accessible, create the public `wennding5/campus-customs-hw5` repository if needed and push all committed HW5 files, including the latest documentation updates, to `main`. Verify the repository is public and contains both databases and all required output files, confirm `output/github_url.txt`, do not change database or ticket results, and log this follow-up before pushing. If authentication is still unavailable, provide exact terminal commands to publish the existing local repository.”
2. What was lacking: Mac authentication is not available to this Codex shell; `gh auth status` reports the stored `wennding5` token is invalid here, so repository creation and push cannot be verified from this environment.

### Problem 11 follow-up — Finish publishing automatically

1. Follow-up prompt typed: “Use the authenticated Mac GitHub environment to finish publishing HW5 automatically without asking me to run commands. Check local CLI authentication, preserve all commits and files, create the public `wennding5/campus-customs-hw5` repository if absent, push the entire project to `main`, include both databases and all required backend, frontend, MCP, prompts, screenshots, and reports, exclude `.env` and secrets, do not reset or alter the working database or ticket results, keep 101/102 resolved and 103 open with its $104 blocker, update this prompt log before pushing, verify the remote is public and required files are visible, and report success only after actual push and verification. If this environment cannot access the Mac authenticated session, explain that limitation clearly.”
2. What was lacking: The prior authentication check showed the Codex environment’s `gh` credential is invalid; this follow-up requests one final host-level check and a clear limitation report instead of repeated credential retries.
