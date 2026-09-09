"""Учитавање и провера конфигурације (YAML).

Све опције имају разумне подразумеване вредности, па програм ради и без
конфигурационог фајла. Фајл `config.yaml` само мења оно што треба.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:  # PyYAML је потребан само за учитавање фајла, не и за подразумеване вредности
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


SISTEMSKI_PROMPT = (
    "Ти си школски асистент у техничкој школи. Одговараш кратко и тачно, на "
    "српском језику, ученицима средње школе. Гледаш слику коју ти ученик "
    "покаже (радни лист, електрична шема, мерни инструмент, склоп) и питање. "
    "Ако ти је дат исечак из уџбеника, ослони се на њега и то напомени. "
    "Ако ниси сигуран, реци да ниси сигуран — немој измишљати."
)


@dataclass
class CameraConfig:
    index: int = 0             # индекс USB камере (C922 је обично 0)
    width: int = 1280
    height: int = 720
    warmup_frames: int = 5     # колико кадрова прескочити док се аутофокус смири


@dataclass
class WhisperConfig:
    model: str = "base"            # base за брз одговор, small+ за бољу тачност
    device: str = "cpu"            # "cpu" или "cuda" (Orin: "cuda")
    compute_type: str = "int8"
    language: str = "sr"
    download_root: str = "models/faster-whisper"
    silence_seconds: float = 0.8   # тишина после које се питање сматра завршеним
    energy_threshold: float = 0.010  # RMS праг говор/тишина на опсегу [-1, 1]
    max_seconds: float = 15.0      # безбедносни лимит дужине питања


@dataclass
class AsrConfig:
    backend: str = "faster-whisper"   # faster-whisper | dummy
    samplerate: int = 16000
    block_ms: int = 100
    dummy_text: str = "Шта показује ова шема?"
    whisper: WhisperConfig = field(default_factory=WhisperConfig)


@dataclass
class VlmConfig:
    backend: str = "qwen"             # qwen | dummy
    model: str = "Qwen/Qwen2-VL-2B-Instruct"
    quantization: str = "int4"       # int4 | int8 | none
    device: str = "auto"
    download_root: str = "models/vlm"
    max_new_tokens: int = 256
    temperature: float = 0.2
    system_prompt: str = SISTEMSKI_PROMPT


@dataclass
class TtsConfig:
    backend: str = "piper"           # piper | console
    voice: str = "sr_RS-serbian-medium"
    model_path: str = "models/piper"
    speak: bool = True               # изговори одговор наглас


@dataclass
class RagConfig:
    enabled: bool = False
    index_path: str = "models/rag/index.json"
    embed_backend: str = "hashing"   # hashing (без зависности) | sentence-transformers
    embed_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    dim: int = 512                   # димензија за hashing уградњу
    top_k: int = 3
    chunk_chars: int = 800
    chunk_overlap: int = 150
    min_score: float = 0.15


@dataclass
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    asr: AsrConfig = field(default_factory=AsrConfig)
    vlm: VlmConfig = field(default_factory=VlmConfig)
    tts: TtsConfig = field(default_factory=TtsConfig)
    rag: RagConfig = field(default_factory=RagConfig)
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
    """Врати `Config` спојен из подразумеваних вредности и (по избору) YAML фајла."""
    cfg = Config()
    if path is None:
        return cfg
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Конфигурациони фајл не постоји: {p}")
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML није инсталиран — `pip install pyyaml`")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    _apply(cfg, data)
    return cfg
