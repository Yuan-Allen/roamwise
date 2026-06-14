# Roamwise Skill Package

Roamwise is a skill-first travel research workflow. Use it when a user asks for destination recommendations, trip feasibility research, itinerary references, or detailed travel advice.

The skill is the main interface. Repository code is a supporting tool library for repeatable evidence collection and report artifacts.

## What The Agent Owns

- Understanding the user's constraints and preferences.
- Building the runbook stack.
- Choosing source strategy.
- Discovering and revising candidate destinations.
- Interpreting social and guide content.
- Reconciling conflicts and uncertainty.
- Writing the final recommendation or detailed itinerary.

## What Tools Own

- Fetching weather and route facts.
- Normalizing source evidence.
- Running deterministic filters and scoring signals.
- Producing draft Markdown or JSON artifacts.
- Making stable source access repeatable.

Tools do not decide where the user should travel.

## Reading Order

Start with:

1. `SKILL.md`
2. `docs/09-skill-first-usage.md`
3. `docs/11-agent-runbooks.md`

Read when needed:

- `docs/12-runbook-examples.md` for complex or ambiguous examples.
- `docs/10-content-source-playbooks.md` before using social, guide, search, MCP, OpenCLI, or browser access.
- `README.md` for tool commands, setup, and environment variables.
- `docs/07-architecture.md` for deeper architecture boundaries.
- `docs/08-technology-stack.md` for tooling decisions.

## Default Execution

1. Parse the request into hard filters, feasibility constraints, preferences, and missing inputs.
2. Ask only for information that blocks safe progress.
3. Build a composable runbook stack.
4. Use discovery sources to find or revise candidate destinations when the candidate set is broad.
5. Use factual tools and official sources to verify hard filters.
6. Use social and guide sources to improve fit among feasible candidates.
7. Produce a recommendation report with citations, tradeoffs, confidence, and filtered-out destinations.
8. After the user selects a destination, run detailed destination planning.

## Tool Commands

Weather-only recommendation:

```bash
uv run roamwise recommend weather examples/requests/rain_first.json
```

Weather plus route feasibility:

```bash
uv run roamwise recommend destination examples/requests/no_drive.json
```

Content evidence contract:

```bash
uv run roamwise content seed examples/requests/auto_candidates_no_drive.json
```

Public search adapter:

```bash
uv run roamwise content search examples/requests/auto_candidates_no_drive.json
```

Amap diagnostics:

```bash
uv run roamwise amap geocode 西湖 --city 杭州
uv run roamwise amap driving 121.4737,31.2304 120.1551,30.2741
```

## Environment

- `AMAP_API_KEY`: enables Amap tools.
- `TAVILY_API_KEY`: enables the public search adapter.
- Open-Meteo weather access requires no key.

Do not commit secrets, cookies, raw private social content, or login artifacts.

## Safety And Scope

- Do not book, purchase, post, like, comment, follow, favorite, message, or modify user accounts.
- Treat Xiaohongshu, Zhihu, blogs, forums, and social posts as inspiration unless corroborated.
- Use official sources for closures, entry rules, safety, attraction status, and other hard facts.
- Preserve evidence freshness and uncertainty.
