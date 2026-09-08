from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class BlockFeatures:
    vectors: np.ndarray   # (G*G, D) — по један дескриптор за сваки блок
    grid: int             # G


class FeatureExtractor:
    def extract(self, image) -> BlockFeatures:  # pragma: no cover - интерфејс
        raise NotImplementedError


def to_gray(image) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float32)
    if arr.ndim == 3:
        arr = arr.mean(axis=2)
    return arr


def resize(gray: np.ndarray, size: int) -> np.ndarray:
    if gray.shape == (size, size):
        return gray
    try:
        import cv2

        return cv2.resize(gray, (size, size)).astype(np.float32)
    except Exception:  # pragma: no cover - без OpenCV: најближи сусед
        h, w = gray.shape
        yi = (np.linspace(0, h - 1, size)).astype(int)
        xi = (np.linspace(0, w - 1, size)).astype(int)
        return gray[np.ix_(yi, xi)].astype(np.float32)
