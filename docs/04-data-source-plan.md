# Data-Source Plan

## Source Categories

The source plan is split into factual sources and inspiration sources. Factual sources can block or rank destinations. Inspiration sources can suggest attractions, food, routes, and style, but should not be treated as verified facts without corroboration.

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
| QWeather | Forecasts, alerts, AQI | REST API | API key | plan-dependent | hours | Normalized facts | P0 candidate |
| Open-Meteo | Global forecast fallback | REST API | no key for basic use | policy-dependent | hours | Normalized facts | P0 candidate |
| Amap | China geocoding, POI, routing, traffic | REST API | API key | plan-dependent | live to daily | Normalized facts | P0 candidate |
| Google Maps Platform | International routing and POI | REST API | API key and billing | plan-dependent | live to daily | Normalized facts | P0 candidate |
| Trip.com Developers | Flights, hotels, trains, tours | Partner API | login/partner approval | partner-dependent | live to daily | Normalized facts plus links | P1 candidate |
| 12306 | Official China railway verification | official site/app only unless approved | user/session | not public API | live | verification notes | P1 with constraints |
| Zhihu | China Q&A and guide inspiration | official API/MCP/Skill if approved | account/API key | plan-dependent | recent search | Summaries plus references | P1 candidate |
| Xiaohongshu | China lifestyle and trip-note inspiration | official API only if content access exists; otherwise controlled OpenCLI/browser path if allowed | likely account/session | source-dependent | recent search | Summaries plus references | P1 candidate |
| Yelp | International food/local business | REST API | API key | plan-dependent | daily | Normalized POI summaries | P1 candidate |
| Tripadvisor | International attractions, hotels, restaurants | approved Content API | approval/API key | plan-dependent | daily | Normalized POI summaries | P1 candidate |
| Official sites | Closures, notices, advisories | search/API/browser | varies | varies | hours to days | Facts and citations | mandatory for detailed plans |

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
