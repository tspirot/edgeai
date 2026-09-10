from cilim.generator.base import GeneratorBackend


def build_generator(katalog, cfg) -> GeneratorBackend:
    """`cfg` је цео `Config` — процедуралном генератору треба и мрежа картона."""
    if cfg.generator.backend == "pravila":
        from cilim.generator.pravila_backend import PravilaGenerator

        return PravilaGenerator(katalog, cfg)
    if cfg.generator.backend == "difuzija":
        from cilim.generator.difuzija_backend import DifuzijaGenerator

        return DifuzijaGenerator(katalog, cfg.generator)
    raise ValueError(
        f"Непознат генератор: '{cfg.generator.backend}' (има: difuzija, pravila)"
    )


__all__ = ["GeneratorBackend", "build_generator"]
