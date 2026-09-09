"""Избор ASR модула према конфигурацији."""

from __future__ import annotations

from asistent.asr.base import AsrBackend

__all__ = ["AsrBackend", "build_asr"]


def build_asr(asr_cfg) -> AsrBackend:
    backend = (asr_cfg.backend or "").lower()

    if backend in ("faster-whisper", "whisper", "faster_whisper"):
        from asistent.asr.faster_whisper_backend import FasterWhisperAsr

        return FasterWhisperAsr(asr_cfg.whisper, asr_cfg.samplerate)

    if backend == "dummy":
        from asistent.asr.dummy_backend import DummyAsr

        return DummyAsr(asr_cfg)

    raise ValueError(f"Непознат ASR backend: '{asr_cfg.backend}'")
