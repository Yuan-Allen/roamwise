# Source Research

This document records the initial source research for a skill-driven travel-planning MVP that supports both China domestic and international trips.

## Source Strategy

Use three layers:

1. Fact layer: weather, AQI, routing, traffic, transport availability, official notices, attraction status, visa or safety advisories. These can block or strongly affect recommendations.
2. Context layer: POI databases, maps, hotels, prices, event calendars, holiday calendars, crowd proxies. These improve scoring and feasibility.
3. Inspiration layer: Xiaohongshu, Zhihu, forums, blogs, reviews, travel notes, and social posts. These are useful for itinerary ideas and subjective fit, but must be labeled as inspiration unless corroborated.

Preferred access order:

1. Official API.
2. Official MCP or officially published skill/tool.
3. Partner API or approved data feed.
4. Search API that links back to sources.
5. OpenCLI or browser automation with user-provided access and source-specific policy review.
6. Manual seed list for early testing.

## Priority Matrix

| Priority | Source | Region | Data | Recommended Access | Why It Matters | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | QWeather | China plus global | forecast, warnings, weather indices, AQI | REST API | Strong China fit; includes global forecast and alerts | API key and plan needed |
| P0 | Open-Meteo | global | forecast, historical forecast, air quality, geocoding | REST API | Easy global baseline and no-key startup path | Commercial usage and quota policy must be checked |
| P0 | Amap | China | geocoding, POI, routing, traffic, public transit | REST API | Best first choice for China maps and routing | Mainland-focused; API key needed |
| P0 | Google Maps Platform | international | routes, traffic, place search, reviews, photos | REST API | Strong global routing and POI baseline | Billing, regional terms, and coverage constraints |
| P0 | Official tourism and attraction sites | both | closures, notices, ticket rules, safety alerts | search/API/browser | Required for detailed plans | Heterogeneous parsing |
| P1 | Trip.com Developers | both | flights, hotels, trains, tours, car rentals | partner API | Broad travel-commerce data and China/international bridge | Login/partner access required |
| P1 | Amadeus | international | flight offers, prices, availability | REST API | Mature flight API for international coverage | Flight availability is commercial and must be verified |
| P1 | 12306 | China | train schedules, tickets, official railway notices | official site/app verification; avoid unofficial booking automation | Authoritative train source | No general public booking API found; 12306 says third-party ticketing is not authorized |
| P1 | Zhihu | China | Q&A, guides, recent discussion | official API/MCP/Skill if accessible | Good structured long-form China context | Need account, quota, and endpoint confirmation |
| P1 | Xiaohongshu | China | recent lifestyle/travel notes | official API if content access exists; otherwise approved OpenCLI/browser adapter | Very high-value domestic inspiration source | Current official docs found are mostly ecommerce/merchant APIs, not general travel-note search |
| P1 | Dianping/Meituan | China | food, local services, reviews | official/partner if available; fallback to Amap POI plus social mentions | Strong domestic food signal | Public general review API access is unclear |
| P1 | Google Places | international | places, ratings, reviews, photos | REST API | Strong global POI and food baseline | Cost and usage constraints |
| P1 | Yelp Fusion | international | restaurants and local businesses | REST API | Food and local-business search | Coverage varies outside North America and major cities |
| P1 | Tripadvisor Content API | international | hotels, attractions, restaurants, reviews, photos | approved Content API | Travel-specific global content | Requires approved access |
| P2 | Foursquare Places | international | POI and venue metadata | REST API | Alternative POI source | API terms and cost need validation |
| P2 | OpenTripMap | international | attractions and POI | REST API | Lightweight attraction seed source | Quality varies; needs corroboration |
| P2 | Reddit, blogs, forums, YouTube/TikTok/Instagram | international | social inspiration | search/API/browser if allowed | Useful for vibe and recent subjective reports | Treat as inspiration only |

## Data Categories To Support

### Weather And Environment

Signals:

- Rain probability and precipitation amount.
- Temperature and apparent temperature.
- Wind, typhoon, snow, extreme weather alerts.
- AQI and pollutant level.
- UV, heat/cold comfort, sunrise/sunset, tide for coastal trips.

Initial sources:

- QWeather for China-heavy forecast, alerts, weather indices, and AQI.
- Open-Meteo for global baseline and forecast fallback.
- Local official weather offices for high-risk detailed plans when needed.

### Routing, Traffic, And Mobility

Signals:

- Door-to-door travel time.
- Public transit feasibility.
- Self-drive vs no-drive feasibility.
- Transfer count and last-mile complexity.
- Live traffic, road closures, tolls, parking pressure.

Initial sources:

- Amap for China geocoding, POI, routing, traffic, and public transit.
- Google Maps Routes and Places internationally.
- HERE or TomTom as alternatives if Google coverage, billing, or terms are a problem.

### Long-Distance Transport

Signals:

- Flight/train feasibility.
- Travel duration and transfer count.
- Price range and schedule density.
- Ticket availability risk.

Initial sources:

- Trip.com Developers if partner access is available.
- Amadeus for international flights.
- 12306 official site/app for China train verification and user-facing links.

Policy:

