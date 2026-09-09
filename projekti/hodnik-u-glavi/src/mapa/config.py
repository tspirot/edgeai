"""Конфигурација (YAML) са разумним подразумеваним вредностима."""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


@dataclass
class LidarConfig:
    backend: str = "auto"      # auto | rplidar | dummy
    port: str = "/dev/ttyUSB0"
    min_mm: float = 150.0      # ближе = шум / само возило
    max_mm: float = 6000.0     # даље = непоуздано
    forward_offset_deg: float = 0.0


@dataclass
class IcpConfig:
    max_iter: int = 20
    tol: float = 1e-4          # праг помака за прекид (m)
    max_pairs_dist: float = 0.5   # одбаци парове даље од овога (m)
    min_points: int = 40


@dataclass
class SlamConfig:
    keyframes: int = 6         # колико последњих скенова чини „мапу“ за ICP
    subsample: int = 1         # сваку N-ту тачку кенрефрејма чувати (1 = све)
    min_fitness: float = 0.35  # испод овог удела упарених — не помери положај


@dataclass
class GridConfig:
    res_m: float = 0.05        # величина ћелије
    size_m: float = 20.0       # страница мапе
    hit_logodds: float = 0.85
    miss_logodds: float = -0.4
    clamp: float = 6.0
    occupied_threshold: float = 0.5   # вероватноћа изнад које је ћелија препрека


@dataclass
class PlannerConfig:
    inflate_m: float = 0.25   # прошири препреке за пола ширине возила
    allow_diagonal: bool = True
    unknown_is_blocked: bool = False   # False: вози кроз непознато и препланирај док мапа расте



@dataclass
class PursuitConfig:
    lookahead_m: float = 0.5
    wheelbase_m: float = 0.16
    max_steer_rad: float = 0.5
    cruise_speed: float = 0.3
    goal_tol_m: float = 0.2


@dataclass
class Config:
    lidar: LidarConfig = field(default_factory=LidarConfig)
    icp: IcpConfig = field(default_factory=IcpConfig)
    slam: SlamConfig = field(default_factory=SlamConfig)
    grid: GridConfig = field(default_factory=GridConfig)
    planner: PlannerConfig = field(default_factory=PlannerConfig)
    pursuit: PursuitConfig = field(default_factory=PursuitConfig)
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
