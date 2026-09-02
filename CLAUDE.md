# CLAUDE.md

Materials for the coding-agent security workshop: the plans, and the harness
code that implements them. Build-checklist step 0 (credential pass-through PoC,
`poc/` + `src/ws/`) is done; step 1 (harness skeleton) is specced in
`specs/001-harness-skeleton/`.

## What's where

- `PLAN.md` — concept, motivation, sources for slides, key theses. Change
  rarely, only when the workshop's concept shifts.
- `WORKSHOP_DETAILED_PLAN.md` — the working detailed plan: stack, harness,
  sections, challenges, hints, timing, build checklist, open questions.
  **The primary document, keep it up to date.**
- `poc/`, `src/ws/` — the CodeMie credential-pass-through PoC. `poc/README.md`
  explains it; the design write-up is in `WORKSHOP_DETAILED_PLAN.md §0`
  ("Credentials into the container").
- `specs/` — spec-driven-development specs (`specs/NNN-slug/SPEC.md`), one per
  non-trivial change. `specs/README.md` covers numbering and lifecycle; the
  `spec` skill covers authoring.

When stack/format decisions change, update `WORKSHOP_DETAILED_PLAN.md` (and
`PLAN.md` if the concept changed), not just the chat reply.

## Decisions locked in (details in WORKSHOP_DETAILED_PLAN.md §0)

- **Format:** individual, no teams, no scoring/leaderboard/competition. The
  harness prints "FLAG CAPTURED / not captured" privately to each
  participant. Group of up to ~15. 90 min main block + an optional 90 min
  continuation.
- **Victim-agent stack:** Claude Code CLI via `codemie-claude`
  (`codemie-ai/codemie-code`) — routes through a local CodeMie proxy on
  corporate tokens. NOT the Claude Agent SDK.
- **Everything on the participant path is Python, not bash** (participants may
  be on Windows): the `ws` CLI and all challenge tooling. Paths via `pathlib`,
  not strings.
- **A `Makefile` carries developer-only commands** (build images, run tests,
  lint). macOS only, never on the participant path — participants only run
  `uv run ws ...`.
- **Project and dependency management — `uv`** (`pyproject.toml` + `uv.lock`).
  A single entry point — the Python CLI `ws` (`uv run ws run c1 --level 1`,
  `ws eval c4`, `ws setup`).
- **mock MCP** — separate stdio MCP servers in Python (`uv run
  ws-mcp-<name>`), file-backed.
- **Claude Code hooks** (`PreToolUse`/`PostToolUse`) — `command: "uv run
  ws-hook-*"`, Python, reading JSON from stdin. These drive sink detection,
  flag-capture detection, and the guard.
- **Levels L1/L2/L3** — `--append-system-prompt` + a generated
  `settings.json` + the `ws-hook-guard` hook + `policy_mcp`.

## Working rules

- Don't assume requirements/architecture for the workshop — ask. Reasonable
  implementation details are fine once the requirement is clear.
- Libraries: check the current version against official docs/repo before
  adding one.
- Code comments — only when the "why" isn't obvious (hidden constraints,
  workarounds, invariants).
- Output: concise, bullet points, no emoji, no unnecessary explanations.
- Respond in Russian in chat; technical terms and identifiers stay in the
  original language.
- **All text in the repository is British English only** (commit messages,
  `.md` file content, code comments, PR descriptions). This covers the
  entire git history: anyone cloning the repo must see only English text,
  never Russian — regardless of the chat language.

## Open questions

See `WORKSHOP_DETAILED_PLAN.md §10` for the current list (CodeMie PoC, the
licence's model catalogue, Windows without WSL, gateway rate limits, 2A
channels, etc.).
</content>
