"""Generate the per-run Claude Code ``settings.json``.

Passed to the agent as ``--settings=<file>``. It merges with (does not replace)
CodeMie's plugin settings; the hook lists concatenate.
"""

from __future__ import annotations

import json
from pathlib import Path

from ws.config import HOOK_SINK_CMD

_SINK_MATCHER = "mcp__email__.*"


def generate(level: int, settings_path: Path) -> dict:
    """Write ``settings_path`` for ``level`` and return the settings dict."""
    if level != 1:
        raise ValueError(f"level {level} not implemented (step 1 is L1 only)")

    settings = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": _SINK_MATCHER,
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
