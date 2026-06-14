# Roamwise Agent Instructions

This repository is a skill-first travel research workspace. It is not a traditional application where the main behavior lives in code.

## Required Entry Point

When a user asks for destination recommendations, trip feasibility research, itinerary references, or detailed travel advice in this repository, first read and follow:

1. `skills/roamwise/SKILL.md`
2. `skills/roamwise/README.md`

Read additional references only when needed:

- `docs/09-skill-first-usage.md` for the operating model.
- `docs/10-content-source-playbooks.md` for Xiaohongshu, Zhihu, Ctrip/Trip.com, public web, official sources, MCP, OpenCLI, or browser access.
- `docs/11-agent-runbooks.md` for runbook composition.
- `docs/12-runbook-examples.md` for complex request examples.

## Core Operating Rule

The agent is the decision lead. Scripts are supporting tools.

For travel recommendation tasks:

1. Parse user constraints and preferences.
2. Build a runbook stack.
3. Use agent-native web search, browser, MCP, OpenCLI, or other available native capabilities for open-ended destination discovery.
4. Use repository Python tools only for repeatable evidence, weather checks, route checks, schema examples, or report artifacts.
5. Synthesize recommendations independently; do not treat script output, local seed data, or numeric scores as the final recommendation.

## Tool Boundaries

Available helper commands include:

```bash
uv run roamwise recommend weather ...
uv run roamwise recommend destination ...
uv run roamwise content seed ...
uv run roamwise amap geocode ...
uv run roamwise amap driving ...
```

Do not call `uv run roamwise content search`; this repository intentionally removed that path. Live content discovery should be done by agent-native search, browser, MCP, or OpenCLI capabilities unless a future approved adapter is added.

Local content seed data is only a schema example and bootstrap fallback. It is not a production content source.

## Evidence Rules

- Treat Xiaohongshu, Zhihu, blogs, forums, and social posts as inspiration unless corroborated.
- Use official, weather, route, transport, visa, safety, and attraction sources for hard facts.
- Label stale, missing, conflicting, or social-only evidence.
- Do not book, purchase, post, like, comment, follow, favorite, message, or modify user accounts.

## Validation

For code or tool changes, run:

```bash
UV_CACHE_DIR=.uv-cache uv run ruff check .
UV_CACHE_DIR=.uv-cache uv run pytest
```
