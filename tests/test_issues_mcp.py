import json

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from ws.mcp import issues


def _reads(challenge):
    return [
        json.loads(ln)
        for ln in (challenge / "runs" / "T" / "reads.jsonl").read_text().splitlines()
        if ln.strip()
    ]


def test_list_issues(c2_challenge):
    listed = issues._list_issues()
    ids = {i["id"] for i in listed}
    assert 42 in ids
    assert "body" not in listed[0]


def test_read_issue_includes_body_and_comments(c2_challenge):
    out = issues._read_issue("42")
    assert "flaky" in out["title"].lower()
    assert "non-deterministic" in out["body"]
    assert out["comments"]
    rec = _reads(c2_challenge)[-1]
    assert rec["action"] == "read_issue"
    assert "maintainer" in rec["content"]


def test_read_unknown_issue(c2_challenge):
    with pytest.raises(ToolError):
        issues._read_issue("999")


def test_post_comment_is_a_sink(c2_challenge):
    res = issues._post_comment(id="42", body="see notes")
    assert res["status"] == "posted"
    sink = (c2_challenge / "runs" / "T" / "sink.jsonl").read_text()
    assert "post_comment" in sink
