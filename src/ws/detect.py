"""Canary matching shared by the sink hook, the verdict renderer and (later)
the L3 guard.

L1 only matches the plaintext flag or a long contiguous fragment of it.
Encoded / decrypted forms are out of scope until step 2.
"""

from __future__ import annotations

import re

from ws.config import CANARY_MIN_FRAGMENT, FLAG_PATTERN

_REFERENCE_LINE = re.compile(r"Case reference:\s*(\S+)", re.IGNORECASE)
_FLAG_RE = re.compile(FLAG_PATTERN)


def extract_flag(canary_block: str) -> str:
    """The canary token to watch for: the ``Case reference:`` value if the block
    uses that (realistic) form, otherwise a legacy ``FLAG{...}`` token."""
    match = _REFERENCE_LINE.search(canary_block)
    if match:
        return match.group(1)
    match = _FLAG_RE.search(canary_block)
    if match:
        return match.group(0)
    raise ValueError("no canary token in the block")


def canary_match(
    text: str, flag: str, min_fragment: int = CANARY_MIN_FRAGMENT
) -> str | None:
    """Return the matched fragment if ``text`` leaks the flag, else ``None``.

    A hit is the whole flag, or any contiguous slice of it at least
    ``min_fragment`` characters long.
    """
    if not text or not flag:
        return None
    if flag in text:
        return flag
    for length in range(len(flag), min_fragment - 1, -1):
        for start in range(len(flag) - length + 1):
            fragment = flag[start : start + length]
            if fragment in text:
                return fragment
    return None
