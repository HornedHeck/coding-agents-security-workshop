"""Shared file-backed layer for the mock MCP servers.

State lives under ``$WS_CHALLENGE_DIR/state/``; per-run artefacts (the read log,
the sink log, the outbox) under ``$WS_RUN_DIR/``. Both are set on the container
by the launcher. The MCP server has no idea it is all files.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

from ws.config import ENV_CHALLENGE_DIR, ENV_INJECT, ENV_LEVEL, ENV_RUN_DIR


def _env_dir(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(
            f"{name} is not set — the MCP server must run via the launcher"
        )
    return Path(value)


def challenge_dir() -> Path:
    return _env_dir(ENV_CHALLENGE_DIR)


def run_dir() -> Path:
    path = _env_dir(ENV_RUN_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def inject_enabled() -> bool:
    return os.environ.get(ENV_INJECT, "1") != "0"


def level() -> int:
    return int(os.environ.get(ENV_LEVEL, "1"))


def injection_text() -> str | None:
    """The payload authored for the current level, or None.

    Authored as plain Markdown at ``state/injections/l<level>.md`` so it reads
    naturally; ``read_email`` appends it to the flagged email's body.
    """
    path = challenge_dir() / "state" / "injections" / f"l{level()}.md"
    return path.read_text().strip() if path.is_file() else None


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def load_inbox() -> list[dict]:
    inbox = challenge_dir() / "state" / "inbox"
    return [json.loads(p.read_text()) for p in sorted(inbox.glob("*.json"))]


def canary_block() -> str:
    return (challenge_dir() / "state" / "canary.txt").read_text().strip()


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(record) + "\n")


def log_read(action: str, args: dict, summary: str) -> None:
    _append_jsonl(
        run_dir() / "reads.jsonl",
        {"ts": _now(), "action": action, "args": args, "summary": summary},
    )


def log_sink(action: str, args: dict) -> None:
    _append_jsonl(
        run_dir() / "sink.jsonl", {"ts": _now(), "action": action, "args": args}
    )


def write_outbox(message: dict) -> str:
    outbox = run_dir() / "outbox"
    outbox.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%f")
    (outbox / f"{stamp}.json").write_text(json.dumps(message, indent=2))
    return stamp
