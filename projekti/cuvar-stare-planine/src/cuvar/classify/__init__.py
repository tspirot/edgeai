"""Класификација врсте — избор модула према конфигурацији."""

from __future__ import annotations

from cuvar.classify.base import Classifier, Prediction

__all__ = ["Classifier", "Prediction", "build_classifier"]


def build_classifier(cfg):
    backend = (cfg.backend or "").lower()
    if backend == "imx500":
        from cuvar.classify.imx500_backend import IMX500Classifier

        return IMX500Classifier(cfg)
    if backend == "onnx":
        from cuvar.classify.onnx_backend import OnnxClassifier

        return OnnxClassifier(cfg)
    if backend == "dummy":
        from cuvar.classify.dummy_backend import DummyClassifier

        return DummyClassifier(cfg)
    raise ValueError(f"Непознат classify backend: '{cfg.backend}'")
