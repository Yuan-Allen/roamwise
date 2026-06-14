# Skill-First Usage

Roamwise should be used as a skill package for an agent. The skill is the stable interface; scripts are supporting tools.

## Operating Model

1. The agent reads `skills/roamwise/SKILL.md`.
2. The agent turns the user request into constraints, hard filters, and ranking priorities.
3. The agent selects the closest runbook from `docs/11-agent-runbooks.md`.
4. The agent decides which factual and inspiration sources are needed.
5. The agent uses built-in web search, browser tools, MCP, OpenCLI, APIs, or repository scripts as appropriate.
6. Scripts return structured facts, evidence, draft scoring signals, or artifacts.
7. The agent interprets evidence, resolves conflicts, expands candidates, and writes recommendations.
8. After the user chooses a destination, the agent performs deeper targeted research and drafts a detailed plan.

## Boundary

The agent owns:

- destination discovery.
- source selection.
- candidate expansion.
- qualitative interpretation of social and guide content.
- tradeoff synthesis.
- final recommendation and itinerary writing.

The scripts own:

- stable source calls.
- normalization.
- schema validation.
- cacheable evidence collection.
- deterministic filtering and scoring signals.
- Markdown or JSON artifact generation.

## Source Strategy

Use factual sources for hard filters:

- weather.
- traffic and route feasibility.
- railway, flight, ferry, and public transport availability.
- official tourism notices.
- visa, entry, safety, and closure information.

Use inspiration sources for discovery and qualitative judgment:

- Xiaohongshu.
- Zhihu.
- Ctrip and Trip.com.
- Mafengwo and guide sites.
- public web search.
- local blogs, forums, and official destination pages.

Social and guide content should influence recommendations, but it should be labeled as inspiration unless corroborated by factual or official sources.

## Tool Selection

Prefer source access in this order when possible:

1. Official API, official site, or authorized data provider.
2. MCP or provider CLI with explicit supported operations.
3. Search API or built-in web search for public pages.
4. Browser automation for read-only inspection when no better interface exists.
5. Local seed data only as a fallback bootstrap.

Browser or logged-in platform access should be read-only, rate-limited, cached, and never used to post, like, comment, follow, book, or purchase.

## Script Design Rule

Add a script only when the workflow is repeatable enough that the agent benefits from a standard tool. A good script should answer one of these questions:

- What facts can we fetch reliably?
- What evidence can we normalize?
- Which hard filters are clearly violated?
- What scoring signals are useful for the agent?
- What artifact should be generated consistently?

A script should not answer: "where should the user go?" The agent answers that after reviewing evidence.
