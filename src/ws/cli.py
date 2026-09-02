"""``ws`` — the workshop CLI (challenge commands only; dev commands live in the Makefile)."""

from __future__ import annotations

import argparse

from ws import config, setup, verdict
from ws.launcher import run_challenge

_CHALLENGE_ALIASES = {"c1": "c1_email"}


def _cmd_run(args: argparse.Namespace) -> int:
    checks = setup.run_host_checks()
    for c in checks:
        if not c.ok:
            print(f"[FAIL] {c.name}: {c.detail}")
            return 1
    challenge = _CHALLENGE_ALIASES.get(args.challenge, args.challenge)
    run_dir = run_challenge(
        challenge,
        args.level,
        model=args.model,
        inject=not args.no_inject,
    )
    return verdict.render(run_dir)


def _cmd_setup(args: argparse.Namespace) -> int:
    return setup.main(["--image"] if args.image else [])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ws")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run a challenge")
    run.add_argument("challenge")
    run.add_argument("--level", type=int, default=1)
    run.add_argument("--model", default=config.DEFAULT_MODEL)
    run.add_argument(
        "--no-inject", action="store_true", help="disable the injection (clean run)"
    )
    run.set_defaults(func=_cmd_run)

    st = sub.add_parser("setup", help="preflight checks")
    st.add_argument(
        "--image", action="store_true", help="also run the in-container gate"
    )
    st.set_defaults(func=_cmd_setup)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
