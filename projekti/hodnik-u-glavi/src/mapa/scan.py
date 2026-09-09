"""Ласерски скен: поларно (угао, растојање) ↔ тачке у равни. Извори скенова."""

from __future__ import annotations

import logging

import numpy as np

log = logging.getLogger(__name__)


def polar_to_points(angles_deg, ranges_m, forward_offset_deg: float = 0.0) -> np.ndarray:
    """(угао°, растојање m) → (N, 2) тачке у оквиру возила (x напред, y лево)."""
    a = np.deg2rad(np.asarray(angles_deg, dtype=float) + forward_offset_deg)
    r = np.asarray(ranges_m, dtype=float)
    return np.column_stack([r * np.cos(a), r * np.sin(a)])


def clean_scan(angles_deg, ranges_mm, min_mm: float, max_mm: float):
    """Одбаци нула/бесконачно и вредности ван опсега. Врати (углови°, растојања m)."""
    a = np.asarray(angles_deg, dtype=float)
    r = np.asarray(ranges_mm, dtype=float)
    ok = np.isfinite(r) & (r >= min_mm) & (r <= max_mm)
    return a[ok], r[ok] / 1000.0


class ScanSource:
    def read(self) -> "tuple[np.ndarray, np.ndarray]":
        """Врати (углови°, растојања mm) за један комплетан круг."""
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        pass


class ReplayScanSource(ScanSource):
    """Скенови из снимка (.npz са 'angles' и 'ranges' листама низова)."""

    def __init__(self, path: str) -> None:
        data = np.load(path, allow_pickle=True)
        self._angles = list(data["angles"])
        self._ranges = list(data["ranges"])
        self._i = 0

    def read(self):
        if self._i >= len(self._angles):
            raise StopIteration
        a, r = self._angles[self._i], self._ranges[self._i]
        self._i += 1
        return np.asarray(a), np.asarray(r)


class RplidarScanSource(ScanSource):  # pragma: no cover - тражи хардвер
    def __init__(self, port: str) -> None:
        from rplidar import RPLidar

        self._lidar = RPLidar(port)
        self._it = self._lidar.iter_scans(max_buf_meas=1200)

    def read(self):
        scan = next(self._it)
        angles = np.array([m[1] for m in scan])
        ranges = np.array([m[2] for m in scan])
        return angles, ranges

    def close(self) -> None:
        try:
            self._lidar.stop()
            self._lidar.disconnect()
        except Exception:
            pass


def build_scan_source(cfg, replay: "str | None" = None) -> ScanSource:
    if replay:
        return ReplayScanSource(replay)
    backend = (cfg.backend or "auto").lower()
    if backend in ("auto", "rplidar"):
        try:
            return RplidarScanSource(cfg.port)
        except Exception as exc:  # pragma: no cover
            if backend == "rplidar":
                raise
            raise RuntimeError(
                f"RPLIDAR недоступан ({exc}). За пробу: `mapa sim` или `--replay снимак.npz`."
            ) from exc
    raise ValueError(f"Непознат lidar backend: '{cfg.backend}'")
