import pytest

from znak.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.hands.backend == "mediapipe"
    assert cfg.classifier.k == 5
    assert cfg.vote.min_count == 5


def test_merge(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(
        "hands:\n  backend: dummy\nclassifier:\n  k: 3\nvote:\n  window: 12\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.hands.backend == "dummy"
    assert cfg.classifier.k == 3
    assert cfg.vote.window == 12
    assert cfg.camera.fps == 30.0


def test_unknown_key(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("vote:\n  brzina: 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)
