"""Нормализација тачака шаке — независна од положаја, величине и ротације шаке.

Улаз: 21 тачка (x, y) редоследом као MediaPipe Hands (0 = зглоб).
Излаз: вектор од 42 броја, спреман за класификатор.
"""

from __future__ import annotations

import numpy as np

WRIST = 0
MIDDLE_MCP = 9


def normalize_landmarks(points) -> np.ndarray:
    pts = np.asarray(points, dtype=np.float64).reshape(21, 2)

    # 1) премести зглоб у координатни почетак
    p = pts - pts[WRIST]

    # 2) скалирај по дужини длана (зглоб → корен средњег прста)
    scale = np.linalg.norm(p[MIDDLE_MCP])
    if scale < 1e-9:
        scale = 1.0
    p = p / scale

    # 3) ротирај да средњи прст гледа „на горе" (+y)
    angle = np.arctan2(p[MIDDLE_MCP, 0], p[MIDDLE_MCP, 1])
    c, s = np.cos(angle), np.sin(angle)
    rot = np.array([[c, -s], [s, c]])
    p = p @ rot.T

    return p.reshape(-1).astype(np.float32)
