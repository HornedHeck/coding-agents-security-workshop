"""Build the ``codemie-claude`` command line and run a challenge in a container."""

from __future__ import annotations

import datetime as dt
import json
import random
import re
import shutil
import string
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ws import config, detect
from ws.codemie_creds import MachineIdentity, rewrap
from ws.settings import generate as generate_settings

_CONTAINER_MCP = f"{config.CONTAINER_WORKSHOP}/challenges/{{name}}/mcp.json"

# run_dir names: "<attempt>.<run_in_attempt>_<keyword>", both zero-padded,
# starting at 00. Lets a facilitator eyeball which runs belong to one
# `ws run --runs N` invocation and skim the keyword instead of a timestamp.
_KEYWORD_MAX_LEN = 10
_RUN_NAME_RE = re.compile(r"^(\d+)\.\d+")


def sanitize_keyword(raw: str | None) -> str:
    """Alphanumeric-only, capped at 10 chars; a random one if none/empty."""
    if raw:
        cleaned = re.sub(r"[^a-zA-Z0-9]", "", raw)[:_KEYWORD_MAX_LEN]
        if cleaned:
            return cleaned
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


def next_attempt(challenge_dir: Path) -> int:
    """The next attempt number for ``challenge_dir/runs/`` (0 if none exist)."""
    runs_dir = challenge_dir / "runs"
    if not runs_dir.is_dir():
        return 0
    attempts = [
        int(m.group(1))
        for p in runs_dir.iterdir()
        if p.is_dir() and (m := _RUN_NAME_RE.match(p.name))
    ]
    return max(attempts, default=-1) + 1


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


def build_argv_copilot(
    *,
    task: str,
    prompt: str,
    model: str,
    cli: str,
    mcp_config: str | None,
    available_tools: tuple[str, ...],
    skill: str | None = None,
) -> list[str]:
    """The ``codemie-copilot`` argv for a headless, MCP-scoped run.

    ``--task`` and ``--model`` are CodeMie-owned (CodeMie drives the model, not
    the Copilot CLI); everything after is forwarded to GitHub Copilot CLI. The
    level defence has no Copilot flag, so it is prepended to the task. The
    ``--available-tools`` whitelist is variadic and goes last so it does not
    swallow the other flags.
    """
    combined_task = f"{prompt.strip()}\n\n---\n\n{task}" if prompt.strip() else task
    if skill:
        combined_task = (
            f"/{skill} Load this skill, then complete this task:\n\n{combined_task}"
        )
    argv = [
        cli,
        "--task",
        combined_task,
        "--model",
        model,
        *config.COPILOT_HEADLESS_FLAGS,
    ]
    if mcp_config is not None:
        argv[5:5] = ["--additional-mcp-config", f"@{mcp_config}"]
    if available_tools:
        argv.append("--available-tools")
        argv.extend(available_tools)
    return argv


def _timestamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def _prompt_text(spec: config.ChallengeSpec, level: int) -> str:
    name = spec.prompt_template.format(level=level)
    return (config.REPO_ROOT / "src" / "ws" / "prompts" / name).read_text()


