"""RPLIDAR A1 очитавање + рачун најближе препреке у конусу испред аута.

`rplidar` библиотека се увози лениво. `nearest_in_cone` је чиста функција —
покрива је тест и не тражи хардвер.
"""

from __future__ import annotations

import logging
import threading
import time

import numpy as np

log = logging.getLogger(__name__)

# скен = низ (angle_deg, distance_mm); angle 0..360, distance 0 = нема очитавања


def nearest_in_cone(
    scan,
    cone_deg: float,
    forward_offset_deg: float = 0.0,
    min_valid_mm: float = 120.0,
    max_range_mm: float = 4000.0,
) -> float:
    """Најмање растојање (mm) у конусу ширине `cone_deg` око „напред".

    Враћа `max_range_mm` ако у конусу нема ниједне важеће тачке.
    """
    if cone_deg <= 0:
        raise ValueError("cone_deg мора бити позитиван")
    half = cone_deg / 2.0
    best = max_range_mm
    for angle, dist in scan:
        if dist is None or dist <= 0:
            continue
        # разлика угла у односу на „напред“, нормализована на [-180, 180]
        delta = ((angle - forward_offset_deg) + 180.0) % 360.0 - 180.0
        if abs(delta) > half:
            continue
        if dist < min_valid_mm or dist > max_range_mm:
            continue
        if dist < best:
            best = dist
    return best


class LidarSource:
    """Позадинска нит која држи најсвежији скен. Заједнички интерфејс за прави и лажни лидар."""

    def latest(self) -> "tuple[list, float]":
        """(scan, timestamp) — најсвежији комплетан круг."""
        raise NotImplementedError

    def close(self) -> None:
        pass


class DummyLidar(LidarSource):
    """Синтетички лидар: препрека испред на задатом растојању које се може мењати."""

    def __init__(self, obstacle_mm: float = 4000.0, spread_deg: float = 20.0) -> None:
        self.obstacle_mm = obstacle_mm
        self.spread_deg = spread_deg

    def set_obstacle(self, mm: float) -> None:
        self.obstacle_mm = mm

    def latest(self):
        scan = []
        for a in range(0, 360, 1):
            delta = (a + 180) % 360 - 180
            if abs(delta) <= self.spread_deg / 2:
                scan.append((float(a), float(self.obstacle_mm)))
            else:
                scan.append((float(a), 3500.0))
        return scan, time.monotonic()


class RplidarSource(LidarSource):
    def __init__(self, port: str) -> None:
        from rplidar import RPLidar

        self._lidar = RPLidar(port)
        self._scan: list = []
        self._ts = 0.0
        self._stop = threading.Event()
        self._thr = threading.Thread(target=self._loop, daemon=True)
        self._thr.start()

    def _loop(self) -> None:  # pragma: no cover - тражи хардвер
        try:
            for scan in self._lidar.iter_scans(max_buf_meas=800):
                self._scan = [(ang, dist) for (_q, ang, dist) in scan]
                self._ts = time.monotonic()
                if self._stop.is_set():
                    break
        except Exception:
            log.exception("RPLIDAR нит пала")

    def latest(self):
        return list(self._scan), self._ts

    def close(self) -> None:  # pragma: no cover
        self._stop.set()
        try:
            self._lidar.stop()
            self._lidar.disconnect()
        except Exception:
            pass


def build_lidar(cfg) -> LidarSource:
    backend = (cfg.backend or "auto").lower()
    if backend == "dummy":
        return DummyLidar()
    if backend in ("auto", "rplidar"):
        try:
            return RplidarSource(cfg.port)
        except Exception as exc:  # pragma: no cover
            if backend == "rplidar":
                raise
            log.warning("RPLIDAR недоступан (%s) — користим DummyLidar", exc)
            return DummyLidar()
    raise ValueError(f"Непознат lidar backend: '{cfg.backend}'")
