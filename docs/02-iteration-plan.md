# Iteration Plan

## Phase 0: Bootstrap

Status: initialized.

Deliverables:

- Git repository.
- Project brief.
- Clarification checklist.
- Data-source plan.
- Agent design sketch.
- Git workflow.

## Phase 1: Requirements Lock

Goal: turn the open checklist into concrete MVP decisions.

Deliverables:

- MVP user flow: skill-driven workflow with scripts and tools.
- Chosen geography and trip types: China domestic and international travel.
- Source access matrix.
- Dynamic ranking profile design.
- 5-10 representative travel requests for testing.

Suggested branch:

```text
docs/requirements-v1
```

Suggested commits:

```text
docs: define mvp travel-planning requirements
docs(data): record initial source access decisions
docs(architecture): define skill-first source adapter design
```

## Phase 2: Source Access Spike

Status: in progress.

Goal: prove that the system can fetch useful, fresh, attributable data.

Design note: source-access scripts provide tools and scoring signals for the agent. They should not replace agent-led research, source selection, qualitative analysis, or final recommendation synthesis.

Deliverables:

- Minimal provider interfaces.
- Weather lookup prototype, preferably QWeather plus Open-Meteo.
- Transport or traffic lookup prototype, preferably Amap for China.
- Destination-content lookup prototype, preferably Zhihu official API/MCP if credentials are available, otherwise a controlled search or OpenCLI adapter.
- Source freshness and citation schema.

Suggested branch:

```text
feat/source-access-spike
```

Recommended first thin slice:

1. Parse one Chinese trip request into a `TravelRequest`. Done for JSON input.
2. Generate 10-20 candidate destinations. Started with a local seed generator as a fallback only.
3. Fetch weather for all candidates. Done with Open-Meteo.
4. Fetch China route estimates for a subset through Amap. Done for geocode, driving, and transit route adapters.
5. Fetch one inspiration source for the top 3. Next priority because agent-led recommendation needs social/guide source analysis.
6. Score with a dynamic ranking profile. Done for weather hard filters and weights.
7. Produce a sourced markdown report. Done for weather-only and weather-plus-transit recommendations.

Recommended next branch:

```text
feat/content-research-spike
```

Recommended next thin slice:

1. Add a content research adapter interface. Done with `ContentResearchQuery`, `ContentMention`, and `ContentResearchResult`.
2. Document source-access playbooks for Xiaohongshu, Zhihu, Ctrip/Trip.com, public search, and official tourism sources.
3. Support one approved source path such as agent-native web search, Zhihu MCP/API, Xiaohongshu OpenCLI/browser path, or Trip.com guide search.
4. Return structured inspiration evidence: candidate mentions, themes, itinerary patterns, warnings, source references, and freshness.
5. Let the agent add or remove candidates based on that evidence.
6. Rerun weather and route tools for the updated candidate set.

Skill-first acceptance criteria:

- The agent can use the skill without treating any script as the final recommender.
- The content tool returns evidence that helps the agent reason, not opaque rankings.
- The local candidate generator remains a bootstrap/fallback path only.
- The docs say when to use agent-native web search, platform-specific access, MCP, OpenCLI, or browser automation.

## Phase 2.5: Skill Usage Hardening

Goal: make the repository easier to hand to an agent as a skill package.

Deliverables:

- Skill-first usage guide.
- Tool-use discipline rules in `skills/roamwise/SKILL.md`.
- Source-access decision tree for factual sources vs social/guide sources.
- Examples showing agent-led research plans and which scripts they call.
- Golden report examples where the agent revises candidates based on external content.

Suggested branch:

```text
docs/skill-first-usage
```

## Phase 3: Destination Ranking Prototype

Goal: rank candidate destinations using normalized signals.

Deliverables:

- Candidate destination model.
- Scoring rubric and weights.
- Evidence object model.
- Sample ranked output for golden test requests.
- Tests for obvious ranking behavior.

Suggested branch:

```text
feat/destination-ranking
```

## Phase 4: Itinerary Reference Prototype

Goal: generate useful trip outlines for top destinations.

Deliverables:

- Itinerary schema.
- Day-by-day itinerary generator.
- Route feasibility checks where data is available.
- Fallback plan generation for bad weather or transport disruption.
- Golden examples for itinerary quality.

Suggested branch:

```text
feat/itinerary-references
```

## Phase 5: Detailed Destination Advisor

Goal: after the user selects a destination, create a detailed travel guide.

Deliverables:

- Detailed plan generator.
- Budget estimate.
- Packing and risk checklist.
- Food, hotel-area, route, and attraction recommendations.
- Source-backed caveats and confidence notes.

Suggested branch:

```text
feat/detailed-trip-advisor
```

## Phase 6: Productization

Goal: make the prototype pleasant and repeatable.

Deliverables:

- Chosen UI or API surface.
- Job history and cached results.
- Structured logs and cost tracking.
- CI checks.
- Documentation for setup and operation.

Suggested branch:

```text
feat/product-surface
```
