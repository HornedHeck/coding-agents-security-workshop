"""Build the ``codemie-claude`` command line and run a challenge in a container."""

from __future__ import annotations

import datetime as dt
import shutil
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ws import config
from ws.codemie_creds import MachineIdentity, rewrap
from ws.settings import generate as generate_settings

_CONTAINER_MCP = f"{config.CONTAINER_WORKSHOP}/challenges/{{name}}/mcp.json"


@contextmanager
def rewrapped_credentials(codemie_home: Path | None = None) -> Iterator[Path]:
    """Yield a scratch dir holding the host SSO credential re-wrapped for the
    container identity. Deleted on exit."""
    codemie_home = codemie_home or (Path.home() / ".codemie")
    scratch = Path(tempfile.mkdtemp(prefix="ws-creds-"))
    try:
        rewrap(
            codemie_home,
            scratch,
            MachineIdentity.for_host(),
            MachineIdentity(config.CONTAINER_HOSTNAME, "linux", config.docker_arch()),
        )
        yield scratch
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def run_acceptance(codemie_home: Path | None = None) -> int:
    """`ws setup --image` — run the in-container gate with credentials mounted."""
    with rewrapped_credentials(codemie_home) as scratch:
        proc = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--platform",
                config.linux_platform(),
                "--hostname",
                config.CONTAINER_HOSTNAME,
                "-v",
                f"{scratch}:{config.CONTAINER_CODEMIE_HOME}",
                "-e",
                f"WS_MODEL={config.DEFAULT_MODEL}",
                "--entrypoint",
                "ws-acceptance",
                config.HARNESS_IMAGE,
            ],
            check=False,
        )
    return proc.returncode


def build_argv(
    *,
    task: str,
    prompt: str,
    model: str,
    mcp_config: str,
    settings: str,
    allowed_tools: tuple[str, ...],
    strategy: str = config.AGENT_TOOL_STRATEGY,
) -> list[str]:
    """The full ``codemie-claude`` argv.

    CodeMie owns ``--task`` and ``--model`` (space form); every other flag is
    unknown to CodeMie and passed through to ``claude``, so it uses the
    ``--flag=value`` form to keep the value attached.
    """
    argv = [
        "codemie-claude",
        "--task",
        task,
        "--model",
        model,
        f"--mcp-config={mcp_config}",
        f"--settings={settings}",
        f"--append-system-prompt={prompt}",
    ]
    if strategy == "bypass":
        argv.append("--dangerously-skip-permissions")
        argv.append("--disallowed-tools=" + ",".join(config.BYPASS_DISALLOWED_TOOLS))
    else:
        argv.append("--allowed-tools=" + ",".join(allowed_tools))
    argv += ["--output-format=stream-json", "--verbose"]
    return argv


def _timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def run_challenge(
    challenge: str,
    level: int,
    *,
    model: str = config.DEFAULT_MODEL,
    inject: bool = True,
    codemie_home: Path | None = None,
) -> Path:
    """Run ``challenge`` at ``level`` in the harness container. Returns the run dir."""
    cdir = config.challenge_dir(challenge)
    if not cdir.is_dir():
        raise FileNotFoundError(f"unknown challenge: {challenge}")

    ts = _timestamp()
    run_dir = cdir / "runs" / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    container_run_dir = f"{config.CONTAINER_WORKSHOP}/challenges/{challenge}/runs/{ts}"

    generate_settings(level, run_dir / "settings.json")

    task = (cdir / "TASK.md").read_text()
    prompt = (config.REPO_ROOT / "src" / "ws" / "prompts" / "l1.md").read_text()

    with rewrapped_credentials(codemie_home) as scratch:
        argv = build_argv(
            task=task,
            prompt=prompt,
            model=model,
            mcp_config=_CONTAINER_MCP.format(name=challenge),
            settings=f"{container_run_dir}/settings.json",
            allowed_tools=config.C1_ALLOWED_TOOLS,
        )
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "--platform",
            config.linux_platform(),
            "--hostname",
            config.CONTAINER_HOSTNAME,
            "-v",
            f"{scratch}:{config.CONTAINER_CODEMIE_HOME}",
            "-v",
            f"{cdir}:{config.CONTAINER_WORKSHOP}/challenges/{challenge}",
            "-e",
            f"{config.ENV_CHALLENGE_DIR}={config.CONTAINER_WORKSHOP}/challenges/{challenge}",
            "-e",
            f"{config.ENV_RUN_DIR}={container_run_dir}",
            "-e",
            f"{config.ENV_INJECT}={'1' if inject else '0'}",
            "-e",
            f"{config.ENV_LEVEL}={level}",
            "-w",
            f"{config.CONTAINER_WORKSHOP}/challenges/{challenge}/workspace",
            config.HARNESS_IMAGE,
            *argv,
        ]
        (run_dir / "command.txt").write_text(" ".join(docker_cmd) + "\n")
        with (
            (run_dir / "stream.jsonl").open("w") as out,
            (run_dir / "stderr.log").open("w") as err,
        ):
            try:
                subprocess.run(
                    docker_cmd,
                    stdout=out,
                    stderr=err,
                    stdin=subprocess.DEVNULL,
                    timeout=config.AGENT_TIMEOUT_S,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                err.write(f"\n[ws] timed out after {config.AGENT_TIMEOUT_S}s\n")

    return run_dir
