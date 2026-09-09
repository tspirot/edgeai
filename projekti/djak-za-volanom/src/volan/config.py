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
    backend: str = "auto"       # auto | picamera2 | opencv | dummy
    index: int = 0              # за opencv
    width: int = 160
    height: int = 120
    fps: int = 30


@dataclass
class ModelConfig:
    backend: str = "tflite"     # tflite | heuristic | dummy
    path: str = "models/pilot.tflite"
    input_width: int = 160
    input_height: int = 120
    predicts_throttle: bool = False   # True ако модел даје и гас, иначе фиксни гас
    cruise_throttle: float = 0.35     # гас када модел не предвиђа гас (0–1)


@dataclass
class LidarConfig:
    backend: str = "auto"       # auto | rplidar | dummy
    port: str = "/dev/ttyUSB0"
    cone_deg: float = 60.0      # ширина конуса испред аута (укупно) за проверу препрека
    forward_offset_deg: float = 0.0   # где је „напред“ на лидару (0 = 0°)
    min_valid_mm: float = 120.0       # ближе од овога = шум/само возило, игнорише се
    max_range_mm: float = 4000.0


@dataclass
class SafetyConfig:
    brake_mm: float = 550.0     # испод овог растојања — кочи (гас на 0)
    release_mm: float = 800.0   # изнад овог — пусти (хистереза, да не трепери)
    slow_mm: float = 1200.0     # између brake и slow — ограничи гас
    slow_factor: float = 0.5    # колико смањити гас у зони успоравања
    stale_scan_s: float = 0.4   # ако нема свежег скена дуже од овога — кочи


@dataclass
class DriveConfig:
    hz: float = 20.0            # петља одлучивања
    max_throttle: float = 0.45  # тврди лимит гаса, за почетак низак
    steer_trim: float = 0.0     # механичка корекција центра волана (−1..1)
    steer_gain: float = 1.0     # појачање излаза модела на волан
    invert_steer: bool = False


@dataclass
class ActuatorConfig:
    backend: str = "auto"      # auto | pca9685 | dummy
    steer_channel: int = 0
    throttle_channel: int = 1
    steer_left_us: int = 1000
    steer_center_us: int = 1500
    steer_right_us: int = 2000
    throttle_stop_us: int = 1500
    throttle_full_us: int = 2000
    throttle_reverse_us: int = 1000


@dataclass
class RecordConfig:
    out_dir: str = "data"
    jpg_quality: int = 90


@dataclass
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    lidar: LidarConfig = field(default_factory=LidarConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    drive: DriveConfig = field(default_factory=DriveConfig)
    actuator: ActuatorConfig = field(default_factory=ActuatorConfig)
    record: RecordConfig = field(default_factory=RecordConfig)
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
