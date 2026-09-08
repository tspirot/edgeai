"""Лажни детектор тачака — „показује" слова из унапред задатог низа.

За симулацију и тестове: уместо камере, врти листу слова, свако неколико кадрова,
уз насумичну варијацију положаја.
"""

from __future__ import annotations

import numpy as np

from znak.poses import POSES, sample


class DummyHands:
    def __init__(self, cfg=None, sequence=None, hold: int = 12, seed: int = 0,
                 scale_px: float = 220.0, center=(640.0, 360.0)) -> None:
        self.sequence = list(sequence or ["A", "B", "V", "D", "L", "O"])
        self.hold = hold
        self.rng = np.random.default_rng(seed)
        self.scale_px = scale_px
        self.center = np.array(center, dtype=float)
        self._i = -1

    def detect(self, frame=None):
        self._i += 1
        step = self._i // self.hold
        if step >= len(self.sequence):
            return None
        letter = self.sequence[step]
        pts = sample(letter, self.rng)
        # у „пиксел" простор (нормализација је инваријантна на скалу и померај)
        return pts * self.scale_px + self.center

    @property
    def expected(self) -> "str | None":
        step = self._i // self.hold
        return self.sequence[step] if 0 <= step < len(self.sequence) else None

    def close(self) -> None:
        pass
