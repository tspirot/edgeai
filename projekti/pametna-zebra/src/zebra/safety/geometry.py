"""Геометрија судара — чисте функције, лако се тестирају.

Ради у произвољним јединицама (пиксели или метри) — важно је да позиције,
брзине и полупречник буду у истим јединицама.
"""

from __future__ import annotations

import math

Vec = "tuple[float, float]"


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def time_to_conflict(pos_a, vel_a, pos_b, vel_b, radius: float) -> float:
    """Време (s) док растојање два објекта не падне на `radius`.

    Претпоставка: константна брзина. Враћа 0 ако су већ ближе од `radius`,
    `inf` ако се путеви никад не приближе на `radius` или се удаљавају.
    """
    rx, ry = _sub(pos_a, pos_b)
    vx, vy = _sub(vel_a, vel_b)

    c = rx * rx + ry * ry - radius * radius
    if c <= 0.0:
        return 0.0  # већ у зони судара

    a = vx * vx + vy * vy
    if a <= 1e-12:
        return math.inf  # нема релативног кретања

    b = 2.0 * (rx * vx + ry * vy)
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return math.inf  # минимално растојање остаје веће од radius

    t = (-b - math.sqrt(disc)) / (2.0 * a)
    return t if t >= 0.0 else math.inf


def closest_approach(pos_a, vel_a, pos_b, vel_b) -> tuple[float, float]:
    """Врати (t*, d_min): тренутак и вредност најмањег растојања (константна брзина)."""
    rx, ry = _sub(pos_a, pos_b)
    vx, vy = _sub(vel_a, vel_b)
    a = vx * vx + vy * vy
    if a <= 1e-12:
        return (0.0, math.hypot(rx, ry))
    t = -(rx * vx + ry * vy) / a
    t = max(0.0, t)
    dx, dy = rx + vx * t, ry + vy * t
    return (t, math.hypot(dx, dy))


def speed(vel, meters_per_pixel: float = 1.0) -> float:
    """Интензитет брзине; уз `meters_per_pixel` даје m/s из px/s."""
    return math.hypot(vel[0], vel[1]) * meters_per_pixel
