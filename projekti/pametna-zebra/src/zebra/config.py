"""Конфигурација (YAML). Све има подразумеване вредности."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class VideoConfig:
    source: str = "0"          # индекс камере ("0"), путања фајла, или "sim"
    width: int = 1280
    height: int = 720
    fps: float = 30.0


@dataclass
class DetectConfig:
    backend: str = "yolo"      # yolo | hailo | dummy
    model: str = "yolov8n.pt"
    conf: float = 0.35         # високи праг (ByteTrack прва рунда)
    conf_low: float = 0.15     # ниски праг (ByteTrack друга рунда)
    person_labels: tuple = ("person",)
    vehicle_labels: tuple = ("car", "truck", "bus", "motorcycle", "bicycle")


@dataclass
class TrackConfig:
    max_age: int = 30          # колико кадрова траг „преживи" без детекције
    min_hits: int = 3          # колико потврда пре него што траг постане активан
    iou_match: float = 0.2


@dataclass
class SafetyConfig:
    ttc_seconds: float = 3.0        # праг: време до уласка у зону судара
    conflict_radius_m: float = 2.0  # растојање које се сматра сударом
    hold_seconds: float = 2.0       # колико упозорење остаје упаљено после окидача
    meters_per_pixel: float = 0.05  # из калибрације (zebra calibrate)


@dataclass
class ZoneConfig:
    file: str = "zones.json"   # полигони: пешачки прелаз и коловоз


@dataclass
class IOConfig:
    gpio: bool = True
    led_pin: int = 17
    log_file: str = "brojac.csv"
    log_interval_s: float = 60.0


@dataclass
class Config:
    video: VideoConfig = field(default_factory=VideoConfig)
    detect: DetectConfig = field(default_factory=DetectConfig)
    track: TrackConfig = field(default_factory=TrackConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    zone: ZoneConfig = field(default_factory=ZoneConfig)
    io: IOConfig = field(default_factory=IOConfig)
    log_level: str = "INFO"


def _apply(obj, data) -> None:
    if data is None:
        return
    if not isinstance(data, dict):
        raise ValueError(f"Очекиван објекат, добијено: {type(data).__name__}")
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
