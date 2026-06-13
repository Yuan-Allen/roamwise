# Clarification Checklist

Use this checklist to decide what the project should do before implementation. The highest-priority questions are at the top.

## 1. Product Surface

- Should the first usable version be a CLI, local web app, API service, chat bot, or scheduled report?
- Is the primary language Chinese, English, or bilingual?
- Should it focus on domestic China travel first, international travel first, or both?
- What trip lengths should the MVP optimize for: day trips, weekends, 3-5 days, 1-2 weeks, or flexible?
- Should the system support solo travel, couples, families, older adults, children, pets, or business travel?

## 2. User Inputs

- Required inputs: origin city, date range, number of travelers, budget, travel style, hard exclusions.
- Optional inputs: passport or visa constraints, preferred transport, hotel level, food preferences, mobility constraints, weather tolerance, crowd tolerance, safety concerns.
- Should users be able to save reusable preference profiles?
- How should uncertain inputs be handled: ask follow-up questions, assume defaults, or provide multiple branches?

## 3. Recommendation Criteria

- What matters most: weather comfort, transport convenience, cost, novelty, scenery, food, crowding, safety, or popularity?
- Should scoring be transparent with weights?
- Are there hard filters, such as no rain, no long transfers, no high altitude, no expensive flights, or no visa risk?
- Should the agent recommend "do not travel" when all options are poor?
- How many destinations should be returned: top 3, top 5, or grouped by theme?

## 4. Data Sources

- Weather: which provider should be used, and how fresh must forecasts be?
- Traffic and local mobility: which source can provide congestion, road closures, public transit, and driving estimates?
- Long-distance transport: should it query flights, trains, buses, ferries, car rental, or ride hailing?
- Destination content: which platforms should be used for inspiration and itinerary references, such as Xiaohongshu, Zhihu, Mafengwo, Trip.com, official tourism sites, blogs, or maps?
- How will each source be accessed: official API, browser automation, opencli, private tool, exported data, search engine, or manual seed list?
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

- Preferred language and framework: Python, TypeScript, or mixed.
- Agent runtime: custom tool-calling loop, OpenAI Agents SDK, LangGraph, CrewAI, AutoGen, or other.
- Storage: local files, SQLite, Postgres, vector database, object storage, or cache only.
- Queue and scheduling: none for MVP, local worker, Celery, BullMQ, Temporal, or cron.
- Observability: logs, traces, source audit trail, prompt/version snapshots, cost tracking.

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

1. MVP surface: CLI, local web app, API, or chat-style tool?
2. Initial geography: China domestic only, international only, or both?
3. Initial data sources and access methods, especially for Xiaohongshu, Zhihu, maps, weather, and transport.
4. Ranking priorities and hard filters.
5. Preferred implementation stack.
