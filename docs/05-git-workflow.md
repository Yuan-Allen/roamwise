# Git Workflow

## Repository Defaults

- Main branch: `main`.
- Work branches: `<type>/<short-description>`.
- Commit style: Conventional Commits 1.0.0.
- Pull requests: small and focused when a remote is introduced.

## Branch Naming

Use one of these prefixes:

- `feat/` for product behavior or new capabilities.
- `fix/` for bug fixes.
- `docs/` for documentation.
- `test/` for tests and fixtures.
- `refactor/` for internal restructuring.
- `chore/` for maintenance.
- `build/` for dependencies and build tooling.
- `ci/` for CI configuration.

Examples:

```text
docs/requirements-v1
feat/weather-provider
feat/destination-ranking
fix/traffic-provider-timeouts
test/itinerary-golden-cases
chore/repo-tooling
```

## Commit Format

Use:

```text
<type>[optional scope]: <description>
```

Examples:

```text
docs: bootstrap travel agent project charter
docs(data): add source access matrix
feat(weather): add forecast provider adapter
feat(ranking): explain destination score tradeoffs
fix(itinerary): avoid impossible same-day transfers
```

Use `!` for breaking changes:

```text
feat(api)!: replace trip request schema
```

Or use a footer:

```text
BREAKING CHANGE: trip requests now require origin coordinates.
```

## Recommended Development Loop

1. Create a focused branch.
2. Make a small change.
3. Run relevant checks.
4. Commit with a Conventional Commit message.
5. Merge after review or local verification.

## Suggested Scopes

- `agent`
- `weather`
- `traffic`
- `transport`
- `content`
- `ranking`
- `itinerary`
- `data`
- `ui`
- `docs`
- `ci`

## Commit Type Guidance

- Use `docs` for requirements, design notes, and source-policy docs.
- Use `feat` when the user can do something new.
- Use `fix` when behavior was wrong.
- Use `test` when adding or changing tests only.
- Use `chore` for repository setup and non-product maintenance.
- Use `refactor` only when behavior should stay the same.

## Git Hygiene

- Do not commit `.env`, cookies, tokens, exported private user data, or raw session dumps.
- Keep generated artifacts out of Git unless they are intentional fixtures.
- Prefer fixtures with sanitized data.
- Before committing, run `git status --short` and inspect the diff.
