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


def test_c2_accepts_levels_1_to_3_with_broad_matcher(tmp_path):
    for level in (1, 2, 3):
        settings = generate(
            level, tmp_path / f"s{level}.json", challenge="c2_channel_hunt"
        )
        group = settings["hooks"]["PreToolUse"][0]
        assert group["matcher"] == "mcp__.*"
        assert group["hooks"][0]["command"] == HOOK_SINK_CMD


def test_c2_rejects_level_4(tmp_path):
    with pytest.raises(ValueError):
        generate(4, tmp_path / "s.json", challenge="c2_channel_hunt")
