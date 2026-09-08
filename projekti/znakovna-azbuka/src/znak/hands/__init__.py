"""Детекција тачака шаке."""

from __future__ import annotations

from znak.hands.base import HandDetector

__all__ = ["HandDetector", "build_detector"]


def build_detector(cfg):
    backend = (cfg.backend or "").lower()
    if backend == "mediapipe":
        from znak.hands.mediapipe_backend import MediaPipeHands

        return MediaPipeHands(cfg)
    if backend == "dummy":
        from znak.hands.dummy_backend import DummyHands

        return DummyHands(cfg)
    raise ValueError(f"Непознат hands backend: '{cfg.backend}'")
