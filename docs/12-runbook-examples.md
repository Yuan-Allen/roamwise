# Runbook Examples

These examples show how an agent should apply the Roamwise skill. They are execution references, not fixed scripts.

Each example includes:

- user request.
- constraint breakdown.
- runbook stack.
- discovery plan.
- verification plan.
- tool plan.
- recommendation report shape.

## Example 1: Composite Domestic Request

User request:

```text
6月底从上海出发，3-5天，不想下雨，不自驾，想吃得好，最好小众一点。
```

Constraint breakdown:

- origin: Shanghai.
- travel window: late June.
- trip length: 3-5 days.
- hard filters: avoid rain, no self-driving.
- preferences: good food, less obvious destination, domestic likely unless user says otherwise.
- missing inputs: budget, acceptable train/flight time, walking tolerance.

Runbook stack:

```text
primary_runbook: Weather-first
secondary_runbooks:
  - No-drive mobility
  - Inspiration-first domestic
hard_filter_runbooks:
  - Weather-first
  - No-drive mobility
preference_runbooks:
  - Inspiration-first domestic
post_selection_runbook:
  - Detailed destination advisor, after user chooses one destination
```

Discovery plan:

1. Use Xiaohongshu/public search for "上海出发 3天 不自驾 美食 小众 6月".
2. Use Zhihu for "上海出发 不自驾 小众 城市 美食 值得去".
3. Use Ctrip/Trip.com or guide pages for attraction clusters and hotel-area context.
4. Build a candidate list from content evidence, not only local seeds.
5. Preserve themes such as food, citywalk, crowd risk, rain season, and last-mile pain points.

Verification plan:

1. Run weather checks for candidate destinations.
2. Run route/transit checks from Shanghai and within the destination when tooling supports it.
3. Remove destinations with high rain risk if "不下雨" is hard.
4. Remove destinations that require self-driving or dispersed scenic-area transfers unless the user accepts taxis or chartered cars.
5. Verify official notices for top attractions only after the shortlist is stable.

Tool plan:

```bash
uv run roamwise recommend destination examples/requests/auto_candidates_no_drive.json
```

Use agent-native web search, browser, MCP, or OpenCLI capabilities for Xiaohongshu, Zhihu, Ctrip/Trip.com, guide, and official-source discovery.

Recommendation report shape:

- selected runbook stack.
- assumptions and questions not blocking the first pass.
- candidate discovery notes from content sources.
- weather pass/fail table.
- no-drive feasibility table.
- top 3 recommendations with food and niche-fit rationale.
- filtered-out destinations with reasons.
- itinerary reference for each top candidate.
- pre-booking checks.

## Example 2: Domestic Inspiration-First Weekend

User request:

```text
周末从北京出发，想找一个好吃、好拍、不要太累的地方，最好最近比较有意思。
```

Constraint breakdown:

- origin: Beijing.
- travel window: weekend.
- trip length: likely 2 days.
- hard filters: low fatigue, short travel time.
- preferences: food, photogenic places, recent interest.
- missing inputs: exact weekend, budget, high-speed rail vs flight tolerance.

Runbook stack:

```text
primary_runbook: Inspiration-first domestic
secondary_runbooks:
  - No-drive mobility
hard_filter_runbooks:
  - No-drive mobility, if low fatigue implies compact movement
preference_runbooks:
  - Inspiration-first domestic
post_selection_runbook:
  - Detailed destination advisor, after user chooses one destination
```

Discovery plan:

1. Start with live content research because the request is subjective.
2. Use Xiaohongshu for recent weekend notes, photo spots, food, and crowd comments.
3. Use Zhihu for whether destinations are worth a weekend from Beijing.
4. Use guide/search pages for attraction clusters and route rhythm.
5. Extract candidates with strong food/photo signals and compact itineraries.

Verification plan:

1. Check travel time from Beijing.
2. Check local movement burden.
3. Check weather if the weekend is known.
4. Check official pages for any must-visit attraction that anchors the recommendation.

Tool plan:

Use agent-native web search, browser, MCP, or OpenCLI capabilities for live content discovery. Use repository scripts only after candidates need factual verification or evidence normalization.

Recommendation report shape:

- selected runbook stack.
- recommended candidates grouped by vibe.
- why each candidate fits food/photo/low-fatigue.
- transport and walking caveats.
- filtered-out destinations that are attractive but too tiring.
- lightweight weekend itinerary references.

