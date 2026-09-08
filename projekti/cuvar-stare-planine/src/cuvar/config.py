"""Конфигурација (YAML). Све има подразумеване вредности."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class CameraConfig:
    source: str = "0"       # "0" камера, путања видеа, или "sim"
    width: int = 1280
    height: int = 720
    fps: float = 10.0


@dataclass
class TriggerConfig:
    change_fraction: float = 0.02   # удео измењених пиксела за окидач
    pixel_delta: int = 25           # разлика по каналу која се броји као „измена"
    cooldown_s: float = 8.0         # најкраће време између два окидача
    warmup_frames: int = 5          # колико кадрова за учење позадине


@dataclass
class ClassifyConfig:
    backend: str = "imx500"         # imx500 | onnx | dummy
    model: str = "models/vrste.rpk"
    min_score: float = 0.55
    labels: tuple = ("srna", "divlja svinja", "lisica", "zec", "vuk", "medved", "ptica")


@dataclass
class ClimateConfig:
    backend: str = "bme688"         # bme688 | dummy
    i2c_address: int = 0x77


@dataclass
class StorageConfig:
    dir: str = "snimci"
    keep_last: int = 500            # максимум сачуваних кадрова (ротација)
    save_images: bool = True


@dataclass
class PowerConfig:
    battery_wh: float = 77.0        # нпр. 3× 18650 (≈ 7700 mAh @ 3.7 V у Wh за пакет)
    active_w: float = 2.4
    sleep_w: float = 0.35


@dataclass
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    trigger: TriggerConfig = field(default_factory=TriggerConfig)
    classify: ClassifyConfig = field(default_factory=ClassifyConfig)
    climate: ClimateConfig = field(default_factory=ClimateConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    power: PowerConfig = field(default_factory=PowerConfig)
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
