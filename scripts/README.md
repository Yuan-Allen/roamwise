# Scripts

This directory will contain local commands used by the Roamwise skill.

Planned command groups:

- `intake`: parse user requests into structured travel constraints.
- `candidates`: generate candidate destinations.
- `collect`: run source adapters for weather, maps, transport, content, and official notices.
- `rank`: apply hard filters and score destinations.
- `report`: generate markdown reports and itinerary references.
- `eval`: run golden examples and source-adapter tests.

Commands should emit structured JSON or Markdown and should be safe for an agent to call repeatedly.

Current command:

```text
uv run roamwise recommend weather examples/requests/rain_first.json
```
