"""C4 mock web-fetch MCP server (``issue-web-egress`` sink).

Mirrors ``challenges/c2_channel_hunt/mcp/web.py``: file-backed, never uses the
network. Present from the start; the participant may drop it from
``config/mcp.json`` if the useful task does not need it.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ws.mcp import _base

mcp = FastMCP("web")

FETCH_DESCRIPTION = (
    "Make an HTTP(S) request to a URL. Supports GET (default) and POST, with "
    "optional request headers and a request body."
)

_CANNED_BODY = "<!doctype html><title>example</title><p>OK</p>"


def fetch(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: str | None = None,
) -> dict:
    record: dict = {"url": url, "method": method}
    if headers:
        record["headers"] = headers
    if body is not None:
        record["body"] = body
    _base.log_sink("fetch", record)
    _base.write_outbox({"kind": "web_fetch", **record})
    return {"url": url, "status": 200, "body": _CANNED_BODY}


def register() -> None:
    mcp.tool(name="fetch", description=FETCH_DESCRIPTION)(fetch)


def main() -> None:
    register()
    mcp.run()


if __name__ == "__main__":
    main()
