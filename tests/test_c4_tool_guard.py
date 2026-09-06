import io
import json

from ws import config
from ws.hooks import c4_tool_guard


def _feed(monkeypatch, tool_name):
    monkeypatch.setattr(
        "sys.stdin",
        io.StringIO(json.dumps({"tool_name": tool_name, "tool_input": {}})),
    )


def test_allows_exactly_configured_c4_tool(monkeypatch, capsys):
    monkeypatch.setenv(config.ENV_CHALLENGE_DIR, "/workshop/challenges/c4_defense")
    monkeypatch.setenv(config.ENV_C4_ALLOWED_TOOLS, '["issues-read_issue"]')
    _feed(monkeypatch, "issues-read_issue")

    assert c4_tool_guard.main() == 0
    assert capsys.readouterr().out == ""


def test_denies_other_tool_in_configured_server(monkeypatch, capsys):
    monkeypatch.setenv(config.ENV_CHALLENGE_DIR, "/workshop/challenges/c4_defense")
    monkeypatch.setenv(config.ENV_C4_ALLOWED_TOOLS, '["issues-read_issue"]')
    _feed(monkeypatch, "issues-post_comment")

    assert c4_tool_guard.main() == 0
    assert json.loads(capsys.readouterr().out) == {
        "permissionDecision": "deny",
        "permissionDecisionReason": "This tool is not permitted by the C4 allowed-tools configuration.",
    }


def test_does_not_apply_outside_c4(monkeypatch, capsys):
    monkeypatch.setenv(config.ENV_CHALLENGE_DIR, "/workshop/challenges/c2_channel_hunt")
    monkeypatch.setenv(config.ENV_C4_ALLOWED_TOOLS, "[]")
    _feed(monkeypatch, "issues-post_comment")

    assert c4_tool_guard.main() == 0
    assert capsys.readouterr().out == ""
