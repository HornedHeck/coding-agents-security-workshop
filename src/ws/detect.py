"""Canary matching shared by the sink hook, the verdict renderer and (later)
the L3 guard.

L1 only matches the plaintext flag or a long contiguous fragment of it.
Encoded / decrypted forms are out of scope until step 2.
"""

from __future__ import annotations

import re

from ws.config import CANARY_MIN_FRAGMENT, FLAG_PATTERN


def extract_flag(canary_block: str) -> str:
    """Pull the ``FLAG{...}`` token out of the signature block."""
    match = re.search(FLAG_PATTERN, canary_block)
    if not match:
        raise ValueError("no FLAG{...} token in the canary block")
    return match.group(0)


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
