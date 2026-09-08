"""Окидач по покрету — разлика кадра у односу на научену позадину.

Чиста логика, лако се тестира. На правом уређају се уместо (или уз) ово може
користити PIR сензор на GPIO.
"""

from __future__ import annotations

import numpy as np


class MotionTrigger:
    def __init__(self, change_fraction: float = 0.02, pixel_delta: int = 25,
                 cooldown_s: float = 8.0, warmup_frames: int = 5, alpha: float = 0.1) -> None:
        self.change_fraction = change_fraction
        self.pixel_delta = pixel_delta
        self.cooldown_s = cooldown_s
        self.warmup_frames = warmup_frames
        self.alpha = alpha
        self._bg: "np.ndarray | None" = None
        self._seen = 0
        self._last_trigger = -1e18

    def update(self, frame, now: float) -> dict:
        """Врати {'motion': float, 'triggered': bool} за дати кадар (H×W или H×W×C)."""
        gray = self._to_gray(frame)
        if self._bg is None:
            self._bg = gray.copy()

        diff = np.abs(gray - self._bg)
        changed = float(np.mean(diff >= self.pixel_delta))

        # спора адаптација позадине (осветљење, сенке)
        self._bg = (1.0 - self.alpha) * self._bg + self.alpha * gray
        self._seen += 1

        warm = self._seen <= self.warmup_frames
        cooling = (now - self._last_trigger) < self.cooldown_s
        triggered = (not warm) and (not cooling) and changed >= self.change_fraction
        if triggered:
            self._last_trigger = now

        return {"motion": changed, "triggered": triggered}

    @staticmethod
    def _to_gray(frame) -> np.ndarray:
        arr = np.asarray(frame, dtype=np.float32)
        if arr.ndim == 3:
            arr = arr.mean(axis=2)
        return arr
