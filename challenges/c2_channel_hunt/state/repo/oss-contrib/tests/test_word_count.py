from textkit import word_count


def test_counts_words():
    assert word_count("one two three") == 3


def test_empty():
    assert word_count("   ") == 0
