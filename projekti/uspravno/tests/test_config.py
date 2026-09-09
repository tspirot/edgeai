import pytest

from drzanje.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.pose.backend == "auto"
    assert cfg.posture.neck_threshold_deg == 12.0
    assert cfg.posture.clear_margin_deg < cfg.posture.neck_threshold_deg
    assert cfg.screening.enabled is False


def test_load_and_merge(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(
        "pose:\n  backend: dummy\n  side: left\n"
        "posture:\n  neck_threshold_deg: 15\n  alert_after_s: 30\n"
        "screening:\n  enabled: true\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.pose.backend == "dummy"
    assert cfg.pose.side == "left"
    assert cfg.posture.neck_threshold_deg == 15
    assert cfg.posture.alert_after_s == 30
    assert cfg.screening.enabled is True
    assert cfg.camera.fps == 15  # неизмењено


def test_unknown_key_raises(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("posture:\n  boja: crvena\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nema.yaml")
