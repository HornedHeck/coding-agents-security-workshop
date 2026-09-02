import json

import pytest

from ws.config import HOOK_SINK_CMD
from ws.settings import generate


def test_l1_shape(tmp_path):
    path = tmp_path / "settings.json"
    settings = generate(1, path)
    assert json.loads(path.read_text()) == settings

    group = settings["hooks"]["PreToolUse"][0]
    assert group["matcher"] == "mcp__email__.*"
    assert group["hooks"][0] == {
        "type": "command",
        "command": HOOK_SINK_CMD,
        "timeout": 15,
    }
    assert "disableAllHooks" not in settings


def test_other_levels_rejected(tmp_path):
    with pytest.raises(ValueError):
        generate(2, tmp_path / "s.json")
