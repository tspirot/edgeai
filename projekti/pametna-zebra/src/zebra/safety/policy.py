"""Правило упозорења: пешак на прелазу + возило на коловозу + мало времена до судара.

Са хистерезисом — упозорење остаје упаљено још `hold_seconds` после окидача,
да не трепери.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from zebra.safety.geometry import speed, time_to_conflict


@dataclass
class WarningState:
    active: bool = False
    reason: str = ""
    ttc: float = math.inf


class WarningPolicy:
    def __init__(self, cfg) -> None:
        self.ttc_threshold = cfg.ttc_seconds
        self.radius_m = cfg.conflict_radius_m
        self.mpp = cfg.meters_per_pixel
        self.hold = cfg.hold_seconds
        self._hold_until = -math.inf

    def evaluate(self, tracks, scene, now: float, fps: float) -> WarningState:
        persons = [t for t in tracks if t.kind == "person"]
        vehicles = [t for t in tracks if t.kind == "vehicle"]

        person_near = [
            p for p in persons if scene.where(p.center) in ("crosswalk", "roadway")
        ]
        # возило на коловозу или већ на самом прелазу (најгори случај)
        vehicles_on_road = [
            v for v in vehicles if scene.where(v.center) in ("roadway", "crosswalk")
        ]

        best_ttc = math.inf
        for p in person_near:
            pa = (p.center[0] * self.mpp, p.center[1] * self.mpp)
            pv = tuple(c * self.mpp for c in p.velocity(fps))
            for v in vehicles_on_road:
                vpos = (v.center[0] * self.mpp, v.center[1] * self.mpp)
                vv = tuple(c * self.mpp for c in v.velocity(fps))
                # возило мора да се стварно креће (паркирано није опасност)
                if speed(v.velocity(fps), self.mpp) < 0.5:
                    continue
                ttc = time_to_conflict(pa, pv, vpos, vv, self.radius_m)
                best_ttc = min(best_ttc, ttc)

        triggered = best_ttc <= self.ttc_threshold
        if triggered:
            self._hold_until = now + self.hold

        if now <= self._hold_until:
            reason = (
                f"пешак и возило, TTC {best_ttc:.1f}s"
                if triggered
                else "задржавање после окидача"
            )
            return WarningState(active=True, reason=reason, ttc=best_ttc)

        return WarningState(active=False, ttc=best_ttc)
