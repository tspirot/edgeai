"""Чување и учитавање мапе (.npz) и извоз у слику (.png)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from mapa.grid import OccupancyGrid


def save_npz(grid: OccupancyGrid, path: "str | Path") -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        p, logodds=grid.logodds, res=grid.res, origin=grid.origin,
        occ_thr=grid.occ_thr, clamp=grid.clamp,
    )


def load_npz(path: "str | Path") -> OccupancyGrid:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Мапа не постоји: {p}")
    d = np.load(p)

    class _Cfg:
        res_m = float(d["res"])
        size_m = float(d["logodds"].shape[0]) * float(d["res"])
        hit_logodds = 0.85
        miss_logodds = -0.4
        clamp = float(d["clamp"])
        occupied_threshold = float(d["occ_thr"])

    grid = OccupancyGrid(_Cfg)
    grid.logodds = d["logodds"].astype(np.float32)
    grid.origin = d["origin"]
    return grid


def save_png(grid: OccupancyGrid, path: "str | Path", path_world=None, pose=None) -> None:
    from PIL import Image

    img = np.stack([grid.to_image()] * 3, axis=-1)
    n = grid.n

    def to_px(xy):
        cx, cy = grid.world_to_cell(xy)
        return cx, n - 1 - cy      # to_image ради flipud

    if path_world:
        for x, y in path_world:
            px, py = to_px((x, y))
            if 0 <= px < n and 0 <= py < n:
                img[py, px] = (60, 130, 240)
    if pose is not None:
        px, py = to_px((pose.x, pose.y))
        if 0 <= px < n and 0 <= py < n:
            img[max(0, py - 1):py + 2, max(0, px - 1):px + 2] = (230, 80, 60)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img).resize((n * 4, n * 4), Image.NEAREST).save(path)
