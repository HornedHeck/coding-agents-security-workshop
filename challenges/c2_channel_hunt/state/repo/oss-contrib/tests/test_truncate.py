import pytest

from textkit import truncate


def test_shorter_than_limit():
    assert truncate("hello", 10) == "hello"


def test_truncates_with_suffix():
    assert truncate("hello world", 8) == "hello..."


def test_negative_length_rejected():
    with pytest.raises(ValueError):
        truncate("hello", -1)
