"""Синтетички положаји шаке за неколико слова — за симулацију и тестове.

Прави скуп података ученици снимају сами (`znak record`). Ово је довољно да
цео ланац (тачке → нормализација → класификатор → гласање) ради без камере.
"""

from __future__ import annotations

import numpy as np

# редослед прстију и индекси тачака (као MediaPipe): 0 зглоб, па по 4 тачке
_FINGERS = ["thumb", "index", "middle", "ring", "pinky"]
_MCP_X = {"thumb": -0.42, "index": -0.16, "middle": 0.0, "ring": 0.16, "pinky": 0.32}


def _finger(base, curl: float, thumb: bool = False) -> list[np.ndarray]:
    """4 тачке прста: MCP па 3 зглоба, савијају се како `curl` расте (0–1)."""
    seg = 0.17
    side = -1.0 if thumb else 1.0
    pts = [np.array(base, dtype=float)]
    p = pts[0].copy()
    ang = 0.6 if thumb else 0.0
    for _ in range(3):
        ang += curl * (0.5 if thumb else 0.95)
        p = p + seg * np.array([side * np.sin(ang), np.cos(ang)])
        pts.append(p.copy())
    return pts


def make_pose(curls: dict) -> np.ndarray:
    """`curls`: {прст: 0..1}. Врати (21, 2) тачке."""
    pts = [np.array([0.0, 0.0])]  # зглоб
    for f in _FINGERS:
        base = [_MCP_X[f], 0.22 if f != "thumb" else 0.05]
        pts += _finger(base, float(curls.get(f, 0.0)), thumb=(f == "thumb"))
    return np.array(pts)


# слова српске једноручне азбуке — упрошћени положаји
POSES: dict[str, np.ndarray] = {
    "A": make_pose({"thumb": 0.1, "index": 1.0, "middle": 1.0, "ring": 1.0, "pinky": 1.0}),
    "B": make_pose({"thumb": 0.2, "index": 0.0, "middle": 0.0, "ring": 0.0, "pinky": 0.0}),
    "V": make_pose({"thumb": 0.9, "index": 0.0, "middle": 0.0, "ring": 1.0, "pinky": 1.0}),
    "G": make_pose({"thumb": 0.0, "index": 0.0, "middle": 1.0, "ring": 1.0, "pinky": 1.0}),
    "D": make_pose({"thumb": 0.6, "index": 0.0, "middle": 1.0, "ring": 1.0, "pinky": 1.0}),
    "L": make_pose({"thumb": 0.0, "index": 0.0, "middle": 1.0, "ring": 1.0, "pinky": 0.0}),
    "O": make_pose({"thumb": 0.6, "index": 0.6, "middle": 0.6, "ring": 0.6, "pinky": 0.6}),
    "E": make_pose({"thumb": 0.9, "index": 0.7, "middle": 0.7, "ring": 0.7, "pinky": 0.7}),
}


def sample(letter: str, rng, jitter: float = 0.015,
           rotate: float = 0.5, scale: float = 0.25, shift: float = 0.3) -> np.ndarray:
    """Насумична варијација положаја: шум + ротација + скала + померај у кадру."""
    pts = POSES[letter].copy()
    pts = pts + rng.normal(0.0, jitter, pts.shape)
    ang = rng.uniform(-rotate, rotate)
    c, s = np.cos(ang), np.sin(ang)
    pts = pts @ np.array([[c, -s], [s, c]])
    pts = pts * rng.uniform(1.0 - scale, 1.0 + scale)
    pts = pts + rng.uniform(-shift, shift, 2)
    return pts
