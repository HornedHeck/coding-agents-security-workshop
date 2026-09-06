"""Enforce C4's participant-owned MCP allow-list at individual tool level."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from ws.config import ENV_C4_ALLOWED_TOOLS, ENV_CHALLENGE_DIR

_DENY_REASON = "This tool is not permitted by the C4 allowed-tools configuration."


def _allowed_tools() -> set[str]:
    raw = os.environ.get(ENV_C4_ALLOWED_TOOLS, "[]")
    try:
        values = json.loads(raw)
    except json.JSONDecodeError:
        return set()
    return {value for value in values if isinstance(value, str)}


def _evaluate(payload: dict) -> dict | None:
    challenge = os.environ.get(ENV_CHALLENGE_DIR)
    if not challenge or Path(challenge).name != "c4_defense":
        return None
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str) or tool_name in _allowed_tools():
        return None
    return {
        "permissionDecision": "deny",
        "permissionDecisionReason": _DENY_REASON,
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        decision = _evaluate(payload)
        if decision is not None:
            print(json.dumps(decision))
    except Exception as exc:  # noqa: BLE001 - a policy hook error must not break the run
        print(f"ws-hook-c4-tool-guard: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
