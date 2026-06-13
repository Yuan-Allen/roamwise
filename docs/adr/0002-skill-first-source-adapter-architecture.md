# ADR 0002: Skill-First Source Adapter Architecture

## Status

Accepted

## Context

The MVP shape is skill-driven with scripts and tools. The product must query many heterogeneous sources across China domestic and international travel: APIs, MCP servers, OpenCLI tools, browser automation, search, and manual seed data.

User priorities also change on every request. One trip may be weather-first, another may require no self-driving, another may optimize food, public transit, safety, or cost. The architecture must therefore separate current user priorities from source adapters and ranking math.

## Decision

Build the project around four boundaries:

1. A repo skill that describes workflow and decision discipline.
2. Source adapters that normalize all external access into evidence objects.
3. A dynamic ranking profile that represents each request's hard filters and weights.
4. Deterministic scripts for collection, normalization, filtering, ranking, and report generation.

The first implementation should avoid a heavy orchestration framework until source access and ranking behavior are proven. OpenAI Agents SDK or LangGraph can be added later without changing the provider contracts.

## Consequences

- Source-specific access can evolve independently.
- Ranking can be tested without live APIs or an LLM.
- Social content can be labeled as inspiration while official/API facts remain authoritative.
- New access methods such as MCP or OpenCLI can be added as adapter types.
- The first MVP remains lightweight but has clean upgrade paths.
