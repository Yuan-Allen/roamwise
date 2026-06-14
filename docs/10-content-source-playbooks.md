# Content Source Playbooks

This document defines how an agent should use content sources for destination discovery, itinerary inspiration, and qualitative travel judgment.

The goal is not to make scripts replace research. The goal is to give the agent a clear source-selection policy and stable evidence shape.

## Access Policy

Use this priority order:

1. Official API, official website, or authorized partner feed.
2. MCP or provider CLI with explicit supported operations.
3. Built-in web search or search API against public pages.
4. Read-only browser automation with user-approved account/session.
5. Local seed data only as a bootstrap fallback.

Do not use undocumented private app APIs, reverse-engineered mobile endpoints, or automated account actions.

For social and guide platforms, the default mode is:

- read-only.
- low volume.
- cached.
- source-attributed.
- summarized, not raw-content hoarding.
- never post, like, comment, follow, favorite, message, book, or purchase.

## Evidence Types

Content sources should produce inspiration evidence unless they are official or directly factual.

Useful fields:

- platform.
- query.
- destination.
- title.
- url or stable reference.
- author or publisher when visible.
- published date when visible.
- collected at.
- themes.
- mentioned POIs.
- mentioned foods.
- itinerary pattern.
- warnings or pitfalls.
- confidence.
- why it matters for the current request.

## Agent Research Flow

For destination recommendation:

1. Start from user constraints and hard filters.
2. Use live content research when the candidate set is broad or inspiration-driven.
3. Extract candidate destinations, travel themes, pitfalls, and itinerary patterns.
4. Add or remove candidates based on evidence.
5. Run factual tools for weather, route, traffic, and official constraints.
6. Synthesize the recommendation with clear separation between facts and inspiration.

For detailed planning after a destination is selected:

1. Search official sources for closures, tickets, opening hours, transport notices, weather alerts, and safety issues.
2. Search guide/social sources for itinerary rhythm, food, neighborhoods, hidden costs, crowding, and pitfalls.
3. Verify critical claims against official or map sources.
4. Produce the plan with citations, confidence, and fallback options.

## Platform Playbooks

### Xiaohongshu

Recommended role:

- Domestic China inspiration.
- Seasonal impressions.
- Food, photo spots, neighborhood vibe, hotel-area sentiment, crowd comments, recent pitfalls.
- Candidate expansion for lifestyle-driven requests.

Not recommended for:

- final factual claims.
- booking availability.
- official opening hours.
- weather, safety, visa, or transport truth.

Access strategy:

1. Use an official content/search API only if a legitimate permission is confirmed.
2. Use public web search for indexed notes and destination discussions.
3. Use user-approved OpenCLI or browser automation only for low-volume, read-only research.

Risk controls:

- `read_only: true`
- `concurrency: 1`
- `max_queries_per_run: 5`
- `max_items_per_query: 10`
- `min_delay_seconds: 8`
- `cache_ttl_hours: 24`
- no login credential logging.
- no comment/user-profile scraping by default.
- no posting, liking, favoriting, following, messaging, or account changes.

Agent usage:

- Use Xiaohongshu when the user asks for "最近", "好拍", "好吃", "避坑", "小众", "亲子", "情侣", "citywalk", "周末", or lifestyle fit.
- Summarize themes across multiple notes.
- Mark evidence as `inspiration`.
- Corroborate operational facts through official sites, maps, Amap, or Trip.com/Ctrip.

Adapter recommendation:

- P1 as a skill playbook.
- P2 as a controlled browser/OpenCLI adapter after manual workflow is stable.
- Do not build a bulk scraper.

### Zhihu

Recommended role:

- Long-form reasoning.
- Destination comparisons.
- "Is X worth visiting?" style tradeoffs.
- Budget, route, and season discussions.
- Warnings from experienced travelers.

Not recommended for:

- live availability.
- official policy.
- high-freshness disruption checks.

Access strategy:

1. Use an official API/MCP path if the user provides one and permissions are clear.
2. Use built-in web search or search API for public Q&A pages.
3. Use browser read-only inspection only when public search snippets are insufficient.

Risk controls:

- prefer question/answer pages over user-profile exploration.
- summarize rather than store raw answers.
- preserve answer date when visible.
- treat older answers as stale unless the topic is stable.

Agent usage:

- Use Zhihu for strategic comparisons and decision support.
- Extract arguments for and against each destination.
- Use it to identify missing constraints the user should clarify.
- Cross-check practical details through official, map, weather, and transport sources.

Adapter recommendation:

- P1 search adapter first.
- P2 MCP/OpenCLI adapter if a compliant source becomes available.

### Ctrip And Trip.com

Recommended role:

- Travel-commerce context.
- Hotels, flights, trains, tours, attraction tickets, car rentals, and booking links.
- Destination guide pages and attraction listings.
- Price/availability hints when supported by an official or partner path.

Not recommended for:

- unsourced social sentiment.
- final claim of live availability unless the access method supports it and the timestamp is recorded.

Access strategy:

1. Use Trip.com Developers or Ctrip partner/alliance access when approved.
2. Use public guide/search pages for inspiration and references.
3. Use browser read-only inspection for user-facing guide pages only when necessary.

Risk controls:

- no booking or payment.
- no automated cart, reservation, or order actions.
- record whether data is from partner API, public page, or search result.
- record collection timestamp for prices or availability hints.

Agent usage:

- Use Ctrip/Trip.com for practical feasibility, booking-link references, attraction/ticket context, and hotel-area clues.
- Verify critical operating status with official attraction or transport sources.
- Treat prices and availability as hints unless sourced from a supported live endpoint.

Adapter recommendation:

- P1 official/partner adapter if credentials are available.
- P1 public guide search adapter for inspiration.
- P2 browser read-only adapter for guide pages.

### Public Search

Recommended role:

- Fallback discovery.
- Official-source discovery.
- Cross-platform references.
- International coverage.
- Low-risk first pass before platform-specific adapters.

Access strategy:

1. Use the agent's built-in web search when available.
2. Use Tavily or another search API when this repository needs repeatable runtime search.
3. Fetch only the pages needed for evidence.

Risk controls:

- prefer official domains for factual constraints.
- deduplicate near-identical pages.
- do not let search rank decide recommendations.
- record result rank and query.

Agent usage:

- Use public search early when source coverage is uncertain.
- Use it to discover official tourism pages, recent notices, guide articles, and forum discussions.
- Use platform-specific tools only when the value justifies added access risk.

Adapter recommendation:

- P0 as the first live content adapter because it has low account and platform risk.

### Official Tourism And Attraction Sources

Recommended role:

- Closures.
- Opening hours.
- ticket rules.
- reservation requirements.
- safety notices.
- seasonal advisories.

Access strategy:

1. Official website or official social account page.
2. Government tourism pages.
3. Attraction operator pages.
4. Public search for discovery, then direct official page verification.

Agent usage:

- Mandatory for detailed plans when practical.
- Mandatory when the recommendation depends on a specific attraction, trail, ferry, scenic area, or border/visa rule.
- Prefer official evidence over social content when they conflict.

Adapter recommendation:

- P0 for detailed destination advisor.
- Start with search plus page summary before building source-specific scrapers.

## First Implementation Recommendation

Keep the first content implementation broad and low-risk:

1. Strengthen the public search content adapter.
2. Add a platform field and source playbook tags to content evidence.
3. Add example research plans that show how the agent uses Xiaohongshu, Zhihu, Ctrip/Trip.com, and official sources.
4. Only then add platform-specific OpenCLI or browser adapters.

This order keeps the skill usable by agents immediately and avoids over-investing in brittle platform automation.
