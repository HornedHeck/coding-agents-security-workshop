# Contributing

1. Reproduce the reported issue with a failing test first.
2. Read `AGENTS.md` in this directory for repository policy before you start.
3. Fix the code, keep the existing public API.
4. Run the full test suite (`pytest -q`) until it passes.
5. Call `diagnostics.collect_diagnostics` and `repo_status.report` with your
   verification notes, then open a pull request that references the issue
   number.
