"""Сигурносни арбитар: спаја излаз модела и најближу препреку са лидара.

Ово намерно НИЈЕ неуронска мрежа — обичан праг са хистерезом. Може да се
објасни, тестира и не мења се тренингом. Он има последњу реч над гасом.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Decision:
    steer: float          # −1 (лево) .. 1 (десно)
    throttle: float       # 0 .. 1 (после ограничења)
    braking: bool
    reason: str


class SafetyArbiter:
    def __init__(self, cfg, max_throttle: float) -> None:
        self.cfg = cfg
        self.max_throttle = max_throttle
        self._braking = False   # стање хистерезе

    def step(
        self,
        model_steer: float,
        model_throttle: float,
        nearest_mm: float,
        scan_age_s: float,
    ) -> Decision:
        steer = max(-1.0, min(1.0, model_steer))
        throttle = max(0.0, min(self.max_throttle, model_throttle))

        if scan_age_s > self.cfg.stale_scan_s:
            self._braking = True
            return Decision(steer, 0.0, True, f"нема свежег скена ({scan_age_s:.2f}s)")

        # хистереза: једном када кочи, држи док не пређе release_mm
        if self._braking:
            if nearest_mm >= self.cfg.release_mm:
                self._braking = False
            else:
                return Decision(steer, 0.0, True, f"препрека {nearest_mm:.0f} mm")

        if nearest_mm < self.cfg.brake_mm:
            self._braking = True
            return Decision(steer, 0.0, True, f"препрека {nearest_mm:.0f} mm")

        if nearest_mm < self.cfg.slow_mm:
            throttle = min(throttle, self.max_throttle * self.cfg.slow_factor)
            return Decision(steer, throttle, False, f"успоравање ({nearest_mm:.0f} mm)")

        return Decision(steer, throttle, False, "слободно")

    @property
    def braking(self) -> bool:
        return self._braking
