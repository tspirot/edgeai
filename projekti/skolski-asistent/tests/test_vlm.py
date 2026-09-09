import numpy as np

from asistent.vlm.base import build_prompt
from asistent.vlm.dummy_backend import DummyVlm


def _slika(v=128):
    return np.full((48, 64, 3), v, dtype=np.uint8)


def test_dummy_vlm_deterministic_and_mentions_question():
    vlm = DummyVlm()
    q = "Шта показује ова шема?"
    a1 = vlm.answer(_slika(), q)
    a2 = vlm.answer(_slika(), q)
    assert a1.text == a2.text
    assert q in a1.text
    assert a1.used_context == []


def test_dummy_vlm_uses_context():
    vlm = DummyVlm()
    ctx = ["Ом-ов закон: U = I * R."]
    a = vlm.answer(_slika(), "објасни", context=ctx)
    assert a.used_context == ctx
    assert "исеч" in a.text.lower()


def test_dummy_vlm_brightness_label():
    vlm = DummyVlm()
    assert "тамна" in vlm.answer(_slika(10), "?").text
    assert "светла" in vlm.answer(_slika(240), "?").text


def test_build_prompt_orders_sections():
    p = build_prompt("СИСТЕМ", "питање?", ["материјал један"])
    assert p.index("СИСТЕМ") < p.index("материјал један") < p.index("питање?")


def test_build_prompt_without_context():
    p = build_prompt("СИСТЕМ", "питање?", None)
    assert "материјал" not in p
    assert "питање?" in p
