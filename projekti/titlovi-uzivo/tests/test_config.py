import pytest

from titlovi.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.audio.samplerate == 16000
    assert cfg.asr.backend == "faster-whisper"
    assert cfg.text.script == "cyrillic"
    assert cfg.display.backend == "pygame"


def test_load_and_merge(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(
        "text:\n  script: latin\nasr:\n  backend: dummy\n  whisper:\n    model: small\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.text.script == "latin"
    assert cfg.asr.backend == "dummy"
    assert cfg.asr.whisper.model == "small"
    assert cfg.audio.samplerate == 16000  # неизмењено


def test_unknown_key_raises(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("text:\n  boja: crvena\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nema.yaml")
