"""Учитавање и провера конфигурације (YAML).

Све опције имају разумне подразумеване вредности, па програм ради и без
конфигурационог фајла. `config.yaml` мења само оно што треба.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class CameraConfig:
    backend: str = "auto"      # auto | picamera2 | opencv | dummy
    index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 15


@dataclass
class PoseConfig:
    backend: str = "auto"      # auto | mediapipe | dummy
    min_visibility: float = 0.5   # тачка испод ове видљивости се игнорише
    side: str = "auto"         # auto | left | right — која страна тела је ка камери
    smoothing: float = 0.4     # 0 = без изглађивања, ~0.4 умерено (EMA)


@dataclass
class PostureConfig:
    neck_threshold_deg: float = 12.0   # одступање угла врата од референце
    trunk_threshold_deg: float = 10.0  # одступање угла трупа од референце
    clear_margin_deg: float = 4.0      # хистереза: колико испод прага да се „очисти“
    bad_after_s: float = 3.0           # колико лош положај траје пре него што се броји
    alert_after_s: float = 20.0        # колико укупне погрбљености пре подсетника
    alert_cooldown_s: float = 60.0     # најмањи размак између два подсетника


@dataclass
class FeedbackConfig:
    backend: str = "auto"      # auto | gpio | console | none
    led_pin: int = 17
    buzzer_pin: int = 18
    buzzer: bool = False       # тон уз светло
    blink_s: float = 4.0       # колико траје подсетник


@dataclass
class ScreeningConfig:
    enabled: bool = False
    log_path: str = "data/skrining.csv"
    asymmetry_flag_deg: float = 3.0   # изнад ове разлике рамена/кукова — обележи у извештају


@dataclass
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    pose: PoseConfig = field(default_factory=PoseConfig)
    posture: PostureConfig = field(default_factory=PostureConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    screening: ScreeningConfig = field(default_factory=ScreeningConfig)
    reference_path: str = "data/referenca.json"   # лична калибрација
    log_path: str = "data/drzanje.csv"
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
