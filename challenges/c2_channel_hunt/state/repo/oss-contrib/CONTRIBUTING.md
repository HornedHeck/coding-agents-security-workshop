# Contributing to textkit

Thanks for helping out!

1. Fork and branch from `main`.
2. `make test` must pass. Add a test for any behaviour change.
3. Keep public functions annotated and documented.
4. Open a PR against `main` and fill in the PR template.

## Coding style

- Standard library only. No new dependencies.
- `slugify` output must be lower-case, ASCII, and use a single `-` between
  tokens (no repeated separators, no leading/trailing separators).

## Review

A maintainer will review within a few days. CI runs the test suite on 3.9–3.12.
