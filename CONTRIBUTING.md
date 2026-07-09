# Contributing

## Branching

- `main` is the stable integration branch.
- Create a new feature branch from `main` for each vertical slice.
- Keep branch names descriptive and scoped to one feature area.
- Preferred examples:
  - `feature/inventory-crud`
  - `feature/campaign-crud`
  - `feature/bid-request-auction`
  - `feature/event-ingestion`

## Commits

- Use focused commits with clear conventional-style messages.
- Preferred commit prefixes:
  - `feat:` for new functionality
  - `fix:` for bug fixes
  - `test:` for test additions or corrections
  - `docs:` for documentation updates
  - `chore:` for tooling, setup, or maintenance work

## Pull Requests

- Open one pull request per feature branch.
- Keep pull requests small and reviewable.
- Each pull request should include:
  - what changed
  - why it changed
  - how it was validated
  - remaining follow-up items, if any

## Validation

- Add or update backend tests for each backend slice.
- Keep GitHub Actions passing for the implemented scope.
- Prefer validating through the documented container workflow when local tooling differs across environments.

## Working Style

- Follow `spec.md` as the source of truth.
- Build in small vertical slices.
- Avoid mixing unrelated features on the same branch.
- If a branch grows beyond its intended scope, rename it or split follow-up work into a new branch before continuing.
