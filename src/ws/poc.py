"""``ws-poc`` — in-container smoke check for the CodeMie credential PoC.

Runs inside the container built by ``poc/Dockerfile``. Driven by env vars set
by ``poc/run.py``:

* ``WS_POC_STRATEGY``  — ``s1`` | ``s2`` (label only; the container behaves the
  same, the host driver arranges the mounts)
* ``WS_POC_MODEL``     — model id for the end-to-end call

Prints a report table and exits non-zero on a hard failure.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_PONG = "PONG"
_E2E_TIMEOUT_S = 150


@dataclass
class Check:
    name: str
    ok: bool | None  # None = informational
    detail: str


def _run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            cmd,
            returncode=124,
            stdout=(exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""),
            stderr=f"[timed out after {timeout}s] "
            + ((exc.stderr or b"").decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")),
        )


def _codemie_home() -> Path:
    return Path(os.environ.get("CODEMIE_HOME", str(Path.home() / ".codemie")))


def _mask(value: str | None) -> str:
    if not value:
        return "<unset>"
    return f"{value[:4]}…{value[-4:]} ({len(value)} chars)" if len(value) > 12 else "<set>"


def check_env() -> Check:
    lines = [
        f"uname={os.uname().sysname}/{os.uname().machine} node_host={os.uname().nodename}",
        f"CODEMIE_HOME={_codemie_home()}",
        f"ANTHROPIC_BASE_URL={os.environ.get('ANTHROPIC_BASE_URL', '<unset>')}",
        f"CODEMIE_JWT_TOKEN={_mask(os.environ.get('CODEMIE_JWT_TOKEN'))}",
    ]
    return Check("environment", None, "; ".join(lines))


def check_profile_visible() -> Check:
    config = _codemie_home() / "codemie-cli.config.json"
    if not config.is_file():
        return Check("profile config", False, f"missing: {config}")
    creds = sorted((_codemie_home() / "credentials").glob("sso-*.enc"))
    return Check(
        "profile config",
        True,
        f"{config} present; credential files: {[p.name for p in creds] or 'none'}",
    )


def check_claude_installed() -> Check:
    probe = _run(["codemie-claude", "--version"], timeout=60)
    if probe.returncode == 0:
        return Check("claude code installed", True, probe.stdout.strip().splitlines()[-1:][0] if probe.stdout.strip() else "ok")
    install = _run(["codemie", "install", "claude"], timeout=300)
    reprobe = _run(["codemie-claude", "--version"], timeout=60)
    return Check(
        "claude code installed",
        reprobe.returncode == 0,
        f"installed at runtime (exit {install.returncode})",
    )


def check_doctor() -> Check:
    # `codemie doctor` exits non-zero for cosmetic gripes (not a git repo,
    # optional frameworks absent), so this is informational only.
    proc = _run(["codemie", "doctor"], timeout=120)
    tail = (proc.stdout or proc.stderr).strip().splitlines()[-3:]
    return Check("codemie doctor", None, f"exit {proc.returncode}; " + (" / ".join(tail) or "no output"))


def check_profile_status() -> Check:
    proc = _run(["codemie", "profile", "status"], timeout=90)
    body = proc.stdout + proc.stderr
    ok = "Authenticated" in body and "Authentication required" not in body
    hit = next((ln.strip() for ln in body.splitlines() if "Auth" in ln), "no auth line")
    return Check("profile status", ok, hit)


# Non-interactive: --dangerously-skip-permissions stops Claude Code blocking on
# a tool-permission / folder-trust prompt (there is no TTY). The image runs as a
# non-root user so this flag is allowed.
_CLAUDE_HEADLESS = ["--dangerously-skip-permissions"]


def check_end_to_end(model: str) -> Check:
    proc = _run(
        [
            "codemie-claude", "-m", model, *_CLAUDE_HEADLESS,
            "--task", f"Reply with exactly one word: {_PONG}",
        ],
        timeout=_E2E_TIMEOUT_S,
    )
    body = (proc.stdout or "") + (proc.stderr or "")
    ok = proc.returncode == 0 and _PONG in proc.stdout
    detail = f"exit {proc.returncode}; " + (
        f"got {_PONG!r}" if _PONG in proc.stdout else f"output tail: {body.strip()[-200:]!r}"
    )
    return Check("end-to-end codemie-claude", ok, detail)


def check_stream_json(model: str) -> Check:
    proc = _run(
        [
            "codemie-claude", "-m", model, *_CLAUDE_HEADLESS,
            "--task", f"Reply with exactly one word: {_PONG}",
            "--output-format", "stream-json", "--verbose",
        ],
        timeout=_E2E_TIMEOUT_S,
    )
    events = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    ok = proc.returncode == 0 and any(e.get("type") == "assistant" for e in events)
    return Check("stream-json survives proxy", ok, f"exit {proc.returncode}; {len(events)} JSON events")


def run_checks() -> list[Check]:
    model = os.environ.get("WS_POC_MODEL", _DEFAULT_MODEL)

    checks: list[Check] = [check_env()]
    checks.append(check_profile_visible())
    checks.append(check_claude_installed())
    checks.append(check_doctor())
    checks.append(check_profile_status())
    checks.append(check_end_to_end(model))
    checks.append(check_stream_json(model))
    return checks


def main(argv: list[str] | None = None) -> int:
    strategy = os.environ.get("WS_POC_STRATEGY", "s2")
    print(f"=== ws-poc (strategy {strategy}) ===")
    checks = run_checks()

    print("\n--- report ---")
    hard_fail = False
    for c in checks:
        mark = {True: "PASS", False: "FAIL", None: "info"}[c.ok]
        if c.ok is False:
            hard_fail = True
        print(f"[{mark}] {c.name}: {c.detail}")

    print(f"\nRESULT: {'FAIL' if hard_fail else 'PASS'} (strategy {strategy})")
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
