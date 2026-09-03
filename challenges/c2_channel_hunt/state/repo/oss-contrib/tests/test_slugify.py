from textkit import slugify


def test_basic():
    assert slugify("Hello World") == "hello-world"


def test_strips_edges():
    assert slugify("  Hello  ") == "hello"


def test_collapses_whitespace():
    # a run of separators should collapse to a single "-"
    assert slugify("hello  world") == "hello-world"


def test_collapses_punctuation():
    assert slugify("a, b & c") == "a-b-c"
