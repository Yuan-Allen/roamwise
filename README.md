# Roamwise

Roamwise is a skill-first travel research workflow for agents. The repository's primary artifact is the Roamwise skill: a reusable operating procedure that tells an agent how to research destinations, choose sources, compare evidence, recommend trips, and produce detailed travel advice.

The Python code in this repository is not the product surface. It is a supporting tool layer for fixed, repeatable procedures such as fetching weather, querying maps, normalizing source evidence, caching, and rendering reports. The agent remains the decision maker.

## Current Status

- Project initialized as a Git-managed workspace.
- MVP shape: skill-driven agent workflow with supporting scripts and tools.
- Geography: China domestic and international travel.
- Product scope, source research, architecture, agent design, iteration plan, and Git workflow are documented under `docs/`.
- Recommended initial stack: lightweight Python tool scripts, typed provider adapters, optional MCP/OpenCLI/browser adapters, and no heavy app framework unless a stable workflow needs it.
- First source-access spike: Open-Meteo weather recommendation CLI.

## Primary Usage

Use this repository as a skill package for an agent:

1. Load and follow [skills/roamwise/SKILL.md](skills/roamwise/SKILL.md).
2. Use [skills/roamwise/README.md](skills/roamwise/README.md) for package-level usage and tool assumptions.
3. Let the agent decide the research plan, source mix, candidate expansion strategy, and final synthesis.
4. Call scripts only when a stable procedure is useful, such as weather lookup, Amap routing, public web search, evidence normalization, or report rendering.
5. Treat script outputs as evidence and scoring signals, not final recommendations.

## Design Principle

Roamwise is agent-led. Scripts standardize fixed, repeatable work such as fetching weather, fetching routes, normalizing evidence, caching, and rendering reports. They are tools for the agent, not the whole decision system.

The agent remains responsible for deciding what to research, which sources to use, how to interpret social and guide content, when to ask follow-up questions, and how to synthesize destination recommendations and itineraries. Local seed candidates are only a bootstrap fallback; production recommendations should be informed by live research from sources such as Xiaohongshu, Zhihu, Trip.com, official tourism sites, maps, and other approved providers.

## Core Flow

1. Capture user constraints: origin city, date range, budget, travel style, group profile, hard exclusions, and risk tolerance.
2. Collect external signals: weather, traffic, transport availability, destination popularity, closures, events, social travel notes, and official information.
3. Score candidate destinations with evidence and freshness metadata.
4. Recommend a short list of destinations with tradeoffs.
5. Generate itinerary references for the recommended destinations.
6. After the user selects a destination, produce a detailed travel plan with daily schedule, logistics, fallback plans, costs, packing tips, and caveats.

## Tool Setup

Install dependencies:

```bash
uv sync
```

Optional environment variables:

- `AMAP_API_KEY`: enables Amap Web Service API tools.

Open-Meteo does not require a key.

## Tool Commands

These commands are agent tools. They are useful for repeatable evidence collection, but they should not replace live source research or agent synthesis.

Run the weather-only recommendation tool:

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

Inspect the content-research output contract:

```bash
uv run roamwise content seed examples/requests/auto_candidates_no_drive.json
```

This command uses local seed mentions only to standardize the structure that future Xiaohongshu, Zhihu, Trip.com, search, MCP, or OpenCLI adapters should return. It is not a production content source.

For live content research, use the agent's native web search, browser, MCP, or OpenCLI capabilities first. Repository scripts only keep the content evidence schema stable; they should not become the main search path.

Platform-specific Xiaohongshu, Zhihu, Ctrip, Trip.com, OpenCLI, MCP, or browser adapters should be added only with strict read-only limits, rate controls, and caching after the agent workflow is stable.

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
- [Skill-first usage](docs/09-skill-first-usage.md)
- [Content source playbooks](docs/10-content-source-playbooks.md)
- [Agent runbooks](docs/11-agent-runbooks.md)
- [Runbook examples](docs/12-runbook-examples.md)
- [Bootstrap ADR](docs/adr/0001-docs-first-bootstrap.md)

## Next Decision

Start with `skills/roamwise/SKILL.md` and `docs/09-skill-first-usage.md`. The next implementation work should improve source-access playbooks and adapters for content research while keeping the agent responsible for destination discovery, interpretation, and recommendations.
