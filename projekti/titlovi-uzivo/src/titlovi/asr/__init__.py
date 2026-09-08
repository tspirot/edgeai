"""Избор ASR модула према конфигурацији."""

from __future__ import annotations

from titlovi.asr.base import AsrBackend, Transcript

__all__ = ["AsrBackend", "Transcript", "build_backend"]


def build_backend(asr_cfg, samplerate: int = 16000) -> AsrBackend:
    backend = (asr_cfg.backend or "").lower()

    if backend in ("faster-whisper", "whisper", "faster_whisper"):
        from titlovi.asr.faster_whisper_backend import FasterWhisperBackend

        return FasterWhisperBackend(asr_cfg.whisper, samplerate)

    if backend == "vosk":
        from titlovi.asr.vosk_backend import VoskBackend

        return VoskBackend(asr_cfg.vosk, samplerate)

    if backend == "dummy":
        from titlovi.asr.dummy_backend import DummyBackend

        return DummyBackend(asr_cfg, samplerate)

    raise ValueError(f"Непознат ASR backend: '{asr_cfg.backend}'")
