import pytest

from volan.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.camera.width == 160
    assert cfg.model.backend == "tflite"
    assert cfg.lidar.cone_deg == 60.0
    assert cfg.safety.brake_mm < cfg.safety.release_mm < cfg.safety.slow_mm
    assert cfg.drive.max_throttle <= 1.0


def test_load_and_merge(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(
        "model:\n  backend: heuristic\n"
        "drive:\n  max_throttle: 0.3\n  hz: 30\n"
        "safety:\n  brake_mm: 400\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.model.backend == "heuristic"
    assert cfg.drive.max_throttle == 0.3
    assert cfg.drive.hz == 30
    assert cfg.safety.brake_mm == 400
    assert cfg.camera.width == 160  # неизмењено


def test_unknown_key_raises(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("drive:\n  boja: crvena\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nema.yaml")
