# Agent Design

## Working Principle

The agent should be evidence-first. It gathers fresh facts, records where they came from, explains uncertainty, and only then produces recommendations or itineraries.

## Proposed Agent Roles

- Intake agent: turns user preferences into structured constraints.
- Candidate agent: generates possible destinations from geography, season, travel style, and seed lists.
- Weather agent: collects forecasts, alerts, historical comfort patterns, and uncertainty.
- Transport agent: checks travel time, transfer complexity, traffic, and availability.
- Content agent: collects itinerary inspiration and subjective signals from social, community, map, and official sources.
- Ranking agent: scores destinations and explains tradeoffs.
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

- weather_score
- transport_score
- cost_score
- preference_match_score
- crowding_score
- safety_or_risk_score
- evidence_quality_score
- total_score
- explanation

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
2. Generate or load candidate destinations.
3. Run source collectors in batches with rate limits.
4. Normalize collected evidence.
5. Score destinations.
6. Produce a recommendation report.
7. Generate itinerary references for top results.
8. Ask the user to choose one destination.
9. Expand into a detailed plan.
10. Run a final feasibility and citation review.

## Important Design Requirements

- Every external fact should carry source and collection time.
- The ranking layer should be deterministic enough to test.
- LLM-written outputs should be generated from structured facts, not raw browsing alone.
- The system should cache source lookups but mark cached data as stale when needed.
- Long-running research should be resumable.
- Failed sources should degrade the confidence score instead of crashing the whole recommendation.

## Open Technical Questions

- Whether to use Python, TypeScript, or both.
- Whether to use an established agent framework or a small custom orchestrator.
- Whether browsing and platform access happen through official APIs, browser automation, opencli, MCP tools, or provider-specific adapters.
- Whether storage starts with JSON files, SQLite, or Postgres.
- Whether destination search should use vector retrieval over collected notes.
