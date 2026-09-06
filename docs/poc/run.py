"""Host-side driver for the CodeMie credential pass-through PoC.

Builds one image and runs the in-container smoke check (``ws-poc``) under each
credential strategy, then prints a matrix:

* ``s1`` mount   — bind-mount ``~/.codemie`` read-only (negative control on
  macOS/Windows: the credential file is machine-key-bound).
* ``s2`` rewrap  — re-encrypt the SSO credential for the container identity,
  mount that. Primary cross-platform candidate.
* ``s3`` login   — not implemented (the SSO callback port is dynamic).

Run from the repository root:  ``uv run python poc/run.py --strategy s2``
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
_IMAGE = "ws-poc"
_CONTAINER_HOSTNAME = "ws-poc"
_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_STRATEGIES = ("s1", "s2")


def _docker_arch() -> str:
    return "arm64" if platform.machine().lower() in {"arm64", "aarch64"} else "x64"


def _linux_platform() -> str:
    return "linux/arm64" if _docker_arch() == "arm64" else "linux/amd64"


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=False, **kw)


def build_image() -> bool:
    proc = _run(
        [
            "docker",
            "build",
            "--platform",
            _linux_platform(),
            "-t",
            _IMAGE,
            "-f",
            str(_REPO_ROOT / "poc" / "Dockerfile"),
            str(_REPO_ROOT),
        ]
    )
    return proc.returncode == 0


def _common_run_args(strategy: str, model: str) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "--platform",
        _linux_platform(),
        "-e",
        f"WS_POC_STRATEGY={strategy}",
        "-e",
        f"WS_POC_MODEL={model}",
    ]


def run_s1(codemie_home: Path, model: str) -> int:
    args = _common_run_args("s1", model) + [
        "--hostname",
        platform.node(),
        "-v",
        f"{codemie_home}:/home/node/.codemie:ro",
        _IMAGE,
    ]
    return _run(args).returncode


def run_s2(codemie_home: Path, model: str) -> int:
    scratch = Path(tempfile.mkdtemp(prefix="ws-poc-creds-"))
    try:
        rewrap = _run(
            [
                "uv",
                "run",
                "ws-rewrap",
                "--src",
                str(codemie_home),
                "--out",
                str(scratch),
                "--container-hostname",
                _CONTAINER_HOSTNAME,
                "--container-arch",
                _docker_arch(),
            ],
            cwd=_REPO_ROOT,
        )
        if rewrap.returncode != 0:
            return rewrap.returncode
        args = _common_run_args("s2", model) + [
            "--hostname",
            _CONTAINER_HOSTNAME,
            "-v",
            f"{scratch}:/home/node/.codemie",
            _IMAGE,
        ]
        return _run(args).returncode
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strategy", choices=[*_STRATEGIES, "all"], default="s2")
    parser.add_argument("--codemie-home", type=Path, default=Path.home() / ".codemie")
    parser.add_argument("--model", default=_DEFAULT_MODEL)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args(argv)

    if shutil.which("docker") is None:
        print("docker not found on PATH", file=sys.stderr)
        return 2

    selected = list(_STRATEGIES) if args.strategy == "all" else [args.strategy]

    if {"s1", "s2"} & set(selected):
        config = args.codemie_home / "codemie-cli.config.json"
        if not config.is_file():
            print(
                f"missing {config} — run `codemie profile login` first", file=sys.stderr
            )
            return 2

    if not args.skip_build and not build_image():
        print("image build failed", file=sys.stderr)
        return 2

    results: dict[str, int] = {}
    for strategy in selected:
        print(f"\n{'=' * 60}\n strategy {strategy}\n{'=' * 60}")
        if strategy == "s1":
            results[strategy] = run_s1(args.codemie_home, args.model)
        else:
            results[strategy] = run_s2(args.codemie_home, args.model)

    print(f"\n{'=' * 60}\n MATRIX\n{'=' * 60}")
    for strategy in selected:
        verdict = (
            "PASS" if results[strategy] == 0 else f"FAIL (exit {results[strategy]})"
        )
        print(f"  {strategy}: {verdict}")

    return 0 if any(rc == 0 for rc in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
