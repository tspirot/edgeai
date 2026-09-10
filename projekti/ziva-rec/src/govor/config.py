"""Учитавање и провера конфигурације (YAML). Ради и без фајла."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class AudioConfig:
    uredjaj: "int | None" = None      # индекс микрофона; None = подразумевани
    samplerate: int = 16000
    kanali: int = 1
    tisina_s: float = 1.2             # тишина после које се исказ сматра готовим
    prag_energije: float = 0.012      # RMS праг говор/тишина на [-1, 1]
    maks_s: float = 600.0             # безбедносни лимит дужине снимка


@dataclass
class AsrConfig:
    backend: str = "faster-whisper"   # faster-whisper | dummy
    model: str = "large-v3-turbo"
    model_dir: str = ""               # локалне дообучене тежине, ако постоје
    download_root: str = "models/whisper"
    device: str = "cuda"              # Jetson: cuda
    compute_type: str = "int8"
    language: str = "sr"
    beam_size: int = 5
    vad_filter: bool = True


@dataclass
class KorpusConfig:
    koren: str = "korpus"
    min_skor_za_isticanje: float = 0.35   # изнад овога: „вреди сачувати“
    min_trajanje_s: float = 1.0           # краће од овога не иде у корпус


@dataclass
class Config:
    audio: AudioConfig = field(default_factory=AudioConfig)
    asr: AsrConfig = field(default_factory=AsrConfig)
    korpus: KorpusConfig = field(default_factory=KorpusConfig)
    recnik: str = ""                       # празно = речник уз пакет
    log_level: str = "INFO"


def _apply(obj, data) -> None:
    if data is None:
        return
    if not isinstance(data, dict):
        raise ValueError(f"Очекиван је објекат, добијено: {type(data).__name__}")
    valid = {f.name for f in fields(obj)}
    for key, value in data.items():
        if key not in valid:
            raise ValueError(f"Непозната опција у конфигурацији: '{key}'")
        current = getattr(obj, key)
        if is_dataclass(current) and not isinstance(current, type):
            _apply(current, value)
        else:
            setattr(obj, key, value)


def load_config(path: "str | Path | None" = None) -> Config:
    cfg = Config()
    if path is None:
        return cfg
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Конфигурациони фајл не постоји: {p}")
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML није инсталиран — `pip install pyyaml`")
    _apply(cfg, yaml.safe_load(p.read_text(encoding="utf-8")))
    return cfg
