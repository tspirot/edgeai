from titlovi.display.wrap import last_lines, wrap_words


def test_wrap_basic():
    words = "ово је прилично дуга реченица за прелом".split()
    lines = wrap_words(words, max_chars=15)
    assert all(len(ln) <= 15 for ln in lines)
    assert " ".join(" ".join(lines).split()) == " ".join(words)


def test_long_word_not_lost():
    lines = wrap_words(["кратко", "супердугачкаречкојанесмедасеизгуби"], max_chars=10)
    assert "супердугачкаречкојанесмедасеизгуби" in lines


def test_last_lines():
    text = "један два три четири пет шест седам осам"
    assert last_lines(text, max_chars=9, n=2) == wrap_words(text.split(), 9)[-2:]
