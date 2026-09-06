from pathlib import Path

import pytest

from ws import cli


def test_c1_clean_runs_once_without_injection(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "run_host_checks", list)
    monkeypatch.setattr(cli, "next_attempt", lambda _challenge: 0)
    monkeypatch.setattr(
        cli,
        "run_challenge",
        lambda *args, **kwargs: calls.append((args, kwargs)) or Path("run"),
    )
    monkeypatch.setattr(cli.verdict, "render", lambda _run: 0)

    assert cli.main(["run", "c1", "--clean"]) == 0
    assert len(calls) == 1
    assert calls[0][0] == ("c1_email", 1)
    assert calls[0][1]["inject"] is False


def test_c2_defaults_to_five_attacked_runs(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "run_host_checks", list)
    monkeypatch.setattr(cli, "next_attempt", lambda _challenge: 0)
    monkeypatch.setattr(
        cli,
        "run_challenge",
        lambda *args, **kwargs: calls.append((args, kwargs)) or Path("run"),
    )
    monkeypatch.setattr(cli.verdict, "aggregate", lambda _runs: 0)

    assert cli.main(["run", "c2"]) == 0
    assert len(calls) == 5
    assert all(call[0] == ("c2_channel_hunt", 1) for call in calls)
    assert all(call[1]["inject"] is True for call in calls)


def test_c2_runs_once_with_attacks_when_requested(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "run_host_checks", list)
    monkeypatch.setattr(cli, "next_attempt", lambda _challenge: 0)
    monkeypatch.setattr(
        cli,
        "run_challenge",
        lambda *args, **kwargs: calls.append((args, kwargs)) or Path("run"),
    )
    monkeypatch.setattr(cli.verdict, "render", lambda _run: 0)

    assert cli.main(["run", "c2", "--runs", "1"]) == 0
    assert len(calls) == 1
    assert calls[0][0] == ("c2_channel_hunt", 1)
    assert calls[0][1]["inject"] is True


def test_c2_rejects_clean_run(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.setup,
        "run_host_checks",
        lambda: pytest.fail("clean C2 run should be rejected before preflight"),
    )

    assert cli.main(["run", "c2", "--clean"]) == 2
    assert capsys.readouterr().out == (
        "[FAIL] --clean is only supported by c1; other challenges always include attacks\n"
    )


def test_c4_uses_the_defence_evaluator(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "run_host_checks", list)
    monkeypatch.setattr(cli, "next_attempt", lambda _challenge: 0)
    monkeypatch.setattr(
        cli,
        "run_challenge",
        lambda *args, **kwargs: calls.append((args, kwargs)) or Path("run"),
    )
    monkeypatch.setattr(cli.verdict, "eval_c4", lambda _runs: 0)

    assert cli.main(["run", "c4"]) == 0
    assert len(calls) == 3
    assert all(call[0] == ("c4_defense", 1) for call in calls)
    assert all(call[1]["inject"] is True for call in calls)


def test_c4_rejects_claude_agent(monkeypatch, capsys):
    monkeypatch.setattr(
        cli.setup,
        "run_host_checks",
        lambda: pytest.fail("Claude C4 run should be rejected before preflight"),
    )

    assert cli.main(["run", "c4", "--agent", "claude"]) == 2
    assert capsys.readouterr().out == "[FAIL] c4 supports the Copilot agent only\n"


def test_image_builds_workshop_images(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "build_image", lambda: calls.append(True) or 0)

    assert cli.main(["image"]) == 0
    assert calls == [True]


def test_run_defaults_to_level_one(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "run_host_checks", list)
    monkeypatch.setattr(cli, "next_attempt", lambda _challenge: 0)
    monkeypatch.setattr(
        cli,
        "run_challenge",
        lambda *args, **kwargs: calls.append((args, kwargs)) or Path("run"),
    )
    monkeypatch.setattr(cli.verdict, "render", lambda _run: 0)

    assert cli.main(["run", "c1"]) == 0
    assert calls[0][0] == ("c1_email", 1)
    assert calls[0][1]["inject"] is True


def test_run_rejects_non_positive_run_count():
    with pytest.raises(SystemExit) as exc:
        cli.main(["run", "c2", "--runs", "0"])

    assert exc.value.code == 2
