from ws import config
from ws.launcher import build_argv

KW = {
    "task": "do the task",
    "prompt": "be helpful",
    "model": "claude-haiku-4-5-20251001",
    "mcp_config": "/workshop/challenges/c1_email/mcp.json",
    "settings": "/workshop/challenges/c1_email/runs/T/settings.json",
    "allowed_tools": config.C1_ALLOWED_TOOLS,
}


def test_allow_strategy():
    argv = build_argv(strategy="allow", **KW)
    assert argv[0] == "codemie-claude"
    assert argv[1:5] == [
        "--task",
        "do the task",
        "--model",
        "claude-haiku-4-5-20251001",
    ]
    assert "--mcp-config=/workshop/challenges/c1_email/mcp.json" in argv
    assert "--append-system-prompt=be helpful" in argv
    assert "--allowed-tools=" + ",".join(config.C1_ALLOWED_TOOLS) in argv
    assert "--dangerously-skip-permissions" not in argv
    assert argv[-2:] == ["--output-format=stream-json", "--verbose"]


def test_bypass_strategy():
    argv = build_argv(strategy="bypass", **KW)
    assert "--dangerously-skip-permissions" in argv
    assert "--disallowed-tools=" + ",".join(config.BYPASS_DISALLOWED_TOOLS) in argv
    assert not any(a.startswith("--allowed-tools=") for a in argv)
