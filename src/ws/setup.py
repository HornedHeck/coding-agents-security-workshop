"""``ws setup`` — host preflight, and ``ws setup --image`` — the container gate."""

from __future__ import annotations

import datetime as dt
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ws import config
from ws.codemie_creds import MachineIdentity, decrypt


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def _codemie_home() -> Path:
    return Path.home() / ".codemie"


def check_docker() -> Check:
    if shutil.which("docker") is None:
        return Check("docker", False, "not on PATH")
    proc = subprocess.run(
        ["docker", "info"], capture_output=True, text=True, check=False
    )
    return Check(
        "docker",
        proc.returncode == 0,
        "running" if proc.returncode == 0 else "daemon not reachable",
    )


def check_config() -> Check:
    cfg = _codemie_home() / "codemie-cli.config.json"
    if not cfg.is_file():
        return Check(
            "codemie config", False, f"missing {cfg} — run `codemie profile login`"
        )
    return Check("codemie config", True, str(cfg))


def check_credential() -> Check:
    creds = sorted((_codemie_home() / "credentials").glob("sso-*.enc"))
    if not creds:
        return Check(
            "codemie credential",
            False,
            "no SSO credential file — run `codemie profile login`",
        )
    identity = MachineIdentity.for_host()
    try:
        payload = json.loads(decrypt(creds[0].read_text(), identity))
    except Exception as exc:  # noqa: BLE001 - decrypt failure has many causes; all mean "not usable"
        return Check(
            "codemie credential", False, f"cannot decrypt {creds[0].name}: {exc}"
        )
    expires_at = payload.get("expiresAt")
    if expires_at:
        when = dt.datetime.fromtimestamp(expires_at / 1000, dt.UTC)
        if when <= dt.datetime.now(dt.UTC):
            return Check("codemie credential", False, f"expired at {when.isoformat()}")
        return Check("codemie credential", True, f"valid until {when.isoformat()}")
    return Check("codemie credential", True, "present (no expiry recorded)")


def check_image() -> Check:
    # `docker image inspect <name>` (no tag) can fail against a containerd-store
    # manifest list that resolves fine with an explicit `:latest`.
    for ref in (config.HARNESS_IMAGE, f"{config.HARNESS_IMAGE}:latest"):
        proc = subprocess.run(
            ["docker", "image", "inspect", ref],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return Check("harness image", True, config.HARNESS_IMAGE)
    return Check("harness image", False, "not built — run `uv run ws image`")


def build_image() -> int:
    docker = check_docker()
    if not docker.ok:
        print(f"[FAIL] {docker.name}: {docker.detail}")
        return 1

    base_command = [
        "docker",
        "build",
        "--platform",
        config.linux_platform(),
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
    ]
    base = subprocess.run(base_command, cwd=config.REPO_ROOT, check=False)
    if base.returncode != 0:
        return base.returncode

    harness_command = [
        "docker",
        "build",
        "--platform",
        config.linux_platform(),
        "-t",
        config.HARNESS_IMAGE,
        "-f",
        str(config.HARNESS_DOCKERFILE),
        ".",
    ]
    return subprocess.run(harness_command, cwd=config.REPO_ROOT, check=False).returncode


def run_host_checks() -> list[Check]:
    return [check_docker(), check_config(), check_credential(), check_image()]


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="ws setup")
    parser.add_argument(
        "--image", action="store_true", help="also run the in-container gate"
    )
    args = parser.parse_args(argv)

    checks = run_host_checks()
    failed = False
    for c in checks:
        mark = "ok  " if c.ok else "FAIL"
        if not c.ok:
            failed = True
        print(f"[{mark}] {c.name}: {c.detail}")

    if failed:
        return 1
    if args.image:
        from ws.launcher import run_acceptance

        return run_acceptance()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