- Do not build booking or payment in MVP.
- Do not claim live ticket availability without a supported source and timestamp.
- For 12306, treat official channels as the authority and avoid unofficial booking automation unless a later legal/access decision explicitly permits it.

### POI, Food, Hotels, And Local Quality

Signals:

- Attraction candidates and operating hours.
- Restaurant clusters, cuisine fit, local specialties.
- Hotel area suitability and commute time.
- Price level and reservation pressure.

Initial sources:

- Amap POI for China.
- Google Places internationally.
- Yelp for international food/local businesses.
- Tripadvisor for travel-specific attractions, hotels, and restaurants if approved.
- Dianping/Meituan if a valid access path is confirmed.

### Social And Guide Inspiration

Signals:

- Recent itinerary patterns.
- Seasonal recommendations.
- Common pitfalls.
- Photo-driven expectations.
- Crowd and popularity signals.
- Food and neighborhood suggestions.

Initial sources:

- Xiaohongshu for China domestic lifestyle/trip notes.
- Zhihu for Q&A, long-form guides, and decision tradeoffs.
- Mafengwo and Ctrip/Trip.com guides if available.
- Reddit, Tripadvisor forums, blogs, and search results internationally.

Policy:

- Social posts are inspiration, not facts.
- Store source URL/reference, platform, author/date when available, extraction time, and confidence.
- Avoid storing raw private content or login artifacts.

### Official Notices And Safety

Signals:

- Attraction closures.
- Weather warnings.
- Travel advisories.
- Visa or entry requirements.
- Local emergency or public health notices.

Initial sources:

- Official attraction/tourism sites.
- Government advisories for international travel.
- Weather alert providers.
- Official transport operators.

Policy:

- Detailed plans should include official-source checks for closures and safety when practical.
- If official verification is missing, lower confidence and say so.

## Access Methods

### Official API Adapter

Use for QWeather, Open-Meteo, Amap, Google Maps, Amadeus, Yelp, and similar sources.

Implementation shape:

- Typed client.
- Rate-limit policy.
- Retry policy.
- Source-specific cache TTL.
- Normalized `Evidence` output.
- Test fixtures with sanitized responses.

### MCP Adapter

Use when a provider exposes an official or trusted MCP server, such as a future Zhihu MCP path.

Implementation shape:

- MCP server config outside Git.
- Tool-call wrapper that emits normalized evidence.
- Tool capability snapshot recorded with each run.

### OpenCLI Adapter

Use when the user provides a CLI that can legally and reliably access a platform.

Implementation shape:

- Shell command wrapper with strict JSON output contract.
- Timeout and rate limit.
- No credentials in arguments or logs.
- Sanitized stderr capture.
- Platform-specific policy note.

### Browser Automation Adapter

Use only when API/MCP/CLI access is unavailable and the source policy allows it.

Implementation shape:

- Playwright-based collector.
- User-controlled authenticated profile if needed.
- Read-only research actions.
- No booking, purchasing, posting, liking, commenting, or automated account actions in MVP.
- Conservative throttling and clear source metadata.

### Search Adapter

Use for official-site discovery, fallback guide lookup, and international web coverage.

Implementation shape:

- Search result capture with URL/title/snippet/rank.
- Fetch only pages needed for evidence.
- Prefer official domains for factual constraints.

## Recommended First Source Spikes

### Spike A: Weather First

Goal: validate hard filters such as "no rain", "not too hot", and "air quality matters".

Sources:

- QWeather.
- Open-Meteo.

Output:

- Candidate weather table.
- Rain hard-filter decision.
- Weather comfort score with citations.

### Spike B: China No-Drive Feasibility

Goal: validate requests such as "I do not drive" and "public transit first".

Sources:

- Amap geocoding, route planning, public transit, traffic.

Output:

- Origin-to-destination travel time.
- Last-mile complexity.
- Self-drive dependency score.

### Spike C: Inspiration Source

Goal: validate itinerary material collection.

Sources:

- Zhihu official API/MCP if credentials are available.
- Xiaohongshu via approved OpenCLI/browser path if the user provides one.
- Search adapter fallback for official and public guide pages.

Output:

- Top themes.
- Recommended itinerary patterns.
- Common warnings.
- Source confidence labels.

## Source References

- [QWeather developer docs](https://dev.qweather.com/docs/)
- [Open-Meteo forecast API docs](https://open-meteo.com/en/docs)
- [Amap Web Service API summary](https://lbs.amap.com/api/webservice/summary)
- [Google Maps Routes API](https://developers.google.com/maps/documentation/routes)
- [Google Places API overview](https://developers.google.com/maps/documentation/places/web-service/overview)
- [Trip.com Developers](https://developers.trip.com/)
- [Amadeus Flight Offers Search](https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search)
- [12306 official channel announcement](https://www.12306.cn/mormhweb/zxdt/202412/t20241211_43192.html)
- [Zhihu developer platform](https://developer.zhihu.com/)
- [Xiaohongshu open platform application docs](https://xiaohongshu.apifox.cn/)
- [Xiaohongshu developer agreement](https://xiaohongshu.apifox.cn/doc-2811022)
- [Yelp business search API](https://docs.developer.yelp.com/reference/v3_business_search)
- [Tripadvisor Content API](https://developer-tripadvisor.com/content-api/)