## Example 3: International Feasibility

User request:

```text
想国庆出国玩 5-7 天，预算不要太高，签证不要太麻烦，最好安全、交通方便。
```

Constraint breakdown:

- region: international.
- travel window: China National Day holiday.
- trip length: 5-7 days.
- hard filters: visa simplicity, safety, transport convenience.
- preferences: lower budget.
- missing inputs: passport nationality/residency, origin city/airport, exact dates, budget range.

Runbook stack:

```text
primary_runbook: International feasibility
secondary_runbooks:
  - Weather-first
  - Inspiration-first domestic, adapted to international guide/social sources
hard_filter_runbooks:
  - International feasibility
  - Weather-first, if seasonal risk is high
preference_runbooks:
  - Inspiration-first domestic, for food/vibe/itinerary fit after feasibility passes
post_selection_runbook:
  - Detailed destination advisor, after user chooses one destination
```

Discovery plan:

1. Ask for passport/residency and origin airport if not available.
2. Use official visa and government sources before guide/social sources.
3. Use Trip.com, airline, rail, or public search for route and price context.
4. Use guide/social sources only for feasible destinations.

Verification plan:

1. Check visa and entry rules through official sources.
2. Check government travel advisories and safety notes.
3. Check flight feasibility and holiday price risk.
4. Check weather and seasonal disruption risk.
5. Check local transport convenience.

Tool plan:

```text
Use agent-native web search, browser, MCP, or OpenCLI capabilities for official visa/safety/transport sources.
Use weather tools once candidate destinations are narrowed.
Use travel-commerce sources for price and route hints only when access supports them.
```

Recommendation report shape:

- selected runbook stack.
- required clarifications.
- destinations grouped as feasible, needs verification, not recommended.
- visa/safety/transport summary.
- budget and holiday crowd risk.
- short itinerary references for feasible options.
- pre-booking verification checklist.

## Example 4: Selected Destination Detailed Advisor

User request:

```text
我决定去青岛，6月底 4 天，不自驾，想吃海鲜、看海、不要太累，帮我做详细攻略。
```

Constraint breakdown:

- selected destination: Qingdao.
- travel window: late June.
- trip length: 4 days.
- hard filters: no self-driving, low fatigue.
- preferences: seafood, sea views.
- missing inputs: origin city, hotel booked or preferred area, budget, seafood restrictions.

Runbook stack:

```text
primary_runbook: Detailed destination advisor
secondary_runbooks:
  - No-drive mobility
  - Weather-first
  - Inspiration-first domestic
hard_filter_runbooks:
  - No-drive mobility
  - Weather-first, for daily fallback planning
preference_runbooks:
  - Inspiration-first domestic
post_selection_runbook:
  - Detailed destination advisor
```

Research plan:

1. Official checks for attractions, beaches, museums, opening hours, reservations, and weather warnings.
2. Map checks for hotel areas, transit routes, walking burden, and taxi fallback.
3. Xiaohongshu/public search for recent seafood, sea-view routes, crowding, and pitfalls.
4. Zhihu/guide content for route rhythm and whether common attractions are worth it.
5. Weather checks by day for outdoor/indoor arrangement.

Verification plan:

1. Avoid itineraries that require long cross-city backtracking.
2. Keep each day clustered by area.
3. Add bad-weather alternatives for sea-view days.
4. Mark restaurants and seafood claims as inspiration unless verified by maps or official pages.

Tool plan:

```bash
uv run roamwise amap geocode 青岛站 --city 青岛
uv run roamwise amap geocode 栈桥 --city 青岛
```

Use weather and route tools when exact coordinates and dates are available.

Detailed plan shape:

- selected runbook stack.
- assumptions and clarifying questions.
- recommended hotel areas.
- day-by-day route.
- food suggestions by area.
- transit/taxi notes.
- bad-weather fallback.
- booking and official checks.
- budget estimate.
- confidence and caveats.

## Example 5: When To Ask Before Research

User request:

```text
帮我推荐一个旅游目的地。
```

Do not launch a large research run immediately.

Ask for:

- origin city.
- rough travel date or season.
- trip length.
- domestic or international preference.
- hard exclusions such as no rain, no driving, budget, visa, older adults, children, or mobility.
- preferred travel style.

If the user wants the agent to assume defaults, state assumptions and proceed with a broad inspiration-first discovery pass.
