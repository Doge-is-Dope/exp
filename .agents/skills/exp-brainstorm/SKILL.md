---
name: exp-brainstorm
description: Explore MVP scope, architecture, or user flows, with an interactive HTML decision aid when useful or requested.
---

# exp brainstorm

Follow [AGENTS.md](../../../AGENTS.md) for workspace conventions and design principles. Use the brief and existing decisions to identify the choices that matter. Recommend an approach based on user outcomes and constraints; ask about consequential unresolved tradeoffs. When file changes are in scope, record decisions in the specification; otherwise present them in the response.

For architecture choices about a new substantive application or a responsibility or contract boundary, read [architecture decisions and verification](../exp-build/references/architecture.md). Distinguish current requirements, confirmed later changes, and runtime capacity goals; ask about unknowns only when they materially affect the approach. Other exploration does not require an architecture exercise.

Use a visual comparison when it helps the user decide. When interactive HTML is useful or requested, deliver a self-contained artifact inside the established project, such as `docs/brainstorm.html`; follow workspace creation rules if a new project is needed. Honor no-file requests. Exploration authorizes planning artifacts, not application implementation.

Choose views that clarify the actual decision: architecture boundaries, where data lives, user flows, or relevant failure and recovery paths. Connect important flows to SPEC acceptance criteria when defined. Let the task determine the layout and implementation. Keep controls keyboard-accessible and the content readable on narrow screens; exercise the delivered interactions when browser tools are available.

Distinguish proposed designs and simulations from working product behavior. An on-screen choice is exploratory until the user confirms it. Deliver a concise recommendation, important tradeoffs, and unresolved decisions. Plain text is sufficient when no visual artifact is useful or requested; include an HTML link only when an artifact was produced. Once implementation is requested, continue through `exp-build`.
