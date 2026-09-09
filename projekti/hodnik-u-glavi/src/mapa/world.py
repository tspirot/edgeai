"""Синтетичка просторија и симулирани RPLIDAR — за `mapa sim` и тестове.

Просторија = списак зидних сегмената. Лидар из датог положаја баца све зраке
одједном (векторски) и враћа растојање до првог пресека са зидом.
"""

from __future__ import annotations

import numpy as np

from mapa.pose import Pose


def room(width=6.0, height=4.0, obstacles=True):
    """Правоугаона просторија, по избору две препреке. Списак сегмената ((x1,y1),(x2,y2))."""
    w, h = width / 2.0, height / 2.0
    segs = [
        ((-w, -h), (w, -h)), ((w, -h), (w, h)),
        ((w, h), (-w, h)), ((-w, h), (-w, -h)),
    ]
    if obstacles:
        segs += [
            ((-1.0, -0.5), (-1.0, 0.8)), ((-1.0, 0.8), (-0.4, 0.8)),
            ((1.4, -1.0), (1.4, 0.2)),
        ]
    return segs


class SimLidar:
    """Симулирани скен из просторије. Опционо додаје Гаусов шум на растојање."""

    def __init__(self, segments, n_beams=360, noise_m=0.01, max_m=6.0, seed=0) -> None:
        self._a = np.array([s[0] for s in segments], dtype=float)          # (S, 2)
        self._ab = np.array([s[1] for s in segments], dtype=float) - self._a
        self.angles = np.linspace(0.0, 360.0, n_beams, endpoint=False)
        self.noise_m = noise_m
        self.max_m = max_m
        self._rng = np.random.default_rng(seed)

    def scan(self, pose: Pose):
        """Врати (углови°, растојања mm) из положаја `pose`."""
        o = np.array([pose.x, pose.y])
        ang = pose.theta + np.deg2rad(self.angles)
        d = np.stack([np.cos(ang), np.sin(ang)], axis=1)                  # (B, 2)
        perp = np.stack([-d[:, 1], d[:, 0]], axis=1)                      # (B, 2)

        v1 = o - self._a                                                  # (S, 2)
        cross_ab_v1 = self._ab[:, 0] * v1[:, 1] - self._ab[:, 1] * v1[:, 0]  # (S,)

        # denom[s, b] = ab_s · perp_b ;  t2num[s, b] = v1_s · perp_b
        denom = self._ab @ perp.T                                         # (S, B)
        t2num = v1 @ perp.T                                               # (S, B)
        with np.errstate(divide="ignore", invalid="ignore"):
            t1 = cross_ab_v1[:, None] / denom                            # (S, B)
            t2 = t2num / denom
        valid = (np.abs(denom) > 1e-9) & (t1 >= 0.0) & (t2 >= 0.0) & (t2 <= 1.0)
        t1 = np.where(valid, t1, np.inf)

        ranges = t1.min(axis=0)                                          # (B,)
        finite = ranges < self.max_m
        r = ranges[finite] + self._rng.normal(0.0, self.noise_m, finite.sum())
        return self.angles[finite], r * 1000.0
