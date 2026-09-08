"""Конфигурација (YAML)."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class FeaturesConfig:
    backend: str = "handcrafted"   # handcrafted | torch | dummy
    image_size: int = 256
    grid: int = 8                  # G×G блокова по слици
    torch_model: str = "resnet18"


@dataclass
class BankConfig:
    coreset_fraction: float = 1.0  # 1.0 = задржи све; <1 = greedy подскуп
    k: int = 1                     # k-НН (просек k најближих)


@dataclass
class ThresholdConfig:
    method: str = "sigma"          # sigma | percentile
    sigma_k: float = 4.0           # праг = mean + k·std OK резултата
    percentile: float = 99.0


@dataclass
class CameraConfig:
    source: str = "0"
    width: int = 640
    height: int = 480


@dataclass
class Config:
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    bank: BankConfig = field(default_factory=BankConfig)
    threshold: ThresholdConfig = field(default_factory=ThresholdConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
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
