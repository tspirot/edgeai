import pytest

from mapa.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.grid.res_m == 0.05
    assert cfg.icp.max_iter == 20
    assert cfg.slam.keyframes == 6
    assert cfg.pursuit.lookahead_m > 0


def test_load_and_merge(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text(
        "grid:\n  res_m: 0.1\n  size_m: 10\n"
        "pursuit:\n  cruise_speed: 0.2\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.grid.res_m == 0.1
    assert cfg.grid.size_m == 10
    assert cfg.pursuit.cruise_speed == 0.2
    assert cfg.icp.max_pairs_dist == 0.5  # неизмењено


def test_unknown_key_raises(tmp_path):
    p = tmp_path / "b.yaml"
    p.write_text("grid:\n  boja: siva\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nema.yaml")
