# Roamwise

Roamwise is a travel-planning agent project. The goal is to collect fresh signals such as weather, traffic, transportation options, destination content, and travel notes at scale, recommend suitable destinations, then generate increasingly detailed itineraries after the user chooses a destination.

This repository starts with a docs-first bootstrap because the product depends heavily on source access, freshness requirements, scoring rules, and agent workflow choices that should be explicit before implementation.

## Current Status

- Project initialized as a Git-managed workspace.
- MVP shape: skill-driven workflow with scripts and tools.
- Geography: China domestic and international travel.
- Product scope, source research, architecture, agent design, iteration plan, and Git workflow are documented under `docs/`.
- Recommended initial stack: Python-first, typed provider adapters, CLI scripts, optional MCP surfaces, and an agent runtime added after the source-access spike.
- First source-access spike: Open-Meteo weather recommendation CLI.

## Core Flow

1. Capture user constraints: origin city, date range, budget, travel style, group profile, hard exclusions, and risk tolerance.
2. Collect external signals: weather, traffic, transport availability, destination popularity, closures, events, social travel notes, and official information.
3. Score candidate destinations with evidence and freshness metadata.
4. Recommend a short list of destinations with tradeoffs.
5. Generate itinerary references for the recommended destinations.
6. After the user selects a destination, produce a detailed travel plan with daily schedule, logistics, fallback plans, costs, packing tips, and caveats.

## Quick Start

Install dependencies:

```bash
uv sync
```

Run the first weather-only recommendation spike:

```bash
uv run roamwise recommend weather examples/requests/rain_first.json \
  --output artifacts/rain-first-weather.md
```

This command reads a structured travel request, fetches Open-Meteo forecasts for the candidate destinations, applies the request's weather hard filters, ranks the candidates, and renders a Markdown report.

Run the combined destination recommendation spike:

```bash
uv run roamwise recommend destination examples/requests/no_drive.json \
  --output artifacts/no-drive-destination.md
```

This command combines Open-Meteo weather data with Amap transit route feasibility for a no-self-drive request.

Run the same flow with generated candidate destinations:

```bash
uv run roamwise recommend destination examples/requests/auto_candidates_no_drive.json \
  --output artifacts/auto-candidates-no-drive.md
```

Inspect Amap Web Service API access after setting `AMAP_API_KEY`:

```bash
uv run roamwise amap geocode 西湖 --city 杭州
uv run roamwise amap driving 121.4737,31.2304 120.1551,30.2741
```

These commands are diagnostic entry points for the route-planning spike. The normalized Amap route data will be merged into destination recommendations in the next iteration.

## Key Documents

- [Product brief](docs/00-product-brief.md)
- [Clarification checklist](docs/01-clarification-checklist.md)
- [Iteration plan](docs/02-iteration-plan.md)
- [Agent design](docs/03-agent-design.md)
- [Data-source plan](docs/04-data-source-plan.md)
- [Git workflow](docs/05-git-workflow.md)
- [Source research](docs/06-source-research.md)
- [Architecture](docs/07-architecture.md)
- [Technology stack](docs/08-technology-stack.md)
- [Bootstrap ADR](docs/adr/0001-docs-first-bootstrap.md)

## Next Decision

Start with `docs/06-source-research.md` and pick the first source-access spike. The recommended first spike is weather plus China routing plus one inspiration source, because this validates factual freshness, hard filters, and subjective travel content in one thin slice.