def run_challenge(
    challenge: str,
    level: int,
    *,
    model: str = config.DEFAULT_MODEL,
    inject: bool = True,
    agent: str | None = None,
    codemie_home: Path | None = None,
    run_name: str | None = None,
) -> Path:
    """Run ``challenge`` at ``level`` in the harness container. Returns the run dir.

    ``run_name`` names the run directory (``<attempt>.<run_in_attempt>_<keyword>``,
    built by the caller for a ``--runs N`` batch); defaults to a UTC timestamp for
    a single ad hoc run (e.g. integration tests).
    """
    cdir = config.challenge_dir(challenge)
    if not cdir.is_dir():
        raise FileNotFoundError(f"unknown challenge: {challenge}")
    spec = config.challenge_spec(challenge)
    agent = agent or config.challenge_agent(spec)
    cli = config.agent_cli(agent)

    ts = run_name or _timestamp()
    run_dir = cdir / "runs" / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    container_challenge = f"{config.CONTAINER_WORKSHOP}/challenges/{challenge}"
    container_run_dir = f"{container_challenge}/runs/{ts}"
    user_skills_dir = cdir / "state" / "user_skills"

    task = (cdir / "TASK.md").read_text()
    prompt = _prompt_text(spec, level)

    allowed_tools = spec.allowed_tools
    config_mounts: list[str] = []
    if spec.has_participant_config:
        config_dir = cdir / "config"
        mcp_config = None
        participant_mcp_config = config_dir / "mcp.json"
        if participant_mcp_config.is_file():
            config_mounts += [
                "-v",
                f"{participant_mcp_config}:{config.CONTAINER_COPILOT_HOME}/mcp-config.json",
            ]
        allowed_path = config_dir / "allowed_tools.txt"
        if allowed_path.is_file():
            allowed_tools = tuple(
                ln.strip() for ln in allowed_path.read_text().splitlines() if ln.strip()
            )
        instructions = config_dir / "copilot-instructions.md"
        if instructions.is_file():
            config_mounts += [
                "-v",
                f"{instructions}:{config.CONTAINER_COPILOT_HOME}/copilot-instructions.md",
            ]
        user_hooks = config_dir / "user-hooks.json"
        if user_hooks.is_file():
            config_mounts += [
                "-v",
                f"{user_hooks}:{config.CONTAINER_COPILOT_HOOKS_DIR}/c4-user.json",
            ]
    else:
        mcp_config = _CONTAINER_MCP.format(name=challenge)

    if spec.per_run_canary:
        canary = detect.generate_canary()
        (run_dir / "canary.txt").write_text(canary + "\n")

    workspace_env: list[str] = []
    workspace_mounts: list[str] = []
    policy_env: list[str] = []
    if spec.has_participant_config:
        policy_env = [
            "-e",
            (
                f"{config.ENV_C4_ALLOWED_TOOLS}="
                f"{json.dumps(config.copilot_permitted_tool_names(allowed_tools))}"
            ),
        ]
    cwd = f"{container_challenge}/workspace"
    if spec.workspace_write_subdir is not None:
        shutil.copytree(cdir / "state" / "repo", run_dir / "ws", symlinks=True)
        container_workspace = f"{container_run_dir}/ws"
        if spec.isolate_workspace:
            container_workspace = "/workspace"
            workspace_mounts = ["-v", f"{run_dir}/ws:{container_workspace}"]
        workspace_env = ["-e", f"{config.ENV_WORKSPACE_DIR}={container_workspace}"]
        cwd = f"{container_workspace}/{spec.workspace_write_subdir}"

    if spec.per_run_canary:
        secrets_path = run_dir / "ws" / config.C4_SECRETS_FILE
        if secrets_path.is_file():
            secrets_path.write_text(
                secrets_path.read_text().replace(config.C4_CANARY_PLACEHOLDER, canary)
            )

    if agent == config.AGENT_CLAUDE:
        generate_settings(level, run_dir / "settings.json", challenge=challenge)

    with rewrapped_credentials(codemie_home) as scratch:
        if agent == config.AGENT_CLAUDE:
            argv = build_argv(
                task=task,
                prompt=prompt,
                model=model,
                mcp_config=mcp_config,
                settings=f"{container_run_dir}/settings.json",
                allowed_tools=allowed_tools,
            )
        else:
            argv = build_argv_copilot(
                task=task,
                prompt=prompt,
                model=model,
                cli=cli,
                mcp_config=mcp_config,
                available_tools=config.copilot_available_tools(allowed_tools),
                skill=spec.copilot_skill,
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
            f"{cdir}:{container_challenge}",
            *workspace_mounts,
            *(
                ["-v", f"{user_skills_dir}:{config.CONTAINER_COPILOT_SKILLS_DIR}"]
                if user_skills_dir.is_dir() and agent == config.AGENT_COPILOT
                else []
            ),
            *config_mounts,
            "-e",
            f"{config.ENV_CHALLENGE_DIR}={container_challenge}",
            "-e",
            f"{config.ENV_RUN_DIR}={container_run_dir}",
            "-e",
            f"{config.ENV_INJECT}={'1' if inject else '0'}",
            "-e",
            f"{config.ENV_LEVEL}={level}",
            *workspace_env,
            *policy_env,
            "-w",
            cwd,
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
