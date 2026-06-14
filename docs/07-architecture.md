# Architecture

## Architectural Decision

Roamwise should be built as an agent-led, skill-first, tool-assisted research system.

The agent is a decision-making participant, not a wrapper around scripts. It owns research strategy, source selection, social/guide interpretation, tradeoff synthesis, and final recommendations. The skill owns workflow, research discipline, and report shape. Scripts and Python modules own deterministic work: source access, normalization, caching, filtering, scoring signals, and artifact generation.

Agent orchestration can call scripts, but scripts are support tools. They standardize repeatable actions and provide evidence/signals; they should not be treated as the full recommendation system.

## Repository Role

This repository should be understood as a skill package, not a traditional application.

- `skills/roamwise/SKILL.md` is the primary interface for agents.
- `docs/` records product decisions, source rules, architecture, and iteration constraints.
- `src/roamwise/` contains helper tools that agents may call for repeatable procedures.
- `examples/` contains request fixtures for tool testing and demonstrations.
- `tests/` keeps the helper tools stable.

The repository should avoid building an app-shaped core too early. Add code when a workflow has become stable enough that the agent benefits from a repeatable tool.

## System Shape

```text
User request
  -> Roamwise skill workflow
  -> agent research plan
  -> intake parser
  -> dynamic ranking profile
  -> seed candidate generator
  -> live source research and candidate expansion
  -> source adapters
  -> evidence store
  -> hard filters
  -> ranking signals
  -> agent synthesis
  -> recommendation report
  -> itinerary reference generator
  -> selected-destination detail planner
  -> final review
```

## Repository Layout

Target layout after the first implementation spike:

```text
skills/
  roamwise/
    SKILL.md
docs/
  00-product-brief.md
  09-skill-first-usage.md
examples/
  requests/
scripts/
  roamwise
src/
  roamwise/
    cli/
    agents/
    adapters/
      weather/
      maps/
      transport/
      content/
      official/
    core/
      models.py
      evidence.py
      ranking.py
      itinerary.py
      reports.py
    storage/
    evals/
tests/
  fixtures/
  golden/
data/
  raw/
  private/
  cache/
```

`data/raw`, `data/private`, and cache directories stay out of Git.

## Core Modules

### Skill Layer

Responsibilities:

- Define the human-readable workflow.
- Explain when to ask clarification questions.
- Route to scripts/tools.
- Require source freshness and citation checks.
- Enforce final report sections.
- Keep the agent in charge of research planning and synthesis.

Non-responsibilities:

- No hidden ranking math.
- No credentials.
- No source-specific scraping logic.
- No assumption that local seeds or numeric scores alone decide recommendations.

### CLI And Scripts Layer

Responsibilities:

- Provide commands the agent can call.
- Emit JSON or Markdown artifacts.
- Validate inputs and outputs.
- Support deterministic reruns.
- Standardize fixed procedures so the agent can reuse them reliably.
- Stay narrow: fetch, normalize, score, cache, or render.

Non-responsibilities:

- Do not decide the final destination.
- Do not replace social/guide interpretation.
- Do not hide source choice or confidence tradeoffs from the agent.

Example commands:

```text
roamwise intake parse
roamwise candidates generate
roamwise collect weather
roamwise collect routes
roamwise collect inspiration
roamwise rank
roamwise report recommendations
roamwise report itinerary
```

### Provider Adapter Layer

Every source implements a common adapter contract:

```text
capabilities() -> ProviderCapabilities
build_query(request, candidate, profile) -> ProviderQuery
fetch(query) -> RawProviderResult
normalize(raw) -> list[Evidence]
```

Adapter types:

- `api`: official REST/GraphQL SDK or direct HTTP.
- `mcp`: MCP server tool.
- `cli`: OpenCLI or provider-specific CLI.
- `browser`: Playwright automation.
- `search`: search API plus page fetch.
- `manual`: curated seed data.

### Evidence Layer

Evidence is the boundary between source access and reasoning.

Required fields:

- `source_name`
- `source_type`
- `access_method`
- `query`
- `url_or_reference`
- `collected_at`
- `valid_until`
- `fact_type`
- `fact_value`
- `confidence`
- `is_factual`
- `needs_corroboration`

### Ranking Layer

Ranking must support different priorities on every request. It produces decision-support signals for the agent rather than replacing agent judgment.

Pipeline:

1. Convert the user request into `RankingProfile`.
2. Apply hard filters before scoring.
3. Score each dimension independently.
4. Weight scores using the current profile.
5. Penalize missing, stale, or low-confidence evidence.
6. Explain the result with facts and tradeoffs.
7. Let the agent reconcile the score with source content, user intent, and qualitative findings.

The scoring layer should answer "what do the measurable signals say?" The agent should answer "what should we recommend, given all evidence and context?"

Example hard filters:

- no rain above a threshold.
- no self-driving required.
- public transit only.
- max door-to-door travel time.
- max budget.
- no high altitude.
- no visa uncertainty.
- accessible with stroller or older adults.

Example score dimensions:

- weather comfort.
- transport convenience.
- cost.
- food fit.
- attraction density.
- novelty.
- crowd risk.
- safety and disruption risk.
- evidence quality.

### Report Layer

Recommendation reports should include:

- ranked destinations.
- filtered-out destinations and reasons.
- tradeoffs.
- evidence freshness.
- source confidence.
- itinerary references for top destinations.
- what to verify before booking.

Detailed plans should include:

- daily schedule.
- route logistics.
- food and lodging-area suggestions.
- budget estimate.
- booking and ticket reminders.
- bad-weather fallback.
- no-drive fallback if relevant.
- official checks and caveats.

## Execution Modes

### Local MVP

- Skill plus CLI.
- Local SQLite cache.
- JSONL artifacts.
- Markdown report output.

### Agent-Assisted MVP

- Same scripts.
- Agent follows `skills/roamwise/SKILL.md`.
- Scripts provide evidence, candidates, route facts, weather facts, cacheable artifacts, and draft scoring signals.
- The agent performs source selection, live research, content analysis, recommendation synthesis, itinerary drafting, and final review.
- Optional OpenAI Agents SDK or LangGraph orchestrator after source adapters stabilize.

### Future Product Surface

Product surfaces are secondary. Add them only after the skill workflow and source-access playbooks are stable.

- FastAPI service for job submission.
- Local web app or Next.js UI for reports.
- Background queue for long-running research.
- MCP server exposing Roamwise tools to other agents.

## Error And Confidence Handling

Source failures should not crash the whole run unless they are required by a hard filter.

Failure behavior:

- Missing weather for a candidate: lower evidence quality; possibly exclude if weather is the top hard filter.
- Missing public transit: label self-drive dependency as unknown; ask user or lower rank.
- Social source unavailable: continue with official/search sources and mark inspiration gap.
- Conflicting facts: prefer official and newer sources, preserve conflict note.
- Local candidate seeds are only fallback starting points; if social/guide research suggests better destinations, the agent should add them and rerun relevant tools.

## Security Boundaries

- No secrets in Git.
- No cookies in logs.
- No raw private social content in committed fixtures.
- Browser automation is read-only for MVP.
- Booking and payment are out of scope.
- Source adapters must redact credentials from command lines and artifacts.
