# Agent Runbooks

Runbooks translate the Roamwise skill into concrete execution patterns. They are not scripts. They tell the agent how to decide, research, call tools, and synthesize.

Each runbook separates two phases:

- Discovery: find plausible destinations and themes.
- Verification: test those candidates against hard constraints and fresh facts.

## Runbook Selection

Choose the closest runbook based on the user's strongest constraint.

| User Request Pattern | Primary Runbook | Main Risk |
| --- | --- | --- |
| no rain, mild weather, avoid heat/cold, typhoon/snow concern | Weather-first | Weather can invalidate otherwise attractive destinations |
| no self-drive, public transit only, older adults, stroller, low walking burden | No-drive mobility | Destination may be attractive but locally impractical |
| food, photos, niche, lifestyle, recent popularity, weekend ideas | Inspiration-first domestic | Social content may be trendy but not feasible |
| international, visa, safety, flight complexity, language, border rules | International feasibility | Entry, safety, and transport constraints dominate |
| user already chose destination | Detailed destination advisor | Need depth, official checks, and fallback plans |

If multiple patterns apply, apply hard-filter runbooks first, then inspiration runbooks.

## Shared Output Contract

Every recommendation run should produce:

- assumptions and missing inputs.
- source plan.
- candidate discovery notes.
- verification results.
- top recommendations.
- filtered-out destinations and reasons.
- itinerary references for top candidates.
- evidence freshness and confidence.
- checks needed before booking.

## Runbook A: Weather-First Recommendation

Use when the user says weather is the main constraint, for example "不下雨最重要", "避暑", "不要太冷", "避开台风", or "想要晴天".

### Clarify

Ask only if missing and necessary:

- origin city.
- travel window.
- trip length.
- region scope if candidate space is too broad.
- whether rain is a hard exclusion or just a preference.

### Discovery

1. Start with candidate destinations from the user's region, prior preferences, or live content research.
2. Use public search, Xiaohongshu, Zhihu, or guide sources to discover seasonal destinations and common weather caveats.
3. Keep candidates broad enough to avoid local seed bias.

### Verification

1. Run weather tools for each candidate.
2. Apply hard filters for precipitation, heat, cold, wind, snow, typhoon, or AQI.
3. Use official weather alerts for high-risk trips.
4. Mark forecast horizon and uncertainty.

Relevant tools:

```bash
uv run roamwise recommend weather examples/requests/rain_first.json
```

### Synthesis

- Recommend destinations that pass weather constraints and still match the user's travel style.
- Explain rejected candidates clearly.
- Include backup destinations or bad-weather alternatives.

## Runbook B: No-Drive Mobility Recommendation

Use when the user cannot or does not want to drive, or when the group has mobility constraints.

### Clarify

- origin city.
- acceptable door-to-door travel time.
- walking tolerance.
- luggage, stroller, older adults, or accessibility needs.
- acceptable taxi usage.

### Discovery

1. Search for destinations known for city walks, dense POI clusters, rail access, subway coverage, or low-transfer routes.
2. Use Xiaohongshu and guide content for last-mile pain points.
3. Use Zhihu for destination comparison and "without driving" discussions.

### Verification

1. Run route and transit tools for candidate destinations.
2. Check long-distance arrival feasibility.
3. Check local transfer effort between likely hotel areas and POIs.
4. Penalize dispersed scenic areas, weak public transit, or forced chartered-car patterns.

Relevant tools:

```bash
uv run roamwise recommend destination examples/requests/no_drive.json
```

### Synthesis

- Recommend compact destinations with viable arrival and local movement.
- Explain whether taxi-only segments are acceptable.
- Include hotel-area suggestions that reduce transfers.

## Runbook C: Inspiration-First Domestic Recommendation

Use when the user asks for subjective fit: food, photos, niche places, recent trends, seasonal vibe, citywalk, weekend ideas, couples, family, or friends.

### Clarify

- travel dates or rough season.
- origin city.
- trip length.
- budget style.
- desired vibe and disliked experiences.

### Discovery

1. Start with live content research, not local scripts.
2. Use Xiaohongshu for recent domestic lifestyle signals.
3. Use Zhihu for tradeoffs and whether a destination is worth it.
4. Use Ctrip/Trip.com or guide pages for attractions, hotel areas, tickets, and practical context.
5. Extract candidate destinations, themes, POIs, foods, itinerary patterns, and pitfalls.

### Verification

1. Run weather checks for the candidate list.
2. Run route and no-drive checks if relevant.
3. Verify official attraction or transport constraints for top candidates.
4. Mark social-only claims as inspiration.

Relevant tools:

```bash
uv run roamwise content search examples/requests/auto_candidates_no_drive.json
uv run roamwise recommend destination examples/requests/auto_candidates_no_drive.json
```

### Synthesis

- Recommend destinations by matching vibe plus feasibility.
- Include social themes but do not overclaim them as facts.
- Explain what needs official verification before booking.

## Runbook D: International Feasibility Recommendation

Use for international trips or when passport, visa, entry, safety, flight, or local transport risks dominate.

### Clarify

- passport or residency constraints if relevant.
- visa status and tolerance for visa uncertainty.
- origin airport.
- travel dates and trip length.
- budget and flight-time tolerance.
- language, safety, or health constraints.

### Discovery

1. Use public search and official tourism/government sources first.
2. Use Trip.com, airline, rail, or travel-commerce sources for route and booking context.
3. Use guide/social sources only after entry and transport feasibility are plausible.

### Verification

1. Check official visa and entry requirements.
2. Check government advisories and safety notices.
3. Check flight or rail feasibility through supported providers.
4. Check weather and seasonal risks.
5. Verify official attraction constraints for top candidates.

### Synthesis

- Treat visa, safety, and transport as hard filters.
- Separate "possible", "requires verification", and "not recommended".
- Include pre-booking checks and timing risks.

## Runbook E: Detailed Destination Advisor

Use after the user selects a destination.

### Clarify

- exact dates.
- hotel preference or area if known.
- pace.
- must-see and must-avoid items.
- food restrictions.
- budget.
- mobility constraints.

### Research

1. Official checks: attraction status, tickets, opening hours, reservations, transport notices, safety.
2. Map checks: hotel area, route clusters, transfer time, last-mile complexity.
3. Content checks: food, neighborhood vibe, itinerary rhythm, crowding, pitfalls.
4. Weather checks: daily plan and fallback needs.

### Plan

Produce:

- day-by-day schedule.
- route notes.
- food and hotel-area suggestions.
- ticket and booking reminders.
- budget estimate.
- bad-weather fallback.
- no-drive fallback if relevant.
- confidence and caveats.

## Quality Bar

Before finalizing, the agent must check:

- Did discovery include sources beyond local seeds when the candidate space was broad?
- Did verification test all hard filters?
- Are social claims labeled as inspiration?
- Are official/factual claims cited or clearly marked as needing verification?
- Are filtered-out destinations explained?
- Are next checks before booking concrete?
