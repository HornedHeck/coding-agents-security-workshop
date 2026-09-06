"""textkit — tiny text helpers (slugs, truncation, word counts)."""

from __future__ import annotations

import re

__all__ = ["slugify", "truncate", "word_count"]

_SEPARATOR = "-"
_NON_SLUG = re.compile(r"[^a-z0-9]")


def slugify(text: str) -> str:
    """Turn arbitrary text into a URL-safe slug."""
    lowered = text.strip().lower()
    slug = _NON_SLUG.sub(_SEPARATOR, lowered)
    return slug.strip(_SEPARATOR)


def truncate(text: str, length: int, suffix: str = "...") -> str:
    """Truncate text to at most `length` characters, appending `suffix`."""
    if length < 0:
        raise ValueError("length must be non-negative")
    if len(text) <= length:
        return text
    return text[: max(0, length - len(suffix))] + suffix


def word_count(text: str) -> int:
    """Count whitespace-separated words."""
    return len(text.split())
