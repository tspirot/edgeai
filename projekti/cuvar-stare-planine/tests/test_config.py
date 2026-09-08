import pytest

from cuvar.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.camera.fps == 10.0
    assert cfg.classify.backend == "imx500"
    assert cfg.trigger.change_fraction == 0.02


def test_merge(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(
        "camera:\n  source: sim\nclassify:\n  backend: dummy\n  min_score: 0.7\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.camera.source == "sim"
    assert cfg.classify.backend == "dummy"
    assert cfg.classify.min_score == 0.7
    assert cfg.power.battery_wh == 77.0


def test_unknown_key(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("trigger:\n  boja: 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)
