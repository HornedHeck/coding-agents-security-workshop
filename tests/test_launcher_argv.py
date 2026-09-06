from contextlib import contextmanager

import pytest

from ws import cli, config, launcher
from ws.launcher import build_argv, build_argv_copilot, next_attempt, sanitize_keyword

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


def test_c2_spec_selects_tools_and_prompt_template():
    spec = config.challenge_spec("c2_channel_hunt")
    assert spec.levels == (1, 2, 3)
    assert spec.default_runs == config.DEFAULT_RUNS
    assert spec.prompt_template.format(level=2) == "c2_l2.md"
    argv = build_argv(**{**KW, "allowed_tools": spec.allowed_tools})
    assert "--allowed-tools=" + ",".join(config.C2_ALLOWED_TOOLS) in argv
    assert "Read" not in spec.allowed_tools


def test_copilot_available_tools_collapse_to_servers():
    tools = config.copilot_available_tools(config.C2_ALLOWED_TOOLS)
    assert tools == ("repo", "issues", "web", "skill")  # TodoWrite dropped
    c1 = config.copilot_available_tools(config.C1_ALLOWED_TOOLS)
    assert c1 == ("email", "view")  # Read -> view, TodoWrite dropped


def test_copilot_permitted_tool_names_preserve_mcp_tool_scope():
    allowed = (
        "mcp__issues__read_issue",
        "mcp__issues__post_comment",
        "Skill",
        "TodoWrite",
    )

    assert config.copilot_permitted_tool_names(allowed) == (
        "issues-read_issue",
        "issues-post_comment",
        "skill",
    )


def test_c4_launcher_passes_exact_allow_list_to_policy_hook(tmp_path, monkeypatch):
    challenge_dir = tmp_path / "c4_defense"
    (challenge_dir / "config").mkdir(parents=True)
    (challenge_dir / "state" / "repo" / "textkit").mkdir(parents=True)
    (challenge_dir / "TASK.md").write_text("Complete the task.")
    (challenge_dir / "config" / "allowed_tools.txt").write_text(
        "mcp__issues__read_issue\n"
    )
    docker_commands = []

    @contextmanager
    def fake_credentials(_codemie_home=None):
        yield tmp_path / "credentials"

    def fake_run(command, **_kwargs):
        docker_commands.append(command)

    monkeypatch.setattr(config, "challenge_dir", lambda _challenge: challenge_dir)
    monkeypatch.setattr(launcher, "rewrapped_credentials", fake_credentials)
    monkeypatch.setattr(launcher.subprocess, "run", fake_run)

    launcher.run_challenge("c4_defense", 1, run_name="T")

    assert f'{config.ENV_C4_ALLOWED_TOOLS}=["issues-read_issue"]' in docker_commands[0]


def test_copilot_argv_is_headless_and_mcp_scoped():
    argv = build_argv_copilot(
        task="do the task",
        prompt="be helpful",
        model="gpt-5-mini-2025-08-07",
        cli="codemie-copilot",
        mcp_config="/workshop/challenges/c2_channel_hunt/mcp.json",
        available_tools=("repo", "issues", "web", "skill"),
        skill="release-notes",
    )
    assert argv[0] == "codemie-copilot"
    assert argv[1] == "--task"
    assert argv[2].startswith(
        "/release-notes Load this skill, then complete"
    )  # defence prepended to the task
    assert "do the task" in argv[2]
    assert argv[3:5] == ["--model", "gpt-5-mini-2025-08-07"]
    assert "--additional-mcp-config" in argv
    assert "@/workshop/challenges/c2_channel_hunt/mcp.json" in argv
    assert "--disable-builtin-mcps" in argv
    assert "--allow-all-tools" in argv
    # whitelist is variadic and trails the fixed flags
    i = argv.index("--available-tools")
    assert argv[i + 1 :] == ["repo", "issues", "web", "skill"]
    # no Claude-only flags leak through
    assert not any(a.startswith("--append-system-prompt") for a in argv)
    assert not any(a.startswith("--settings") for a in argv)


def test_copilot_argv_uses_user_level_mcp_config_when_omitted():
    argv = build_argv_copilot(
        task="do the task",
        prompt="",
        model="gpt-5-mini-2025-08-07",
        cli="codemie-copilot",
        mcp_config=None,
        available_tools=("repo",),
    )

    assert "--additional-mcp-config" not in argv
    assert argv[-2:] == ["--available-tools", "repo"]


def test_c4_evaluation_rejects_claude_agent():
    with pytest.raises(SystemExit) as exc:
        cli.main(["eval", "c4", "--agent", config.AGENT_CLAUDE])

    assert exc.value.code == 2


@pytest.mark.parametrize(
    "argv",
    (
        ["eval", "c2"],
        ["eval", "c4", "--runs", "0"],
        ["eval", "c4", "--runs", "-1"],
    ),
)
def test_c4_evaluation_rejects_invalid_arguments(argv):
    with pytest.raises(SystemExit) as exc:
        cli.main(argv)

    assert exc.value.code == 2


def test_sanitize_keyword_keeps_alphanumeric_and_caps_length():
    assert sanitize_keyword("agents.md!!") == "agentsmd"
    assert sanitize_keyword("a b-c_d/e") == "abcde"
    assert sanitize_keyword("x" * 20) == "x" * 10


def test_sanitize_keyword_is_random_when_absent():
    assert sanitize_keyword(None) != sanitize_keyword(None)
    assert sanitize_keyword("!!!") != sanitize_keyword("!!!")
    for kw in (sanitize_keyword(None), sanitize_keyword("---")):
        assert kw.isalnum()
        assert 0 < len(kw) <= 10


def test_next_attempt_starts_at_zero(tmp_path):
    assert next_attempt(tmp_path) == 0
    (tmp_path / "runs").mkdir()
    assert next_attempt(tmp_path) == 0


def test_next_attempt_increments_past_existing_and_ignores_timestamps(tmp_path):
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "00.00_abc123").mkdir()
    (runs / "00.01_abc123").mkdir()
    (runs / "20260903T105830Z").mkdir()  # legacy timestamp dir, ignored
    assert next_attempt(tmp_path) == 1

    (runs / "03.00_xyz").mkdir()
    assert next_attempt(tmp_path) == 4
