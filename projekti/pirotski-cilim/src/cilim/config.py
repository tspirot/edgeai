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


UPUT = (
    "шара у духу пиротског ћилима, симетрична геометријска орнаментика, "
    "црвена преовлађује, равне површине боје без прелаза, бордура око поља"
)

NE_ZELIM = (
    "фотографија, сенке, меки прелази, перспектива, потпис, текст, "
    "тродимензионални приказ, косе линије"
)


@dataclass
class CameraConfig:
    index: int = 0
    width: int = 1280
    height: int = 720
    warmup_frames: int = 5     # колико кадрова прескочити док се аутофокус смири


@dataclass
class PravilaConfig:
    """Правила заната — види `cilim/pravila.py`."""

    spoljasnji_cenar: float = 0.04    # удео половине краће странице
    bordura: float = 0.14
    unutrasnji_cenar: float = 0.05
    ogledalo_uspravno: bool = True
    ogledalo_vodoravno: bool = True
    min_niti: int = 3                 # најкраћи потез који разбој још изводи


@dataclass
class KartonConfig:
    redova: int = 64
    kolona: int = 48
    niti_po_celiji: int = 2
    piksela_po_celiji: int = 12       # само за PNG за штампу


@dataclass
class KlasifikatorConfig:
    backend: str = "vit"              # vit | dummy
    model: str = "vit_small_patch16_224"
    tezine: str = "models/klasifikator/sare.pt"
    device: str = "auto"
    velicina: int = 224
    min_pouzdanost: float = 0.45      # испод овога: „нисам сигуран“


@dataclass
class GeneratorConfig:
    backend: str = "difuzija"         # difuzija | pravila
    model: str = "runwayml/stable-diffusion-v1-5"
    controlnet: str = "lllyasviel/sd-controlnet-scribble"
    lora: str = "models/generator/cilim-lora"
    download_root: str = "models/generator"
    device: str = "auto"
    velicina: int = 512
    koraka: int = 20
    jacina_skice: float = 0.9         # колико ControlNet држи скицу
    uput: str = UPUT
    ne_zelim: str = NE_ZELIM


@dataclass
class Config:
    camera: CameraConfig = field(default_factory=CameraConfig)
    pravila: PravilaConfig = field(default_factory=PravilaConfig)
    karton: KartonConfig = field(default_factory=KartonConfig)
    klasifikator: KlasifikatorConfig = field(default_factory=KlasifikatorConfig)
    generator: GeneratorConfig = field(default_factory=GeneratorConfig)
    katalog: str = ""                 # празно = каталог који долази уз пакет
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
    _apply(cfg, yaml.safe_load(p.read_text(encoding="utf-8")))
    return cfg
