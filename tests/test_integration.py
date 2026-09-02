"""Real end-to-end run. Needs Docker, a valid CodeMie credential and the
ws-harness image. Excluded from `make test`; run with `make test-integration`.
"""

import pytest

from ws import verdict
from ws.launcher import run_challenge


@pytest.mark.integration
def test_c1_l1_end_to_end():
    run_dir = run_challenge("c1_email", 1)
    assert (run_dir / "stream.jsonl").is_file()
    assert (run_dir / "reads.jsonl").is_file()
    # a verdict is always produced (captured or not)
    assert verdict.render(run_dir) == 0


@pytest.mark.integration
def test_c1_l1_clean_run_not_captured():
    run_dir = run_challenge("c1_email", 1, inject=False)
    assert not (run_dir / "verdict.json").is_file()
