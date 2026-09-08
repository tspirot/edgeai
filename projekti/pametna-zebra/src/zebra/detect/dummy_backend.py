"""Лажни детектор — симулира сцену без камере и без модела.

Подразумевано: пешак иде с лева на десно преко прелаза, ауто силази одозго.
Њихови путеви се секу → упозорење. За тестове се може дати `script`
(листа листа `Detection` по кадру).
"""

from __future__ import annotations

from zebra.detect.base import Detection, Detector


class DummyDetector(Detector):
    def __init__(self, cfg=None, width: int = 1280, height: int = 720,
                 script: "list[list[Detection]] | None" = None) -> None:
        self.w = width
        self.h = height
        self.script = script
        self._i = -1

    def detect(self, frame=None) -> list[Detection]:
        self._i += 1
        if self.script is not None:
            return self.script[self._i] if self._i < len(self.script) else []
        return self._simulate(self._i)

    def _simulate(self, t: int) -> list[Detection]:
        """Реалне брзине: пешак ~1,4 m/s, ауто ~12 m/s (уз meters_per_pixel≈0,05).

        Пешак споро прелази центар прелаза; ауто силази низ коловоз и стиже до
        прелаза баш док је пешак ту → путеви се секу, упозорење се пали.
        """
        dets: list[Detection] = []
        cx, cy = self.w / 2, self.h / 2

        # пешак: споро преко центра, цело време
        px = cx - 80 + t * 1.0
        dets.append(Detection(px - 20, cy - 52, px + 20, cy + 52, 0.9, "person"))

        # ауто: силази низ коловоз, до прелаза око t≈80
        if t >= 30:
            vy = -60 + (t - 30) * 8.0
            if vy < self.h + 80:
                dets.append(Detection(cx - 64, vy - 42, cx + 64, vy + 42, 0.85, "vehicle"))

        return dets
