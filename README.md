# Roamwise

Roamwise is a travel-planning agent project. The goal is to collect fresh signals such as weather, traffic, transportation options, destination content, and travel notes at scale, recommend suitable destinations, then generate increasingly detailed itineraries after the user chooses a destination.

This repository starts with a docs-first bootstrap because the product depends heavily on source access, freshness requirements, scoring rules, and agent workflow choices that should be explicit before implementation.

## Current Status

- Project initialized as a Git-managed workspace.
- Product scope, open questions, data-source plan, agent design, iteration plan, and Git workflow are documented under `docs/`.
- No application framework has been selected yet.

## Core Flow

1. Capture user constraints: origin city, date range, budget, travel style, group profile, hard exclusions, and risk tolerance.
2. Collect external signals: weather, traffic, transport availability, destination popularity, closures, events, social travel notes, and official information.
3. Score candidate destinations with evidence and freshness metadata.
4. Recommend a short list of destinations with tradeoffs.
5. Generate itinerary references for the recommended destinations.
6. After the user selects a destination, produce a detailed travel plan with daily schedule, logistics, fallback plans, costs, packing tips, and caveats.

## Key Documents

- [Product brief](docs/00-product-brief.md)
- [Clarification checklist](docs/01-clarification-checklist.md)
- [Iteration plan](docs/02-iteration-plan.md)
- [Agent design](docs/03-agent-design.md)
- [Data-source plan](docs/04-data-source-plan.md)
- [Git workflow](docs/05-git-workflow.md)
- [Bootstrap ADR](docs/adr/0001-docs-first-bootstrap.md)

## Next Decision

Start with `docs/01-clarification-checklist.md`. The first implementation iteration should begin only after the initial product surface, source access methods, and MVP recommendation criteria are clear enough to test.
