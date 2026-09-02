"""``ws-mcp-email`` — mock email MCP for challenge c1.

Tools: ``list_emails``, ``read_email`` (reads inject the "internal signature"
canary), ``send_email`` (the side-effect sink — always succeeds; capture
detection happens out of band in the PreToolUse hook).
"""

from __future__ import annotations

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from ws.mcp import _base

mcp = MCPServer("email")


def _list_emails() -> list[dict]:
    emails = [
        {"id": e["id"], "from": e["from"], "subject": e["subject"], "date": e["date"]}
        for e in _base.load_inbox()
    ]
    _base.log_read("list_emails", {}, f"{len(emails)} emails")
    return emails


def _read_email(id: str) -> dict:
    match = next((e for e in _base.load_inbox() if e["id"] == id), None)
    if match is None:
        raise ToolError(f"no email with id {id!r}")

    body = match["body"]
    if match.get("injection") and _base.inject_enabled():
        body = f"{body}\n\n{match['injection']}"
    body = f"{body}\n\n{_base.canary_block()}"

    _base.log_read("read_email", {"id": id}, f"subject={match['subject']!r}")
    return {
        "id": match["id"],
        "from": match["from"],
        "to": match.get("to", ""),
        "subject": match["subject"],
        "date": match["date"],
        "body": body,
    }


def _send_email(to: str, subject: str, body: str, cc: str = "") -> dict:
    message = {"to": to, "cc": cc, "subject": subject, "body": body}
    _base.log_sink("send_email", message)
    stamp = _base.write_outbox(message)
    return {"status": "sent", "id": stamp, "to": to}


@mcp.tool()
def list_emails() -> list[dict]:
    """List the inbox: id, sender, subject and date for every email."""
    return _list_emails()


@mcp.tool()
def read_email(id: str) -> dict:
    """Read one email by id, returning the full body."""
    return _read_email(id)


@mcp.tool()
def send_email(to: str, subject: str, body: str, cc: str = "") -> dict:
    """Send an email. `to` and `cc` are comma-separated address lists."""
    return _send_email(to=to, subject=subject, body=body, cc=cc)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
