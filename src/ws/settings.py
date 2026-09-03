"""Generate the per-run Claude Code ``settings.json``.

Passed to the agent as ``--settings=<file>``. It merges with (does not replace)
CodeMie's plugin settings; the hook lists concatenate.
"""

from __future__ import annotations

import json
from pathlib import Path

from ws.config import HOOK_SINK_CMD, challenge_spec


def generate(level: int, settings_path: Path, *, challenge: str = "c1_email") -> dict:
    """Write ``settings_path`` for ``level`` and return the settings dict."""
    spec = challenge_spec(challenge)
    if level not in spec.levels:
        raise ValueError(f"level {level} not implemented for {challenge}")

    settings = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": spec.mcp_matcher,
                    "hooks": [
                        {"type": "command", "command": HOOK_SINK_CMD, "timeout": 15}
                    ],
                }
            ]
        }
    }
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2))
    return settings
