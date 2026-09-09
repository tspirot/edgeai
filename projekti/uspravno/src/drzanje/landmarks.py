"""Кључне тачке тела — 33 тачке по MediaPipe Pose распореду.

Свака тачка: (x, y, visibility), x/y нормализовани на [0, 1] (y расте наниже,
као на слици). Овде држимо само оно што нам треба и именоване приступе.
"""

from __future__ import annotations

import numpy as np

# индекси које користимо (MediaPipe Pose)
IDX = {
    "nose": 0,
    "left_ear": 7,
    "right_ear": 8,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_hip": 23,
    "right_hip": 24,
}
N_POINTS = 33


class Landmarks:
    def __init__(self, points: np.ndarray) -> None:
        pts = np.asarray(points, dtype=float)
        if pts.shape != (N_POINTS, 3):
            raise ValueError(f"Очекивано {N_POINTS}×3, добијено {pts.shape}")
        self.points = pts

    def xy(self, name: str) -> np.ndarray:
        return self.points[IDX[name], :2]

    def visibility(self, name: str) -> float:
        return float(self.points[IDX[name], 2])

    def visible(self, name: str, thr: float) -> bool:
        return self.visibility(name) >= thr

    def midpoint(self, a: str, b: str) -> np.ndarray:
        return (self.xy(a) + self.xy(b)) / 2.0

    def lerp(self, other: "Landmarks", alpha: float) -> "Landmarks":
        """EMA изглађивање: (1-alpha)*self + alpha*other."""
        return Landmarks((1.0 - alpha) * self.points + alpha * other.points)


def facing_side(lm: Landmarks) -> str:
    """Која страна тела је ка камери — она чије је уво видљивије."""
    return "left" if lm.visibility("left_ear") >= lm.visibility("right_ear") else "right"
