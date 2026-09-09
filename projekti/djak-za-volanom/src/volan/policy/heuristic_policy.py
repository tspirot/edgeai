"""Политика без учења — прати светлу траку у доњој трећини слике.

Служи да ауто вози и пре него што се сакупе подаци, и као полазна тачка за
разговор „чиме је CNN бољи од овога“.
"""

from __future__ import annotations

import numpy as np

from volan.policy.base import Policy


class HeuristicPolicy(Policy):
    def __init__(self, cfg=None, cruise_throttle: float = 0.35) -> None:
        self.cruise = cruise_throttle

    def predict(self, image: np.ndarray) -> "tuple[float, float]":
        arr = np.asarray(image)
        if arr.ndim == 3:
            gray = arr[..., :3].mean(axis=-1)
        else:
            gray = arr.astype(np.float32)
        h, w = gray.shape
        band = gray[int(h * 0.66):, :]                 # доња трећина
        weights = band - band.mean()
        weights[weights < 0] = 0
        total = weights.sum()
        if total <= 1e-6:
            return 0.0, self.cruise
        cols = np.arange(w)
        centroid = float((weights.sum(axis=0) * cols).sum() / total)
        steer = (centroid - (w - 1) / 2.0) / ((w - 1) / 2.0)   # −1..1
        return float(np.clip(steer, -1.0, 1.0)), self.cruise
