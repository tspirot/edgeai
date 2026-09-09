"""2D положај (x, y, θ) и трансформације тачака. Угао у радијанима."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Pose:
    x: float = 0.0
    y: float = 0.0
    theta: float = 0.0

    def as_matrix(self) -> np.ndarray:
        c, s = np.cos(self.theta), np.sin(self.theta)
        return np.array([[c, -s, self.x], [s, c, self.y], [0.0, 0.0, 1.0]])

    def transform(self, points: np.ndarray) -> np.ndarray:
        """Примени положај на (N, 2) тачке у локалном оквиру → глобални оквир."""
        pts = np.asarray(points, dtype=float)
        c, s = np.cos(self.theta), np.sin(self.theta)
        rot = np.array([[c, -s], [s, c]])
        return pts @ rot.T + np.array([self.x, self.y])

    def compose(self, delta: "Pose") -> "Pose":
        """Овај положај, па `delta` изражен у локалном оквиру → нови глобални положај."""
        m = self.as_matrix() @ delta.as_matrix()
        return Pose(float(m[0, 2]), float(m[1, 2]), _wrap(self.theta + delta.theta))


def _wrap(a: float) -> float:
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def from_matrix(m: np.ndarray) -> Pose:
    return Pose(float(m[0, 2]), float(m[1, 2]), float(np.arctan2(m[1, 0], m[0, 0])))
