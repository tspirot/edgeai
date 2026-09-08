"""Избор приказа према конфигурацији."""

from __future__ import annotations

from titlovi.display.base import Display

__all__ = ["Display", "build_display"]


def build_display(cfg) -> Display:
    backend = (cfg.backend or "").lower()

    if backend == "pygame":
        from titlovi.display.pygame_display import PygameDisplay

        return PygameDisplay(cfg)

    if backend == "web":
        from titlovi.display.web_display import WebDisplay

        return WebDisplay(cfg)

    if backend == "console":
        from titlovi.display.console_display import ConsoleDisplay

        return ConsoleDisplay(cfg)

    raise ValueError(f"Непознат приказ: '{cfg.backend}'")
