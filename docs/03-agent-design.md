# Agent Design

## Working Principle

The agent should be evidence-first and decision-leading. It gathers fresh facts, records where they came from, explains uncertainty, and only then produces recommendations or itineraries.

The MVP is skill-driven. The skill describes how to run the workflow; scripts and provider tools do deterministic retrieval, normalization, caching, scoring assistance, and report generation. The LLM should decide what to research, select relevant sources, interpret social and guide content, synthesize tradeoffs, and explain the final recommendation. Code owns stable mechanics such as facts, schemas, filters, and repeatable scoring signals.

Scripts are not the product brain. They are reusable instruments that make fixed workflows reliable and convenient for the agent.

## Proposed Agent Roles

- Intake agent: turns user preferences into structured constraints.
- Candidate agent: generates possible destinations from geography, season, travel style, live source research, social/guide content, and seed lists.
- Weather agent: collects forecasts, alerts, historical comfort patterns, and uncertainty.
- Transport agent: checks travel time, transfer complexity, traffic, and availability.
- Content agent: collects itinerary inspiration and subjective signals from social, community, map, and official sources.
- Ranking agent: combines script-provided signals with agent research, scores destinations, and explains tradeoffs.
- Itinerary agent: drafts day-by-day plans for recommended destinations.
- Detail agent: expands the selected destination into a practical guide.
- Review agent: checks feasibility, missing citations, stale data, and risky assumptions.

These can start as functions in one process. Separate agents are a design boundary, not necessarily separate services.

## Core Data Objects

### TravelRequest

- origin
- date_range
- duration
- travelers
- budget
- travel_style
- hard_filters
- soft_preferences
- locale
- ranking_profile

### DestinationCandidate

- name
- region
- coordinates
- themes
- estimated_travel_time
- estimated_cost
- evidence

### Evidence

- source_name
- source_type
- url_or_reference
- collected_at
- freshness_window
- extracted_fact
- confidence
- notes

### DestinationScore

- hard_filter_status
- hard_filter_reasons
- weather_score
- transport_score
- cost_score
- preference_match_score
- crowding_score
- safety_or_risk_score
- evidence_quality_score
- total_score
- explanation

### RankingProfile

- hard_filters
- objective_weights
- risk_tolerance
- transport_modes
- weather_policy
- budget_policy
- food_policy
- crowd_policy
- accessibility_policy
- evidence_requirements

### Itinerary

- destination
- date_range
- days
- transport_plan
- lodging_area_suggestions
- food_suggestions
- fallback_options
- budget_estimate
- citations

## Recommended Runtime Shape

1. Normalize the user request.
2. Build a dynamic ranking profile from the user's current constraints.
3. Decide a research plan: destination sources, factual sources, social/guide sources, and stopping conditions.
4. Generate or load seed candidates, then expand or revise them through live research.
5. Run source collectors in batches with rate limits.
6. Normalize collected evidence.
7. Apply hard filters and compute scoring signals.
8. Let the agent synthesize script signals, social/guide findings, official facts, and user preferences.
9. Produce a recommendation report.
10. Generate itinerary references for top results.
11. Ask the user to choose one destination.
12. Expand into a detailed plan.
13. Run a final feasibility and citation review.

## Important Design Requirements

- Every external fact should carry source and collection time.
- The ranking layer should be deterministic enough to test, but it should provide decision support rather than replace agent judgment.
- LLM-written outputs should be generated from structured facts plus agent-reviewed source research, not raw browsing alone.
- The system should cache source lookups but mark cached data as stale when needed.
- Long-running research should be resumable.
- Failed sources should degrade the confidence score instead of crashing the whole recommendation.
- Local seed candidates are bootstrap defaults, not authoritative destination recommendations.

## Open Technical Questions

- Whether the first implementation should use OpenAI Agents SDK immediately or begin with a custom script orchestrator and add the SDK after provider adapters settle.
- Whether browsing and platform access happen through official APIs, browser automation, opencli, MCP tools, or provider-specific adapters.
- Whether storage starts with JSONL plus SQLite or also includes DuckDB for analysis.
- Whether destination search should use vector retrieval over collected notes.
