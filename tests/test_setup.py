import subprocess

from ws import config, setup


def test_build_image_builds_base_then_harness(tmp_path, monkeypatch):
    commands = []

    monkeypatch.setattr(
        setup, "check_docker", lambda: setup.Check("docker", True, "running")
    )
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(config, "linux_platform", lambda: "linux/test")

    def fake_run(command, **kwargs):
        commands.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(setup.subprocess, "run", fake_run)

    assert setup.build_image() == 0
    assert commands == [
        (
            [
                "docker",
                "build",
                "--platform",
                "linux/test",
                "-t",
                config.BASE_IMAGE,
                "-f",
                str(config.BASE_DOCKERFILE),
                "--build-arg",
                f"CODEMIE_VERSION={config.CODEMIE_VERSION}",
                "--build-arg",
                f"COPILOT_VERSION={config.COPILOT_VERSION}",
                "--build-arg",
                f"UV_IMAGE={config.UV_IMAGE}",
                ".",
            ],
            {"cwd": tmp_path, "check": False},
        ),
        (
            [
                "docker",
                "build",
                "--platform",
                "linux/test",
                "-t",
                config.HARNESS_IMAGE,
                "-f",
                str(config.HARNESS_DOCKERFILE),
                ".",
            ],
            {"cwd": tmp_path, "check": False},
        ),
    ]


def test_build_image_stops_when_docker_is_unavailable(monkeypatch, capsys):
    monkeypatch.setattr(
        setup,
        "check_docker",
        lambda: setup.Check("docker", False, "daemon not reachable"),
    )

    assert setup.build_image() == 1
    assert capsys.readouterr().out == "[FAIL] docker: daemon not reachable\n"


def test_build_image_stops_when_base_image_build_fails(tmp_path, monkeypatch):
    commands = []
    monkeypatch.setattr(
        setup, "check_docker", lambda: setup.Check("docker", True, "running")
    )
    monkeypatch.setattr(config, "REPO_ROOT", tmp_path)

    def fake_run(command, **_kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, 42)

    monkeypatch.setattr(setup.subprocess, "run", fake_run)

    assert setup.build_image() == 42
    assert len(commands) == 1
    assert commands[0][commands[0].index("-t") + 1] == config.BASE_IMAGE
