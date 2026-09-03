"""``ws-mcp-issues`` — mock issue-tracker MCP for challenge c2.

Tools: ``list_issues``, ``read_issue`` (returns the body and any comments —
every read is logged with its content for channel attribution),
``post_comment`` (the side-effect sink).

Issues are file-backed from ``state/issues/*.json`` (``{id, title, state,
body, comments: [{author, body}]}``).
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from ws.mcp import _base

mcp = FastMCP("issues")

_LIST_DESC = "List the open issues: id, title and state."
_READ_DESC = "Read one issue by id, returning its body and all comments."
_COMMENT_DESC = "Post a comment on an issue."


def _list_issues() -> list[dict]:
    issues = [
        {"id": i["id"], "title": i["title"], "state": i.get("state", "open")}
        for i in _base.load_issues()
    ]
    _base.log_read("list_issues", {}, f"{len(issues)} issues")
    return issues


def _read_issue(id: str) -> dict:
    match = next((i for i in _base.load_issues() if str(i["id"]) == str(id)), None)
    if match is None:
        raise ToolError(f"no issue with id {id!r}")

    comments = match.get("comments", [])
    rendered = "\n\n".join(
        [
            match["body"],
            *(f"[comment by {c.get('author', '?')}]\n{c['body']}" for c in comments),
        ]
    )
    _base.log_read(
        "read_issue",
        {"id": id},
        f"title={match['title']!r}, {len(comments)} comments",
        content=rendered,
    )
    return {
        "id": match["id"],
        "title": match["title"],
        "state": match.get("state", "open"),
        "body": match["body"],
        "comments": comments,
    }


def _post_comment(id: str, body: str) -> dict:
    record = {"id": id, "body": body}
    _base.log_sink("post_comment", record)
    stamp = _base.write_outbox({"kind": "issue_comment", **record})
    return {"status": "posted", "id": stamp, "issue": id}


def _register() -> None:
    mcp.tool(name="list_issues", description=_LIST_DESC)(_list_issues)
    mcp.tool(name="read_issue", description=_READ_DESC)(_read_issue)
    mcp.tool(name="post_comment", description=_COMMENT_DESC)(_post_comment)


def main() -> None:
    _register()
    mcp.run()


if __name__ == "__main__":
    main()
