"""Углови држања из кључних тачака. Чисте функције — покривене тестовима.

Слика: x расте удесно, y наниже. „Усправно“ = вектор навише = (0, -1).
Угао од вертикале је позитиван без обзира на смер нагиба (мери се одступање).
"""

from __future__ import annotations

import numpy as np

from drzanje.landmarks import Landmarks, facing_side

_UP = np.array([0.0, -1.0])


def _angle_from_vertical(v: np.ndarray) -> float:
    """Угао (степени) између вектора `v` и вертикале навише, у [0, 180]."""
    n = np.linalg.norm(v)
    if n < 1e-9:
        return 0.0
    cos = float(np.clip(np.dot(v, _UP) / n, -1.0, 1.0))
    return float(np.degrees(np.arccos(cos)))


def neck_angle(lm: Landmarks, side: str = "auto") -> float:
    """Нагиб врата напред: вектор средиште_рамена→уво у односу на вертикалу.

    Усправна глава изнад рамена → близу 0. Глава избачена напред → расте.
    Средиште рамена је стабилније од једне стране (лакше промашива у профилу).
    """
    if side == "auto":
        side = facing_side(lm)
    ear = lm.xy(f"{side}_ear")
    base = lm.midpoint("left_shoulder", "right_shoulder")
    return _angle_from_vertical(ear - base)


def trunk_angle(lm: Landmarks, side: str = "auto") -> float:
    """Нагиб трупа напред: вектор кук→раме у односу на вертикалу.

    Ради са средиштем рамена и кукова (стабилније од једне стране).
    """
    shoulder = lm.midpoint("left_shoulder", "right_shoulder")
    hip = lm.midpoint("left_hip", "right_hip")
    return _angle_from_vertical(shoulder - hip)


def _line_tilt(v: np.ndarray) -> float:
    """Одступање линије од хоризонтале, у [-90, 90]. 0 = равно.

    Знак: позитивно кад десна тачка иде наниже (већи y на слици).
    """
    deg = float(np.degrees(np.arctan2(v[1], v[0])))
    if deg > 90.0:
        deg -= 180.0
    elif deg < -90.0:
        deg += 180.0
    return deg


def shoulder_tilt(lm: Landmarks) -> float:
    """Нагиб линије рамена од хоризонтале (степени, са знаком). За поглед спреда."""
    return _line_tilt(lm.xy("right_shoulder") - lm.xy("left_shoulder"))


def hip_tilt(lm: Landmarks) -> float:
    """Нагиб линије кукова од хоризонтале (степени, са знаком)."""
    return _line_tilt(lm.xy("right_hip") - lm.xy("left_hip"))
