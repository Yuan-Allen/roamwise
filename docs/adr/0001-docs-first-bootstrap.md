# ADR 0001: Docs-First Bootstrap

## Status

Accepted

## Context

The project goal depends on many choices that affect feasibility and legality: data sources, access methods, freshness requirements, ranking rules, product surface, storage, and agent runtime. Implementing code before these decisions would risk building the wrong abstraction around unavailable or unreliable sources.

## Decision

Initialize the repository with a docs-first project skeleton:

- Product brief.
- Clarification checklist.
- Iteration plan.
- Agent design sketch.
- Data-source plan.
- Git workflow.

The first code iteration should begin after the user confirms MVP surface, initial geography, source access methods, ranking priorities, and preferred stack.

## Consequences

- The project has a clear decision trail from the first commit.
- Implementation can proceed in small, source-validated increments.
- Some engineering choices remain intentionally undecided until the required external access paths are known.
