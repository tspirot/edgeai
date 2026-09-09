"""Лажна политика — увек право, фиксни гас. За пробу ланца и тестове."""

from __future__ import annotations

import numpy as np

from volan.policy.base import Policy


class DummyPolicy(Policy):
    def __init__(self, cfg=None, steer: float = 0.0, throttle: float = 0.3) -> None:
        self._steer = steer
        self._throttle = throttle

    def predict(self, image: np.ndarray) -> "tuple[float, float]":
        return self._steer, self._throttle
