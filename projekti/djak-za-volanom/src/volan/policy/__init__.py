"""Избор политике вожње према конфигурацији."""

from __future__ import annotations

from volan.policy.base import Policy, preprocess

__all__ = ["Policy", "preprocess", "build_policy"]


def build_policy(model_cfg) -> Policy:
    backend = (model_cfg.backend or "").lower()

    if backend == "tflite":
        from volan.policy.tflite_policy import TflitePolicy

        return TflitePolicy(model_cfg)

    if backend == "heuristic":
        from volan.policy.heuristic_policy import HeuristicPolicy

        return HeuristicPolicy(model_cfg, model_cfg.cruise_throttle)

    if backend == "dummy":
        from volan.policy.dummy_policy import DummyPolicy

        return DummyPolicy(model_cfg, throttle=model_cfg.cruise_throttle)

    raise ValueError(f"Непозната политика: '{model_cfg.backend}'")
