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
class KameraConfig:
    index: int = 0
    sirina: int = 640
    visina: int = 480
    vfov: float = 42.0             # усправно видно поље, степени
    rastojanje: float = 300.0      # mm, од осе стола до камере
    visina_kamere: float = 220.0   # mm, изнад површине стола
    cilj: float = 60.0             # mm, висина тачке гледања на оси
    zagrevanje: int = 5            # кадрова да се аутофокус смири


@dataclass
class StoConfig:
    backend: str = "koracni"       # koracni | dummy
    pinovi: tuple = (18, 23, 24, 25)   # IN1–IN4 на ULN2003
    koraka_po_krugu: int = 4096    # 28BYJ-48 у half-step режиму
    pauza_ms: int = 300            # колико чекати да се предмет умири пре кадра
    obrnut_smer: bool = False


@dataclass
class SiluetaConfig:
    prag: float = 18.0             # разлика у сивом изнад које је предмет
    zatvaranje: int = 2
    samo_najveca: bool = True


@dataclass
class ZapreminaConfig:
    precnik: float = 160.0         # mm, радни простор око осе стола
    visina: float = 200.0          # mm
    podela: int = 160              # воксела по оси
    van_kadra_rezi: bool = True


@dataclass
class MrezaConfig:
    vrsta: str = "blokovska"       # blokovska | glatka
    naziv: str = "dvojnik"


@dataclass
class Config:
    kamera: KameraConfig = field(default_factory=KameraConfig)
    sto: StoConfig = field(default_factory=StoConfig)
    silueta: SiluetaConfig = field(default_factory=SiluetaConfig)
    zapremina: ZapreminaConfig = field(default_factory=ZapreminaConfig)
    mreza: MrezaConfig = field(default_factory=MrezaConfig)
    kadrova: int = 120             # снимака по пуном кругу (3° по кадру)
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


def kamera_iz(cfg: Config):
    """Конфигурација → `geometrija.Kamera` (иста за снимање и за симулацију)."""
    from dvojnik.geometrija import Kamera

    k = cfg.kamera
    return Kamera(
        sirina=k.sirina, visina=k.visina, vfov=k.vfov,
        rastojanje=k.rastojanje, visina_kamere=k.visina_kamere, cilj=k.cilj,
    )
