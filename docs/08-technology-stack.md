# Technology Stack Recommendation

## Recommendation

Use a Python-first stack for the MVP:

- Python 3.12 or newer.
- `uv` for project, dependency, and script management.
- Pydantic for schemas and validation.
- Typer plus Rich for CLI commands.
- `httpx`, `tenacity`, and source-specific clients for API adapters.
- SQLite for normalized evidence, cache metadata, and run history.
- JSONL for append-only evidence artifacts.
- DuckDB or Polars only when analysis gets larger than SQLite-friendly workflows.
- Playwright for controlled browser automation when API/MCP/CLI access is unavailable.
- pytest, respx, freezegun, and golden Markdown fixtures for tests.

Agent orchestration should start thin:

- First implementation: deterministic scripts plus a repo skill.
- Add OpenAI Agents SDK when we need managed tool execution, guardrails, sessions, tracing, MCP integration, or multi-agent handoffs.
- Add LangGraph only if workflows become long-running, stateful, resumable graphs where explicit nodes, persistence, and human-in-the-loop state editing are worth the extra structure.

## Why Python First

The project is data-heavy and source-adapter-heavy. Python has the strongest fit for:

- API clients and browser automation.
- Data normalization and scoring.
- Local CLI tools.
- Pydantic schemas.
- Evaluation fixtures.
- Agent SDK ecosystem.

TypeScript can be added later for a web UI or an MCP server if the project needs a rich product surface.

## Framework Assessment

| Area | Recommended | Why | Alternative |
| --- | --- | --- | --- |
| Package manager | `uv` | Fast, modern Python workflow and script management | Poetry, pip-tools |
| CLI | Typer | Type-hint driven CLI, good help output, easy to grow | Click, argparse |
| Schema | Pydantic | Strong validation for LLM outputs and source facts | attrs, dataclasses |
| API clients | httpx | Async-first and testable | requests, aiohttp |
| Browser automation | Playwright | Cross-browser automation and tracing | Selenium |
| Local DB | SQLite | Simple, durable, easy to inspect | Postgres later |
| Analytics | DuckDB or Polars | Fast local tabular analysis | pandas |
| Agent runtime | OpenAI Agents SDK after the spike | Python-first managed loops, tools, MCP, sessions, tracing | LangGraph, Pydantic AI |
| Workflow graph | Defer LangGraph | Useful for durable graphs, but premature for the first source spike | Custom orchestrator |
| Web API | FastAPI later | Natural Python API path and Pydantic fit | Litestar, Django Ninja |

## Agent Runtime Recommendation

### Phase 1: No Heavy Agent Framework

Use scripts and typed functions first:

- Easier to test.
- Easier to debug provider access.
- Keeps ranking deterministic.
- Avoids hiding source access problems inside an agent loop.

### Phase 2: OpenAI Agents SDK

Adopt when the project needs:

- Multiple coordinated specialist agents.
- Tool execution managed by the runtime.
- Guardrails.
- Sessions.
- Tracing.
- MCP server tool calling.

OpenAI's Agents SDK is a good fit because it is Python-first, supports function tools, MCP server tool calling, handoffs, sessions, and tracing.

### Phase 3: LangGraph If Needed

Adopt only if we need:

- Explicit graph state.
- Durable execution and resume.
- Long-running jobs with checkpoints.
- Human-in-the-loop edits inside workflow state.

LangGraph is powerful, but likely heavier than needed before provider access, evidence schema, and ranking behavior are stable.

### Pydantic AI Position

Pydantic AI is worth watching and may be a strong fit if we want model-agnostic agents with type-safe dependency injection and built-in eval patterns. For this project, it is a secondary candidate because OpenAI Agents SDK aligns better with OpenAI tool/MCP execution if OpenAI models are the primary runtime.

## Suggested Dependencies For The First Code Spike

```toml
[project]
requires-python = ">=3.12"

dependencies = [
  "httpx",
  "pydantic",
  "pydantic-settings",
  "rich",
  "tenacity",
  "typer",
]

[dependency-groups]
dev = [
  "pytest",
  "pytest-asyncio",
  "respx",
  "ruff",
]
browser = [
  "playwright",
]
agent = [
  "openai-agents",
]
```

Do not install all optional groups immediately. Add `browser` and `agent` only when the first source spike needs them.

## Project Commands To Add Later

```text
uv run roamwise intake parse examples/requests/rain-first.md
uv run roamwise collect weather --request runs/demo/request.json
uv run roamwise collect routes --request runs/demo/request.json
uv run roamwise rank --run runs/demo
uv run roamwise report recommendations --run runs/demo
```

## References

- [uv documentation](https://docs.astral.sh/uv/)
- [Typer documentation](https://typer.tiangolo.com/)
- [Pydantic AI overview](https://pydantic.dev/docs/ai/overview/)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Playwright Python docs](https://playwright.dev/python/docs/intro)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Model Context Protocol introduction](https://modelcontextprotocol.io/docs/getting-started/intro)
