# CLAUDE.md

Materials for the coding-agent security workshop. This is currently the
**design stage** — no code yet, only plans.

## What's where

- `PLAN.md` — concept, motivation, sources for slides, key theses. Change
  rarely, only when the workshop's concept shifts.
- `WORKSHOP_DETAILED_PLAN.md` — the working detailed plan: stack, harness,
  sections, challenges, hints, timing, build checklist, open questions.
  **The primary document, keep it up to date.**

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
- **Everything we write is in Python, not bash** (participants may be on
  Windows). No Make. Paths via `pathlib`, not strings.
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

## Open questions

See `WORKSHOP_DETAILED_PLAN.md §10` for the current list (CodeMie PoC, the
licence's model catalogue, Windows without WSL, gateway rate limits, 2A
channels, etc.).
</content>
