# Data-Source Plan

## Source Categories

### Weather

Purpose:

- Forecasts for trip dates.
- Severe weather alerts.
- Temperature, rain, wind, air quality, comfort level.

Decisions needed:

- Provider.
- Forecast horizon.
- API key and quota.
- Historical weather support.
- Required freshness.

### Traffic And Local Mobility

Purpose:

- Driving time.
- Congestion.
- Road closures.
- Public transit feasibility.
- Local transfer effort.

Decisions needed:

- Map provider.
- Domestic and international coverage.
- Whether to support live traffic in MVP.
- Whether route results can be cached.

### Long-Distance Transport

Purpose:

- Flight, train, bus, ferry, or driving feasibility.
- Travel time and transfer complexity.
- Rough price ranges.

Decisions needed:

- Supported transport modes.
- Data provider or access method.
- Whether booking links are required.
- How to avoid hallucinating availability.

### Destination Inspiration And Guides

Purpose:

- Candidate generation.
- Popular attractions.
- Itinerary patterns.
- Food and lodging-area ideas.
- Subjective travel quality signals.

Candidate sources:

- Xiaohongshu.
- Zhihu.
- Mafengwo.
- Trip.com or Ctrip.
- Dianping or map POI reviews.
- Official tourism and attraction websites.
- Search engine results.
- Curated seed lists.

Decisions needed:

- Which sources are allowed for MVP.
- How each source is accessed.
- Whether login is required.
- How to handle rate limits and platform terms.
- How to distinguish inspiration from verified facts.

### Official And Safety Sources

Purpose:

- Attraction closures.
- Park notices.
- Local government advisories.
- Visa or entry requirements.
- Weather warnings and emergency notices.

Decisions needed:

- Which official sources are mandatory for detailed plans.
- Whether advisories are domestic, international, or both.
- How warnings are shown to the user.

## Access Matrix Template

| Source | Use | Access method | Auth needed | Rate limit | Freshness | Storage | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Weather provider | Forecast and alerts | TBD | TBD | TBD | TBD | Normalized facts | undecided |
| Map provider | Routes and traffic | TBD | TBD | TBD | TBD | Normalized facts | undecided |
| Xiaohongshu | Inspiration and recent notes | TBD | TBD | TBD | TBD | Summary plus references | undecided |
| Zhihu | Q&A and longer guides | TBD | TBD | TBD | TBD | Summary plus references | undecided |
| Official sites | Closures and notices | TBD | TBD | TBD | TBD | Facts and citations | undecided |

## Normalized Evidence Fields

- source_name
- source_type
- query
- url_or_reference
- raw_collected_at
- normalized_at
- fact_type
- fact_value
- confidence
- freshness_window
- license_or_usage_note

## Source Policy

- Prefer official APIs and official notices for factual constraints.
- Treat social platforms as subjective inspiration unless corroborated.
- Keep raw credentials and cookies out of Git.
- Record enough metadata to reproduce a recommendation.
- If a source cannot be accessed reliably, the product should show reduced confidence instead of hiding the gap.
