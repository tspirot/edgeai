"""Заједнички уговор за политику вожње (слика → волан, гас)."""

from __future__ import annotations

import numpy as np


class Policy:
    def predict(self, image: np.ndarray) -> "tuple[float, float]":
        """Врати (steer, throttle): steer ∈ [−1, 1], throttle ∈ [0, 1]."""
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        pass


def preprocess(image: np.ndarray, width: int, height: int) -> np.ndarray:
    """RGB uint8 → (1, H, W, 3) float32 у [0, 1], без спољних зависности."""
    arr = np.asarray(image)
    if arr.ndim == 2:
        arr = np.stack([arr] * 3, axis=-1)
    h, w = arr.shape[:2]
    if (w, h) != (width, height):
        yi = (np.linspace(0, h - 1, height)).astype(np.int64)
        xi = (np.linspace(0, w - 1, width)).astype(np.int64)
        arr = arr[yi][:, xi]
    return (arr[..., :3].astype(np.float32) / 255.0)[None, ...]
