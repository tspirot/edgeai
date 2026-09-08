import pytest

from zebra.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.video.source == "0"
    assert cfg.detect.backend == "yolo"
    assert cfg.track.min_hits == 3
    assert cfg.safety.ttc_seconds == 3.0


def test_merge(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(
        "video:\n  source: sim\ndetect:\n  backend: dummy\nsafety:\n  ttc_seconds: 1.5\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.video.source == "sim"
    assert cfg.detect.backend == "dummy"
    assert cfg.safety.ttc_seconds == 1.5
    assert cfg.track.min_hits == 3


def test_unknown_key(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("safety:\n  brzina: 10\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)
