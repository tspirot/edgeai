"""Occupancy grid — 2D мапа вероватноће заузећа, log-odds.

Свака ћелија чува log-odds вредност: > 0 препрека, < 0 слободно, 0 непознато.
Зрак од сензора до погођене тачке: све ћелије на путу → слободно, крајња → заузето.
"""

from __future__ import annotations

import numpy as np


def _bresenham(x0: int, y0: int, x1: int, y1: int):
    """Ћелије на линији (x0,y0)→(x1,y1), укључујући обе крајње."""
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    cells = []
    while True:
        cells.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return cells


class OccupancyGrid:
    def __init__(self, cfg) -> None:
        self.res = cfg.res_m
        self.n = int(round(cfg.size_m / cfg.res_m))
        self.hit = cfg.hit_logodds
        self.miss = cfg.miss_logodds
        self.clamp = cfg.clamp
        self.occ_thr = cfg.occupied_threshold
        self.logodds = np.zeros((self.n, self.n), dtype=np.float32)
        self.origin = np.array([-cfg.size_m / 2.0, -cfg.size_m / 2.0])  # доњи-леви угао (m)

    # --- координате -----------------------------------------------------
    def world_to_cell(self, xy):
        c = ((np.asarray(xy, dtype=float) - self.origin) / self.res).astype(int)
        return c[..., 0], c[..., 1]

    def in_bounds(self, cx, cy) -> bool:
        return 0 <= cx < self.n and 0 <= cy < self.n

    # --- уградња скена -------------------------------------------------
    def integrate(self, sensor_xy, points_world) -> None:
        sx, sy = self.world_to_cell(sensor_xy)
        n = self.n
        lo = self.logodds
        for p in np.asarray(points_world, dtype=float):
            ex, ey = self.world_to_cell(p)
            ray = np.array(_bresenham(int(sx), int(sy), int(ex), int(ey)))
            inb = (ray[:, 0] >= 0) & (ray[:, 0] < n) & (ray[:, 1] >= 0) & (ray[:, 1] < n)
            if inb.all():
                cx, cy = ray[:, 0], ray[:, 1]
                lo[cy[:-1], cx[:-1]] += self.miss     # пут до тачке — слободно
                lo[cy[-1], cx[-1]] += self.hit        # тачка — заузето
            else:
                cut = int(np.argmin(inb))             # прва ћелија ван мапе
                if cut > 0:
                    cx, cy = ray[:cut, 0], ray[:cut, 1]
                    lo[cy, cx] += self.miss
        np.clip(lo, -self.clamp, self.clamp, out=lo)

    # --- читање -------------------------------------------------------
    def prob(self) -> np.ndarray:
        return 1.0 - 1.0 / (1.0 + np.exp(self.logodds))

    def _thr_logodds(self) -> float:
        t = min(max(self.occ_thr, 1e-4), 1 - 1e-4)
        return float(np.log(t / (1.0 - t)))

    def known_mask(self) -> np.ndarray:
        return self.logodds != 0.0

    def occupied_mask(self) -> np.ndarray:
        # само ћелије за које постоји доказ да су заузете (непознате су logodds == 0)
        return self.logodds > self._thr_logodds()

    def free_mask(self) -> np.ndarray:
        return self.known_mask() & ~self.occupied_mask()

    def to_image(self) -> np.ndarray:
        """Сива слика: 127 непознато, 255 слободно, 0 препрека (за преглед)."""
        img = np.full((self.n, self.n), 127, dtype=np.uint8)
        img[self.free_mask()] = 255
        img[self.occupied_mask()] = 0
        return np.flipud(img)
