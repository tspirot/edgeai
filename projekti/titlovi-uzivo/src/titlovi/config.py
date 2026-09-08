"""Учитавање и провера конфигурације (YAML).

Све опције имају разумне подразумеване вредности, па програм ради и без
конфигурационог фајла. Фајл `config.yaml` само мења оно што треба.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:  # PyYAML је обавезан за учитавање фајла, али не и за подразумеване вредности
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class AudioConfig:
    device: object = None          # индекс (int) или назив (str) улаза; None = подразумевани
    samplerate: int = 16000        # Whisper и Vosk раде на 16 kHz
    block_ms: int = 100            # величина блока који стиже са микрофона
    channels: int = 1


@dataclass
class WhisperConfig:
    model: str = "base"            # tiny/base за Raspberry Pi, small+ за јачи рачунар
    device: str = "cpu"            # "cpu" или "cuda"
    compute_type: str = "int8"     # int8 је најбржи на ARM процесору
    beam_size: int = 1
    language: str = "sr"
    download_root: str = "models/faster-whisper"
    window_seconds: float = 12.0   # колико уназад Whisper "слуша" пре потврде
    step_seconds: float = 1.5      # на колико секунди се покреће препознавање
    silence_seconds: float = 0.7   # тишина после које се реченица закључује
    energy_threshold: float = 0.010  # RMS праг говор/тишина на опсегу [-1, 1]


@dataclass
class VoskConfig:
    model_path: str = "models/vosk"
    # Vosk нема званичан модел за српски (проверено 08.09.2026). Ова опција
    # постоји за друге језике на радионицама (нпр. руски, украјински) и за
    # случај да се појави модел заједнице за српски.


@dataclass
class AsrConfig:
    backend: str = "faster-whisper"   # faster-whisper | vosk | dummy
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    vosk: VoskConfig = field(default_factory=VoskConfig)


@dataclass
class TextConfig:
    script: str = "cyrillic"   # cyrillic | latin | as-is
    max_chars: int = 240       # колико текста се памти за приказ


@dataclass
class DisplayConfig:
    backend: str = "pygame"    # pygame | web | console
    fullscreen: bool = True
    width: int = 1280
    height: int = 720
    font_path: object = None   # путања до .ttf; None = уграђени фонт
    font_size: int = 56
    lines: int = 3
    margin: int = 64
    fg: str = "#FFFFFF"
    dim: str = "#8A8A8A"
    bg: str = "#000000"
    badge: bool = True         # ознака "ЛОКАЛНО · БЕЗ ОБЛАКА"
    # само за backend = "web"
    host: str = "0.0.0.0"
    port: int = 8080
    open_browser: bool = False


@dataclass
class Config:
    audio: AudioConfig = field(default_factory=AudioConfig)
    asr: AsrConfig = field(default_factory=AsrConfig)
    text: TextConfig = field(default_factory=TextConfig)
    display: DisplayConfig = field(default_factory=DisplayConfig)
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
