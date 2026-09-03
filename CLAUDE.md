# CLAUDE.md

Materials for the coding-agent security workshop: the plans, and the harness
code that implements them. Build-checklist step 0 (credential pass-through PoC)
and step 1 (harness skeleton, `specs/001-harness-skeleton/`) are done; step 4
(Challenge 2 channel hunt, `specs/002-c2-channel-hunt/`) is in progress.

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
- **Victim-agent stack:** GitHub Copilot CLI via `codemie-copilot`
  (`codemie-ai/codemie-code`, wrapping `@github/copilot`) — routes through a
  local CodeMie proxy on corporate tokens; the model is CodeMie-driven
  (`--model` on the wrapper, not the agent CLI). The agent is configurable
  (`ws run … --agent claude|copilot`, default `copilot`); `codemie-claude`
  (Claude Code) is kept as the alternate. NOT the Claude Agent SDK. Copilot has
  no per-tool `PreToolUse` hook, so flag capture is detected from the MCP
  server sink log (`sink.jsonl`), not the hook; tool scoping uses Copilot's
  `--available-tools` whitelist and `--disable-builtin-mcps`.
- **Everything on the participant path is Python, not bash** (participants may
  be on Windows): the `ws` CLI and all challenge tooling. Paths via `pathlib`,
  not strings.
- **A `Makefile` carries developer-only commands** (build images, run tests,
  lint). macOS only, never on the participant path — participants only run
  `uv run ws ...`.
- **Project and dependency management — `uv`** (`pyproject.toml` + `uv.lock`).
  A single entry point — the Python CLI `ws` (`uv run ws run c1 --level 1`,
  `ws eval c4`, `ws setup`).
- **mock MCP** — separate stdio MCP servers in Python (`mcp` v2 `MCPServer`),
  file-backed, run **inside the container** as the venv console script
  (`command: "/opt/uv/venv/bin/ws-mcp-<name>"` in `mcp.json`).
- **Claude Code hooks** (`PreToolUse`/`PostToolUse`) — `command:
  "/opt/uv/venv/bin/ws-hook-*"` in the generated `settings.json`, Python,
  reading JSON from stdin. Used only on the `claude` agent (Copilot has no
  per-tool hook). On both agents the MCP servers themselves log every read and
  every sink call, so capture and channel attribution work agent-independently;
  `verdict.py` falls back to scanning `sink.jsonl` when no hook wrote a marker.
- **Levels L1/L2/L3** — on `claude`, `--append-system-prompt` + a generated
  `settings.json` (+ `ws-hook-guard` + `policy_mcp` for the guard). On
  `copilot`, the level defence is prepended to the task prompt (no
  `--append-system-prompt` flag exists); the guard/blocking hook does not port.

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
