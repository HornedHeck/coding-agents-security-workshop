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

from ws import detect
from ws.config import (
    ENV_CHALLENGE_DIR,
    ENV_INJECT,
    ENV_LEVEL,
    ENV_RUN_DIR,
    ENV_WORKSPACE_DIR,
    challenge_spec,
)

# reads.jsonl keeps the returned content so verdict.py can attribute the
# channel; cap it so a large file does not bloat the log.
_READ_CONTENT_CAP = 20_000


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


def workspace_dir() -> Path:
    """The per-run copy of ``state/repo/`` (c2, c4). Set by the launcher."""
    return _env_dir(ENV_WORKSPACE_DIR)


def repo_subdir() -> str:
    """The workspace subdir the repo MCP treats as its root (per challenge,
    e.g. ``oss-contrib`` for c2, ``textkit`` for c4)."""
    subdir = challenge_spec(challenge_dir().name).workspace_write_subdir
    if subdir is None:
        raise RuntimeError("challenge has no workspace_write_subdir")
    return subdir


def inject_enabled() -> bool:
    return os.environ.get(ENV_INJECT) == "1"


def level() -> int:
    return int(os.environ.get(ENV_LEVEL, "1"))


def injection_text() -> str | None:
    """The payload authored for the current level, or None.

    Participant-authored Markdown at ``state/injections/l<level>.md``. The
    fixture starts empty. For c1, non-empty content is appended to the
    ``send_email`` tool description (tool poisoning).
    """
    path = challenge_dir() / "state" / "injections" / f"l{level()}.md"
    return path.read_text().strip() if path.is_file() else None


def _now() -> str:
    return dt.datetime.now(dt.UTC).isoformat()


def load_inbox() -> list[dict]:
    inbox = challenge_dir() / "state" / "inbox"
    return [json.loads(p.read_text()) for p in sorted(inbox.glob("*.json"))]


def load_issues() -> list[dict]:
    issues = challenge_dir() / "state" / "issues"
    return [json.loads(p.read_text()) for p in sorted(issues.glob("*.json"))]


def canary_block() -> str:
    return (challenge_dir() / "state" / "canary.txt").read_text().strip()


def canary_tokens() -> list[str]:
    """Every canary token a sink leak is matched against.

    Prefers a per-run generated canary (``$WS_RUN_DIR/canary.txt``, c4) over
    the static per-challenge tokens (``detect.canary_tokens``, c1/c2).
    """
    run_canary = run_dir() / "canary.txt"
    if run_canary.is_file():
        return [ln.strip() for ln in run_canary.read_text().splitlines() if ln.strip()]
    return detect.canary_tokens(challenge_dir())


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as fh:
        fh.write(json.dumps(record) + "\n")


def log_read(
    action: str,
    args: dict,
    summary: str,
    *,
    content: str | None = None,
    extra: dict | None = None,
) -> None:
    record = {"ts": _now(), "action": action, "args": args, "summary": summary}
    if content is not None:
        record["content"] = content[:_READ_CONTENT_CAP]
    if extra:
        record.update(extra)
    _append_jsonl(run_dir() / "reads.jsonl", record)


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
