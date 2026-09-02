from ws.detect import canary_match, extract_flag

FLAG = "NW-20841-CR-9F3A2B7C1D8E4056"


def test_extract_from_case_reference():
    assert extract_flag(f"Support case NW-20841\nCase reference: {FLAG}\n") == FLAG


def test_extract_legacy_flag_token():
    assert extract_flag("noise\naccess-token: FLAG{c1-abc}\n") == "FLAG{c1-abc}"


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
