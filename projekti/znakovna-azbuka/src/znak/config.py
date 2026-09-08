"""Конфигурација (YAML)."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class CameraConfig:
    source: str = "0"
    width: int = 1280
    height: int = 720
    fps: float = 30.0


@dataclass
class HandsConfig:
    backend: str = "mediapipe"   # mediapipe | dummy
    min_detection_conf: float = 0.6
    min_tracking_conf: float = 0.5


@dataclass
class ClassifierConfig:
    k: int = 5
    min_confidence: float = 0.55


@dataclass
class VoteConfig:
    window: int = 8
    min_count: int = 5
    min_confidence: float = 0.55


@dataclass
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    hands: HandsConfig = field(default_factory=HandsConfig)
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    vote: VoteConfig = field(default_factory=VoteConfig)
    dataset_file: str = "podaci.csv"
    model_file: str = "model.npz"
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
        raise RuntimeError("PyYAML није инсталиран")
    _apply(cfg, yaml.safe_load(p.read_text(encoding="utf-8")))
    return cfg
