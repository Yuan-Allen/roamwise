# Product Brief

## Vision

Build an agent-assisted travel planner that can search many candidate destinations, compare real-world travel conditions, explain recommendations with evidence, and then produce detailed plans once the user chooses a destination.

## Primary User Story

As a traveler, I want to tell the system my origin, time window, budget, preferences, and constraints, so it can recommend places that are practical and enjoyable right now, then help me build a detailed itinerary for the selected destination.

## Product Stages

1. Destination discovery: generate candidate destinations from user constraints and external references.
2. Situation lookup: query weather, traffic, transport, closures, crowding, events, and content sources.
3. Recommendation: rank destinations with reasons, risks, confidence, and source citations.
4. Itinerary reference: draft day-by-day options for top destinations.
5. Detailed plan: after selection, provide schedule, routes, meals, attractions, bookings, fallback plans, budget, packing, and alerts.

## MVP Boundary

The first MVP should answer:

- Where should I go from my origin during a given date range?
- Why are these destinations recommended or filtered out?
- What would a reasonable 2-5 day itinerary look like for each top destination?
- What detailed advice should I follow after selecting one destination?

The MVP can start as a CLI or script-driven prototype if that helps validate data access and ranking before building a full UI.

## Non-Goals For Now

- Automatic booking or payment.
- Guaranteeing official real-time transport availability without provider confirmation.
- Fully autonomous scraping of every social platform without access, compliance, and rate-limit decisions.
- Replacing the user's final judgment on safety, health, or legal travel restrictions.

## Quality Bar

- Recommendations must include evidence, source names, and freshness timestamps.
- The system must separate facts, inference, and subjective preference matching.
- It should show tradeoffs rather than pretending one destination is universally best.
- It must handle missing or contradictory data gracefully.
