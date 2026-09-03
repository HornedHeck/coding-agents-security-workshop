"""``ws`` — the workshop CLI (challenge commands only; dev commands live in the Makefile)."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor

from ws import config, setup, verdict
from ws.launcher import next_attempt, run_challenge, sanitize_keyword

_CHALLENGE_ALIASES = {"c1": "c1_email", "c2": "c2_channel_hunt"}


def _cmd_run(args: argparse.Namespace) -> int:
    checks = setup.run_host_checks()
    for c in checks:
        if not c.ok:
            print(f"[FAIL] {c.name}: {c.detail}")
            return 1
    challenge = _CHALLENGE_ALIASES.get(args.challenge, args.challenge)
    spec = config.challenge_spec(challenge)
    runs = args.runs if args.runs is not None else spec.default_runs

    attempt = next_attempt(config.challenge_dir(challenge))
    keyword = sanitize_keyword(args.keyword)
    run_names = [f"{attempt:02d}.{i:02d}_{keyword}" for i in range(runs)]

    def _run(name: str):
        return run_challenge(
            challenge,
            args.level,
            model=args.model,
            inject=not args.no_inject,
            agent=args.agent,
            run_name=name,
        )

    with ThreadPoolExecutor(max_workers=runs) as pool:
        run_dirs = list(pool.map(_run, run_names))
    if len(run_dirs) == 1:
        return verdict.render(run_dirs[0])
    return verdict.aggregate(run_dirs)


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
        "--runs",
        type=int,
        default=None,
        help="repeat the attempt N times and aggregate (default: per-challenge)",
    )
    run.add_argument(
        "--no-inject", action="store_true", help="disable the injection (clean run)"
    )
    run.add_argument(
        "--agent",
        choices=(config.AGENT_CLAUDE, config.AGENT_COPILOT),
        default=None,
        help="victim agent CLI (default: per-challenge, else copilot)",
    )
    run.add_argument(
        "--keyword",
        default=None,
        help="name postfix for the run dirs, alphanumeric only, max 10 chars "
        "(default: random)",
    )
    run.set_defaults(func=_cmd_run)

    c2_clean = sub.add_parser("c2-clean", help="run one clean C2 attempt")
    c2_clean.set_defaults(
        func=_cmd_run,
        challenge="c2",
        level=1,
        model=config.DEFAULT_MODEL,
        runs=1,
        no_inject=True,
        agent=None,
        keyword=None,
    )

    c2_dirty = sub.add_parser("c2-dirty", help="run five injected C2 attempts")
    c2_dirty.set_defaults(
        func=_cmd_run,
        challenge="c2",
        level=1,
        model=config.DEFAULT_MODEL,
        runs=5,
        no_inject=False,
        agent=None,
        keyword=None,
    )

    st = sub.add_parser("setup", help="preflight checks")
    st.add_argument(
        "--image", action="store_true", help="also run the in-container gate"
    )
    st.set_defaults(func=_cmd_setup)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
