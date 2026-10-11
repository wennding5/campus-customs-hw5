# Campus Customs agent dashboard design

## Layout

The dashboard uses a fixed branded sidebar on wide screens and a compact icon navigation bar on small screens. The main workroom starts with three live summary cards, then moves through ticket selection, agent activity, approvals, or cash depending on the selected navigation item. Ticket cards remain compact while the selected ticket gets a larger handoff panel with its team-run action.

## Palette and type

The palette pairs soft blush pink (`#fbe7ef`), ivory (`#fff9fb`), champagne (`#fff2da`), and rose-gold pink (`#b75b82`) with navy plum text for contrast. Playfair Display gives section headings a boutique serif voice; DM Sans keeps ticket metadata, forms, and tool names easy to scan. Delicate vertical blush stripes sit behind the ivory workspace, while thin pink borders and pearl-like rings keep cards light.

## Agent distinctions

Each agent has a pastel tint, an accent color, and a small icon in the roster and activity feed: Boss uses rose blush and a crown, Inventory uses mint and a flower, Accounting uses champagne and a currency mark, Facilities uses lavender and a house, and Customer Service uses petal pink and a heart. The labels come from live audit records; the colors and icons are stable visual keys so the activity feed remains understandable at a glance.

## Tickets, status, and cash

Ticket cards are populated from `GET /api/tickets`, so IDs, requesters, subjects, and open/resolved statuses are not hardcoded. Running a selected ticket calls `POST /api/tickets/{ticket_id}/run`, then refreshes the event trail. The activity view displays each recorded agent result, actions, stop reason, and MCP tool tag from `GET /api/events`. Cash comes from `GET /api/cash`; the approval form calls `POST /api/approvals`, so the displayed checking balance refreshes only after the backend's human-approval, duplicate, and non-negative-balance guards succeed.

## Creative details and usability

The large CSS-only pink bunny mascot wears a fluffy white-pink outfit and satin bow and sits with gift boxes, pearl dots, and a coffee cup in the sidebar. A smaller peeking mascot anchors the top-right corner. CSS shapes keep the character integrated with the boutique style without adding image requests or distracting from the work. Sleeping bunny text faces appear for empty activity and ticket states, making waiting states feel intentional. Button bows, lift-on-hover cards, focus rings, and smooth color transitions add polish while preserving keyboard-friendly native buttons and form controls.
