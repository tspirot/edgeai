"""Зоне на слици: пешачки прелаз и коловоз. Полигони из `zones.json`."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Polygon:
    points: list[tuple[float, float]]

    def contains(self, point: tuple[float, float]) -> bool:
        """Ray casting — тачка унутар полигона."""
        x, y = point
        pts = self.points
        n = len(pts)
        if n < 3:
            return False
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
            ):
                inside = not inside
            j = i
        return inside

    @property
    def centroid(self) -> tuple[float, float]:
        n = len(self.points) or 1
        sx = sum(p[0] for p in self.points)
        sy = sum(p[1] for p in self.points)
        return (sx / n, sy / n)


@dataclass
class Scene:
    crosswalk: "Polygon | None" = None
    roadway: "Polygon | None" = None

    def where(self, point: tuple[float, float]) -> str:
        if self.crosswalk and self.crosswalk.contains(point):
            return "crosswalk"
        if self.roadway and self.roadway.contains(point):
            return "roadway"
        return "elsewhere"

    # ------------------------------------------------------------------
    @classmethod
    def from_file(cls, path: "str | Path") -> "Scene":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        def poly(key):
            pts = data.get(key)
            return Polygon([tuple(p) for p in pts]) if pts else None
        return cls(crosswalk=poly("crosswalk"), roadway=poly("roadway"))

    def to_file(self, path: "str | Path") -> None:
        out = {}
        if self.crosswalk:
            out["crosswalk"] = [list(p) for p in self.crosswalk.points]
        if self.roadway:
            out["roadway"] = [list(p) for p in self.roadway.points]
        Path(path).write_text(json.dumps(out, indent=2), encoding="utf-8")

    @classmethod
    def default(cls, width: int = 1280, height: int = 720) -> "Scene":
        """Разумне почетне зоне ако калибрација није урађена: прелаз хоризонтално
        кроз средину, коловоз вертикална трака кроз средину."""
        cw = Polygon([
            (0.05 * width, 0.40 * height), (0.95 * width, 0.40 * height),
            (0.95 * width, 0.60 * height), (0.05 * width, 0.60 * height),
        ])
        rw = Polygon([
            (0.35 * width, 0.0), (0.65 * width, 0.0),
            (0.65 * width, height), (0.35 * width, height),
        ])
        return cls(crosswalk=cw, roadway=rw)
