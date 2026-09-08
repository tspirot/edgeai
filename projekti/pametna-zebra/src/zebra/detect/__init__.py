"""Детекција објеката — избор модула према конфигурацији."""

from __future__ import annotations

from zebra.detect.base import Detection, Detector

__all__ = ["Detection", "Detector", "build_detector"]


def build_detector(cfg) -> Detector:
    backend = (cfg.backend or "").lower()

    if backend in ("yolo", "ultralytics"):
        from zebra.detect.yolo_backend import YoloDetector

        return YoloDetector(cfg)

    if backend == "hailo":
        from zebra.detect.hailo_backend import HailoDetector

        return HailoDetector(cfg)

    if backend == "dummy":
        from zebra.detect.dummy_backend import DummyDetector

        return DummyDetector(cfg)

    raise ValueError(f"Непознат detect backend: '{cfg.backend}'")
