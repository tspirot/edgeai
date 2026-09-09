"""Pure pursuit — праћење пута.

Нађи тачку на путу на растојању „lookahead“ испред возила, па израчунај угао
волана бициклистичким моделом да возило стигне ту тачку.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mapa.pose import Pose


@dataclass
class Command:
    steer: float          # угао волана (rad)
    speed: float          # 0..1
    done: bool
    target: "tuple[float, float] | None"


def _lookahead_point(pose: Pose, path, dist: float):
    """Прва тачка пута која је бар `dist` испред возила (по путањи)."""
    p = np.array([pose.x, pose.y])
    # одбаци тачке иза; крени од најближе
    d = [np.linalg.norm(np.array(pt) - p) for pt in path]
    start = int(np.argmin(d))
    for pt in path[start:]:
        if np.linalg.norm(np.array(pt) - p) >= dist:
            return np.array(pt, dtype=float)
    return np.array(path[-1], dtype=float)


def pure_pursuit(pose: Pose, path, cfg) -> Command:
    if not path:
        return Command(0.0, 0.0, True, None)

    goal = np.array(path[-1], dtype=float)
    if np.linalg.norm(goal - np.array([pose.x, pose.y])) <= cfg.goal_tol_m:
        return Command(0.0, 0.0, True, tuple(goal))

    target = _lookahead_point(pose, path, cfg.lookahead_m)

    # циљна тачка у оквиру возила
    dx, dy = target - np.array([pose.x, pose.y])
    c, s = np.cos(-pose.theta), np.sin(-pose.theta)
    lx = c * dx - s * dy
    ly = s * dx + c * dy

    ld = max(1e-3, np.hypot(lx, ly))
    curvature = 2.0 * ly / (ld * ld)                       # pure pursuit
    steer = float(np.arctan(cfg.wheelbase_m * curvature))
    steer = float(np.clip(steer, -cfg.max_steer_rad, cfg.max_steer_rad))

    speed = cfg.cruise_speed * (0.4 if lx <= 0 else 1.0)   # успори ако је циљ бочно/иза
    return Command(steer, speed, False, tuple(target))
