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

- MVP user flow.
- Chosen geography and trip types.
- Source access matrix.
- Initial ranking rubric.
- 5-10 representative travel requests for testing.

Suggested branch:

```text
docs/requirements-v1
```

Suggested commits:

```text
docs: define mvp travel-planning requirements
docs(data): record initial source access decisions
```

## Phase 2: Source Access Spike

Goal: prove that the system can fetch useful, fresh, attributable data.

Deliverables:

- Minimal provider interfaces.
- Weather lookup prototype.
- Transport or traffic lookup prototype.
- Destination-content lookup prototype.
- Source freshness and citation schema.

Suggested branch:

```text
feat/source-access-spike
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
