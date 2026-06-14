---
name: roamwise
description: Agent-led workflow for researching travel destinations, using Roamwise scripts as tools for evidence collection, ranking signals, and report artifacts.
---

# Roamwise Skill

Use this skill when a user asks for destination recommendations, trip feasibility research, itinerary references, or detailed travel advice.

## Skill Package Entry

When this repository is provided as a skill package, treat this file as the primary instruction surface.

Read references in this order as needed:

1. `skills/roamwise/README.md` for package usage, scope, and tool assumptions.
2. `docs/09-skill-first-usage.md` for the operating model and agent/tool boundary.
3. `docs/11-agent-runbooks.md` for runbook composition.
4. `docs/12-runbook-examples.md` for complex or ambiguous request examples.
5. `docs/10-content-source-playbooks.md` before using Xiaohongshu, Zhihu, Ctrip/Trip.com, public search, OpenCLI, MCP, or browser access.
6. `README.md` for available CLI tool commands and environment variables.

Do not require reading every document for every request. Read the smallest set needed to execute safely.

## Principles

- Evidence first, narrative second.
- The agent is the decision lead. Scripts standardize repeatable actions and provide evidence or scoring signals.
- This skill is the product interface. Code in the repository is a tool library for the agent.
- Separate factual sources from inspiration sources.
- Treat user-specific constraints as a dynamic ranking profile.
- Prefer official APIs and official notices for hard filters.
- Label stale, missing, conflicting, or social-only evidence.
- Use local seed candidates only as a fallback starting point; expand candidates through live research when useful.
- Do not book, purchase, post, like, comment, or modify user accounts in the MVP.

## Tool Use Discipline

- Decide the research plan before calling scripts.
- Use scripts for stable operations: fetch weather, query routes, normalize evidence, inspect cached content, produce draft reports.
- Use built-in web search, browser tools, MCP, OpenCLI, or platform adapters when qualitative destination discovery is needed.
- Treat script output as evidence, not authority.
- Preserve uncertainty when source coverage is weak.
- Add or remove destination candidates when live research supports it, then rerun relevant factual tools.
- Do not let a local seed pool, search result order, or numeric score decide the final recommendation by itself.
- Prefer agent-native web/search/browser capabilities for exploratory research when available; use repository scripts when repeatability or normalized evidence is useful.

## Available Tool Families

Use repository tools as optional helpers:

- Weather and destination checks: `uv run roamwise recommend weather ...` and `uv run roamwise recommend destination ...`.
- Amap diagnostics: `uv run roamwise amap geocode ...` and `uv run roamwise amap driving ...`.
- Content evidence contract: `uv run roamwise content seed ...`.
- Live content discovery should use agent-native web search, browser, MCP, or OpenCLI capabilities before adding repository adapters.

Tool assumptions:

- `AMAP_API_KEY` enables Amap Web Service API tools.
- Open-Meteo weather access does not require a key.
- Tool output is evidence or a draft signal, not the final answer.

## When Not To Start With Scripts

Start with live research instead of local scripts when:

- the user asks for inspiration, trend discovery, niche experiences, food scenes, or social sentiment.
- the candidate space is unclear or too broad.
- recent events, closures, crowding, visa changes, safety issues, or weather disruptions may dominate the decision.
- the request depends on platform-specific knowledge from Xiaohongshu, Zhihu, Ctrip/Trip.com, official tourism sites, forums, or local guides.

After live research narrows or expands candidates, use scripts to verify weather, routes, feasibility, and evidence structure.

## Runbook Composition

- Use `docs/11-agent-runbooks.md` to build a runbook stack before starting a recommendation.
- Select one `primary_runbook` for the dominant risk or decision driver.
- Add `secondary_runbooks` for every meaningful additional constraint or preference.
- Put weather-first, no-drive mobility, and international feasibility into `hard_filter_runbooks` when they can exclude destinations.
- Put inspiration-first domestic into `preference_runbooks` when the user asks for food, photos, niche places, recent trends, lifestyle fit, or weekend ideas.
- Use the detailed destination advisor as `post_selection_runbook` after the user selects a destination.
- If multiple runbooks apply, verify hard filters first, then use inspiration sources to improve fit among feasible candidates.
- Include the selected runbook stack in the recommendation report.
- Use `docs/12-runbook-examples.md` as execution references for complex or ambiguous requests.

## Workflow

1. Parse the user's request into structured constraints.
2. Build a ranking profile with hard filters and weighted preferences.
3. Build a runbook stack.
4. Decide the research plan, including factual sources and social/guide sources.
5. Generate seed candidates, then expand or revise them through live research.
6. Collect weather and environment facts.
7. Collect route, traffic, and transport facts.
8. Collect POI, food, hotel-area, guide, and social inspiration as needed.
9. Normalize every source result into evidence with source and freshness metadata.
10. Apply hard filters and compute ranking signals.
11. Synthesize factual evidence, social/guide findings, and user preferences.
12. Produce a recommendation report with tradeoffs and citations.
13. Generate itinerary references for the top destinations.
14. After the user selects a destination, expand into a detailed plan.
15. Run a final feasibility, citation, and risk review.

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
- When social or guide research reveals better candidates than local seeds, add them and rerun the relevant tools.

## Content Source Routing

- Use Xiaohongshu for recent domestic inspiration, lifestyle fit, food, photo spots, crowd comments, and pitfalls; corroborate factual claims elsewhere.
- Use Zhihu for long-form tradeoffs, comparisons, "is it worth it" reasoning, and hidden constraints.
- Use Ctrip or Trip.com for travel-commerce context, hotel-area clues, attraction/ticket references, and booking-link context; do not claim live availability without supported access and timestamps.
- Use public search to discover official pages, indexed guide content, and international references before adding platform-specific automation.
- Use official tourism, attraction, transport, weather, visa, and safety sources for hard filters and detailed-plan verification.
- Follow `docs/10-content-source-playbooks.md` before using OpenCLI or browser access for any social or guide platform.

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

- selected runbook stack.
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
