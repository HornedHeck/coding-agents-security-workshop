import pytest

from textkit import truncate


def test_shorter_than_limit():
    assert truncate("hello", 10) == "hello"


def test_truncates_with_suffix():
    assert truncate("hello world", 8) == "hello..."


def test_negative_length_rejected():
    with pytest.raises(ValueError):
        truncate("hello", -1)


def test_never_exceeds_requested_length():
    # issue #1: for a length shorter than the suffix, the current
    # implementation still appends the full suffix, so the result exceeds
    # the requested length.
    for length in range(0, len("...")):
        assert len(truncate("hello world", length)) <= length
