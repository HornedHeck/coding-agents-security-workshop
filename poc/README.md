# PoC: CodeMie credential pass-through into Docker

Answers one question for `WORKSHOP_DETAILED_PLAN.md` §9 step 0: **can a
containerised `codemie-claude` reach the CodeMie gateway using a credential
that lives on the host, and how?** Nothing else — no MCP, no hooks, no levels.

## Prerequisites

- Docker running.
- `@codemieai/code` installed on the host and `codemie profile login`
  completed (browser SSO). This writes `~/.codemie/`.
- `uv` on the host.

## Run

From the repository root:

```
uv run python poc/run.py --strategy s2     # the working path
uv run python poc/run.py --strategy s1     # negative control
```

## Strategies

| | How the credential gets in | Status |
|---|---|---|
| **s2** rewrap | `ws-rewrap` decrypts the SSO credential with the host identity and re-encrypts it with the container identity (`ws-poc` / `linux` / `<arch>`), mounted at `/home/node/.codemie`; container hostname pinned with `--hostname ws-poc` | **works** — verified end-to-end (`PONG`) on macOS/arm64 |
| **s1** mount | bind-mount `~/.codemie` read-only | **negative control** — the credential file is keyed by `hostname+os+arch`, so it will not decrypt in a Linux container from a macOS/Windows host |
| **s3** login | `codemie profile login` inside the container | not implemented — the SSO callback port is dynamic, needs `--network host` (Linux) or a patch |

The image runs as the non-root `node` user (Claude Code refuses
`--dangerously-skip-permissions` as root) and sets
`NODE_OPTIONS=--dns-result-order=ipv4first` (the in-process proxy binds IPv4;
Node `fetch` otherwise tries `::1` and hangs).

## Reading the result

Each strategy prints a per-check report and a `RESULT: PASS/FAIL` line; the
driver prints a final `MATRIX`. The check that matters is
**`end-to-end codemie-claude`** — a real round-trip to the gateway returning
`PONG`. `stream-json survives proxy` confirms the flag the real harness needs.

`ws-rewrap` also prints each credential's cookie names and time-to-expiry —
the SSO session must outlast the workshop (~90 min).

## Notes

- `codemie-claude` self-hosts its proxy in-process on a dynamic localhost
  port; there is **no** separate `codemie proxy` daemon in this path.
- The gateway logs sessions (`codemie analytics`); the end-to-end checks make
  real calls. Do not wire them into CI.
- Pinned versions live in `poc/Dockerfile` (`CODEMIE_VERSION`, the `uv` image)
  and `../pyproject.toml`.
