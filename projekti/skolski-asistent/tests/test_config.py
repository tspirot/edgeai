import pytest

from asistent.config import Config, load_config


def test_defaults():
    cfg = Config()
    assert cfg.camera.index == 0
    assert cfg.asr.backend == "faster-whisper"
    assert cfg.asr.whisper.language == "sr"
    assert cfg.vlm.backend == "qwen"
    assert cfg.vlm.quantization == "int4"
    assert cfg.tts.backend == "piper"
    assert cfg.rag.enabled is False


def test_load_and_merge(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text(
        "vlm:\n  backend: dummy\n  temperature: 0.0\n"
        "rag:\n  enabled: true\n  top_k: 5\n",
        encoding="utf-8",
    )
    cfg = load_config(p)
    assert cfg.vlm.backend == "dummy"
    assert cfg.vlm.temperature == 0.0
    assert cfg.rag.enabled is True
    assert cfg.rag.top_k == 5
    assert cfg.asr.backend == "faster-whisper"  # неизмењено


def test_unknown_key_raises(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("vlm:\n  boja: plava\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(p)


def test_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nema.yaml")
