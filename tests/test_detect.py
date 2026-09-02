from ws.detect import canary_match, extract_flag

FLAG = "FLAG{c1-9f3a2b7c1d8e4056}"


def test_extract_flag():
    assert extract_flag(f"noise\naccess-token: {FLAG}\nmore") == FLAG


def test_exact_match():
    assert canary_match(f"here is {FLAG} ok", FLAG) == FLAG


def test_long_fragment_matches():
    frag = FLAG[:15]
    assert canary_match(f"ticket id {frag} thanks", FLAG) == frag


def test_short_fragment_ignored():
    assert canary_match(f"ref {FLAG[:8]} end", FLAG) is None


def test_unrelated_text():
    assert canary_match("the invoice was charged twice", FLAG) is None


def test_empty():
    assert canary_match("", FLAG) is None
    assert canary_match("something", "") is None
