---
name: roamwise
description: Skill workflow for researching travel destinations, collecting source evidence, ranking options, and drafting itinerary recommendations with Roamwise scripts.
---

# Roamwise Skill

Use this skill when a user asks for destination recommendations, trip feasibility research, itinerary references, or detailed travel advice.

## Principles

- Evidence first, narrative second.
- Separate factual sources from inspiration sources.
- Treat user-specific constraints as a dynamic ranking profile.
- Prefer official APIs and official notices for hard filters.
- Label stale, missing, conflicting, or social-only evidence.
- Do not book, purchase, post, like, comment, or modify user accounts in the MVP.

## Workflow

1. Parse the user's request into structured constraints.
2. Build a ranking profile with hard filters and weighted preferences.
3. Generate destination candidates.
4. Collect weather and environment facts.
5. Collect route, traffic, and transport facts.
6. Collect POI, food, hotel-area, guide, and social inspiration as needed.
7. Normalize every source result into evidence with source and freshness metadata.
8. Apply hard filters.
9. Rank destinations.
10. Produce a recommendation report with tradeoffs and citations.
11. Generate itinerary references for the top destinations.
12. After the user selects a destination, expand into a detailed plan.
13. Run a final feasibility, citation, and risk review.

## Clarification Rules

Ask before running a large research job when any of these are missing and cannot be safely defaulted:

- origin city.
- date range or rough travel window.
- trip length.
- destination region if the candidate space is too large.
- hard filters such as no rain, no driving, budget cap, passport/visa constraints, or mobility constraints.

Proceed with assumptions when the missing information only affects ranking style, and state the assumption in the report.

## Source Rules

- Weather, transport, traffic, closures, and entry requirements are factual.
- Xiaohongshu, Zhihu, blogs, forums, and social posts are inspiration unless corroborated.
- Do not use a source for booking availability unless the source supports that use.
- Cache source results with a freshness window.
- Preserve enough metadata to reproduce a recommendation.

## Expected Artifacts

- `TravelRequest`
- `RankingProfile`
- `DestinationCandidate`
- `Evidence`
- `DestinationScore`
- recommendation report
- itinerary reference
- detailed plan

## Report Shape

Recommendation reports should include:

- top destinations.
- filtered-out destinations and reasons.
- comparison table.
- weather and transport feasibility.
- social/guide themes.
- evidence freshness.
- confidence and caveats.
- next verification steps before booking.

Detailed plans should include:

- day-by-day schedule.
- routing and transfer notes.
- food and hotel-area suggestions.
- budget estimate.
- bad-weather fallback.
- no-drive fallback if relevant.
- official checks.
- source-backed caveats.
