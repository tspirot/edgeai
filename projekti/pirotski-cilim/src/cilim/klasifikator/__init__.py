from cilim.klasifikator.base import KlasifikatorBackend, Nalaz


def build_klasifikator(katalog, cfg) -> KlasifikatorBackend:
    if cfg.backend == "dummy":
        from cilim.klasifikator.dummy_backend import DummyKlasifikator

        return DummyKlasifikator(katalog, cfg)
    if cfg.backend == "vit":
        from cilim.klasifikator.vit_backend import VitKlasifikator

        return VitKlasifikator(katalog, cfg)
    raise ValueError(f"Непознат класификатор: '{cfg.backend}' (има: vit, dummy)")


__all__ = ["KlasifikatorBackend", "Nalaz", "build_klasifikator"]
