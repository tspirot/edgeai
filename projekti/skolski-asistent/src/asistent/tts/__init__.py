"""Избор синтезе говора према конфигурацији."""

from __future__ import annotations

from asistent.tts.base import TtsBackend

__all__ = ["TtsBackend", "build_tts"]


def build_tts(tts_cfg) -> TtsBackend:
    backend = (tts_cfg.backend or "").lower()

    if backend == "piper":
        from asistent.tts.piper_backend import PiperTts

        return PiperTts(tts_cfg)

    if backend in ("console", "terminal"):
        from asistent.tts.console_tts import ConsoleTts

        return ConsoleTts(tts_cfg)

    raise ValueError(f"Непозната синтеза говора: '{tts_cfg.backend}'")
