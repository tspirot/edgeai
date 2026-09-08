import pytest

from qc.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.features.backend == "handcrafted"
    assert cfg.features.grid == 8
    assert cfg.threshold.method == "sigma"


def test_merge(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(
        "features:\n  grid: 12\nthreshold:\n  method: percentile\n  percentile: 97.5\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.features.grid == 12
    assert cfg.threshold.method == "percentile"
    assert cfg.threshold.percentile == 97.5
    assert cfg.features.image_size == 256


def test_unknown_key(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("bank:\n  velicina: 5\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)
