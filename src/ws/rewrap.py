"""``ws-rewrap`` — host-side: re-encrypt CodeMie SSO credentials for a container.

See ``ws.codemie_creds`` for the crypto. The launcher re-wraps automatically
per run; this CLI is for a manual ``docker run``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from ws.codemie_creds import MachineIdentity, rewrap
from ws.config import CONTAINER_HOSTNAME as _DEFAULT_CONTAINER_HOSTNAME


def _format_expiry(expires_at_ms: int | None) -> str:
    if not expires_at_ms:
        return "unknown"
    when = dt.datetime.fromtimestamp(expires_at_ms / 1000, dt.UTC)
    remaining = when - dt.datetime.now(dt.UTC)
    return f"{when.isoformat()} ({remaining} from now)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=Path.home() / ".codemie")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--container-hostname", default=_DEFAULT_CONTAINER_HOSTNAME)
    parser.add_argument(
        "--container-arch",
        default="arm64",
        choices=["arm64", "x64"],
        help="Node os.arch() the container will report (linux/arm64 -> arm64)",
    )
    args = parser.parse_args(argv)

    source = MachineIdentity.for_host()
    target = MachineIdentity(args.container_hostname, "linux", args.container_arch)

    try:
        summaries = rewrap(args.src, args.out, source, target)
    except (FileNotFoundError, ValueError) as exc:
        print(f"rewrap failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"source identity : {source.hostname} / {source.node_platform} / {source.node_arch}"
    )
    print(
        f"target identity : {target.hostname} / {target.node_platform} / {target.node_arch}"
    )
    print(f"written to      : {args.out}")
    for item in summaries:
        print(
            f"  {item['file']}: cookies={item['cookies']} "
            f"apiUrl={item['apiUrl']} expires={_format_expiry(item['expiresAt'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
