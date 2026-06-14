# Clarification Checklist

Use this checklist to decide what the project should do before implementation. The highest-priority questions are at the top.

## 1. Product Surface

- Decision: the MVP is skill-driven, assisted by scripts and tools.
- The first usable version should be runnable from the command line and from an agent skill workflow.
- A local web app or API service can come later after source access and ranking are validated.
- Is the primary language Chinese, English, or bilingual?
- Decision: domestic China and international travel are both in scope.
- What trip lengths should the MVP optimize for: day trips, weekends, 3-5 days, 1-2 weeks, or flexible?
- Should the system support solo travel, couples, families, older adults, children, pets, or business travel?

## 2. User Inputs

- Required inputs: origin city, date range, number of travelers, budget, travel style, hard exclusions.
- Optional inputs: passport or visa constraints, preferred transport, hotel level, food preferences, mobility constraints, weather tolerance, crowd tolerance, safety concerns.
- Should users be able to save reusable preference profiles?
- How should uncertain inputs be handled: ask follow-up questions, assume defaults, or provide multiple branches?

## 3. Recommendation Criteria

- Decision: ranking criteria must be dynamic per request. One request may prioritize no rain; another may require no self-driving; later requests may combine weather, public transit, budget, food, safety, and novelty.
- Should scoring be transparent with weights?
- Are there hard filters, such as no rain, no long transfers, no high altitude, no expensive flights, or no visa risk?
- Should the agent recommend "do not travel" when all options are poor?
- How many destinations should be returned: top 3, top 5, or grouped by theme?

## 4. Data Sources

- See `docs/06-source-research.md` for the first source matrix.
- Weather: likely QWeather plus Open-Meteo for MVP.
- Maps and routing: likely Amap for China, Google Maps or HERE/TomTom for international coverage.
- Long-distance transport: Trip.com and Amadeus are likely API candidates; 12306 should be treated as official verification, not a public third-party booking API.
- Destination content: social and guide sources should be separated from factual sources. Xiaohongshu and Zhihu are high-value China inspiration sources; Google Places, Tripadvisor, Yelp, Foursquare, OpenTripMap, and official tourism sites are stronger international candidates.
- Access methods should be explicit per source: official API first, MCP wrapper when available, agent-native web search for discovery, OpenCLI or browser automation only when allowed and needed, manual seed lists for bootstrap.
- What rate limits, login requirements, anti-scraping rules, and terms-of-service constraints apply?

## 5. Evidence And Trust

- Should every recommendation cite source URLs or only internal evidence summaries?
- How should the system score source reliability?
- Should social posts be treated as inspiration instead of verified facts?
- How should stale, conflicting, or low-confidence data be surfaced?
- Should the agent store raw pages, extracted summaries, or only normalized facts?

## 6. Agent Workflow

- Should the agent run one destination at a time or batch many destinations concurrently?
- How many candidate places should be researched per request?
- Should there be specialist agents for weather, transport, social content, ranking, itinerary, and final review?
- When should the user be asked for clarification instead of letting the agent continue?
- Should long-running research jobs resume from checkpoints?

## 7. Output Format

- Destination recommendation output: ranked table, narrative report, map, cards, or JSON API.
- Itinerary reference output: day-by-day plan, time blocks, route map, checklist, or exportable document.
- Detailed plan output: markdown, web view, PDF, spreadsheet, calendar, or map pins.
- Should the output include Chinese names, English names, addresses, map links, and booking links?

## 8. Technical Choices

- Recommended MVP stack: Python-first with `uv`, Pydantic models, Typer CLI, async provider adapters, SQLite/DuckDB for local evidence storage, and Playwright only for sources that need browser automation.
- Agent runtime should start thin. Use deterministic scripts and typed outputs first; add OpenAI Agents SDK or LangGraph after source adapters and ranking profiles are tested.
- Storage should start local and auditable: JSONL for raw evidence summaries, SQLite for normalized facts and cache metadata, DuckDB or Polars for analysis if needed.
- Observability should include structured logs, source audit trail, request IDs, prompt/version snapshots, and cost/latency tracking from the first implementation spike.

## 9. Privacy, Security, Compliance

- What user data is stored, and for how long?
- Where should API keys, login cookies, and session tokens live?
- Are user profiles and travel history sensitive data?
- Should outputs include warnings for weather alerts, high-risk activities, health, visa, or political restrictions?
- Which data sources are allowed or disallowed by policy?

## 10. Evaluation

- What are 5-10 representative test requests?
- How will a good recommendation be judged?
- Should the project maintain golden examples for ranking and itinerary quality?
- What failure modes are unacceptable: hallucinated routes, closed attractions, impossible transfers, missing citations, or unsafe advice?
- What benchmark should be met before building a richer UI?

## First Answers Needed From You

1. Which exact source-access spike should be implemented first: weather, China routing, international routing, social inspiration, train/flight, or food/POI?
2. Which API keys or tools are already available locally?
3. Should social platforms be allowed through browser automation/OpenCLI, or only through official APIs/MCP?
4. What are the first 5 representative travel requests for evaluation?
5. Is the first user-facing language Chinese-only or bilingual?
