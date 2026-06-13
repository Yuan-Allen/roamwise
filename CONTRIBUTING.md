# Contributing

This project uses small, reviewable changes and Conventional Commits.

## Branch Names

Use lowercase kebab-case:

- `docs/project-bootstrap`
- `feat/destination-ranking`
- `feat/weather-provider`
- `fix/source-timeout`
- `chore/dev-tooling`
- `test/ranking-fixtures`

Prefer one purpose per branch. Keep branches short-lived while the project is moving quickly.

## Commit Messages

Use the Conventional Commits 1.0.0 shape:

```text
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Common types for this project:

- `feat`: user-visible capability or new agent behavior.
- `fix`: bug fix.
- `docs`: documentation-only change.
- `test`: tests or fixtures.
- `refactor`: code structure change without behavior change.
- `chore`: maintenance, setup, or repo housekeeping.
- `build`: dependency, packaging, or build-system changes.
- `ci`: CI configuration.

Examples:

```text
docs: bootstrap travel agent project charter
feat(weather): add provider interface
feat(ranking): score destinations by weather and transport
fix(scraper): handle empty search results
test(ranking): add golden cases for rainy-weekend trips
```

Breaking changes must be marked with `!` or a `BREAKING CHANGE:` footer.

## Change Discipline

- Keep each commit focused on one product or engineering intent.
- Include source and freshness metadata whenever adding external-data behavior.
- Add tests or fixtures for ranking, parsing, and itinerary generation logic.
- Never commit secrets, cookies, raw session dumps, or private user travel data.
