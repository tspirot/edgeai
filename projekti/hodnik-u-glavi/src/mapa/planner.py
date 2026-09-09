"""Планирање пута кроз occupancy grid: проширење препрека + A*."""

from __future__ import annotations

import heapq

import numpy as np


def inflate(occupied: np.ndarray, radius_cells: int) -> np.ndarray:
    """Прошири True ћелије за `radius_cells` (Чебишев) — ширина возила."""
    if radius_cells <= 0:
        return occupied.copy()
    out = occupied.copy()
    ys, xs = np.where(occupied)
    n = occupied.shape[0]
    r = radius_cells
    for y, x in zip(ys, xs):
        out[max(0, y - r):min(n, y + r + 1), max(0, x - r):min(n, x + r + 1)] = True
    return out


def _neighbors(x, y, diagonal):
    steps = [(-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0)]
    if diagonal:
        d = 2 ** 0.5
        steps += [(-1, -1, d), (-1, 1, d), (1, -1, d), (1, 1, d)]
    for dx, dy, cost in steps:
        yield x + dx, y + dy, cost


def a_star(blocked: np.ndarray, start, goal, allow_diagonal=True):
    """Најкраћи пут (листа (x, y) ћелија) кроз `blocked` (True = непроходно).

    Враћа [] ако нема пута. `start`/`goal` су (cx, cy).
    """
    n = blocked.shape[0]
    sx, sy = int(start[0]), int(start[1])
    gx, gy = int(goal[0]), int(goal[1])
    for cx, cy in ((sx, sy), (gx, gy)):
        if not (0 <= cx < n and 0 <= cy < n) or blocked[cy, cx]:
            return []

    def h(x, y):
        return ((x - gx) ** 2 + (y - gy) ** 2) ** 0.5

    open_heap = [(h(sx, sy), 0.0, sx, sy)]
    came: dict = {}
    g_cost = {(sx, sy): 0.0}
    while open_heap:
        _, g, x, y = heapq.heappop(open_heap)
        if (x, y) == (gx, gy):
            path = [(x, y)]
            while (x, y) in came:
                x, y = came[(x, y)]
                path.append((x, y))
            return path[::-1]
        if g > g_cost.get((x, y), float("inf")):
            continue
        for nx, ny, step in _neighbors(x, y, allow_diagonal):
            if not (0 <= nx < n and 0 <= ny < n) or blocked[ny, nx]:
                continue
            ng = g + step
            if ng < g_cost.get((nx, ny), float("inf")):
                g_cost[(nx, ny)] = ng
                came[(nx, ny)] = (x, y)
                heapq.heappush(open_heap, (ng + h(nx, ny), ng, nx, ny))
    return []


def plan(grid, start_xy, goal_xy, cfg):
    """Планирај у светским координатама. Врати листу (x, y) тачака у метрима."""
    occupied = grid.occupied_mask()
    if cfg.unknown_is_blocked:
        occupied = occupied | ~grid.known_mask()
    blocked = inflate(occupied, int(round(cfg.inflate_m / grid.res)))

    sx, sy = grid.world_to_cell(start_xy)
    gx, gy = grid.world_to_cell(goal_xy)
    cells = a_star(blocked, (sx, sy), (gx, gy), cfg.allow_diagonal)
    return [
        (grid.origin[0] + (cx + 0.5) * grid.res, grid.origin[1] + (cy + 0.5) * grid.res)
        for cx, cy in cells
    ]
