from pathlib import Path

from ws import cli


def test_c2_clean_runs_once_without_injection(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "run_host_checks", list)
    monkeypatch.setattr(cli, "next_attempt", lambda _challenge: 0)
    monkeypatch.setattr(
        cli,
        "run_challenge",
        lambda *args, **kwargs: calls.append((args, kwargs)) or Path("run"),
    )
    monkeypatch.setattr(cli.verdict, "render", lambda _run: 0)

    assert cli.main(["c2-clean"]) == 0
    assert len(calls) == 1
    assert calls[0][0] == ("c2_channel_hunt", 1)
    assert calls[0][1]["inject"] is False


def test_c2_dirty_runs_five_times_with_injection(monkeypatch):
    calls = []
    monkeypatch.setattr(cli.setup, "run_host_checks", list)
    monkeypatch.setattr(cli, "next_attempt", lambda _challenge: 0)
    monkeypatch.setattr(
        cli,
        "run_challenge",
        lambda *args, **kwargs: calls.append((args, kwargs)) or Path("run"),
    )
    monkeypatch.setattr(cli.verdict, "aggregate", lambda _runs: 0)

    assert cli.main(["c2-dirty"]) == 0
    assert len(calls) == 5
    assert all(call[0] == ("c2_channel_hunt", 1) for call in calls)
    assert all(call[1]["inject"] is True for call in calls)
