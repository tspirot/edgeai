"""Возило: даје скен и прима команду кретања. Симулирано или право.

Бициклистички модел: (x, y, θ) се мења по брзини и углу волана.
"""

from __future__ import annotations

import logging

import numpy as np

from mapa.pose import Pose, _wrap

log = logging.getLogger(__name__)


def bicycle_step(pose: Pose, steer: float, speed_mps: float, dt: float, wheelbase: float) -> Pose:
    x = pose.x + speed_mps * np.cos(pose.theta) * dt
    y = pose.y + speed_mps * np.sin(pose.theta) * dt
    th = _wrap(pose.theta + speed_mps / max(wheelbase, 1e-3) * np.tan(steer) * dt)
    return Pose(float(x), float(y), th)


class Robot:
    def sense(self):
        raise NotImplementedError  # pragma: no cover

    def move(self, steer: float, speed: float, dt: float) -> None:
        raise NotImplementedError  # pragma: no cover

    def stop(self) -> None:
        self.move(0.0, 0.0, 0.0)

    def close(self) -> None:
        self.stop()


class SimRobot(Robot):
    def __init__(self, sim_lidar, start: Pose, wheelbase: float, speed_scale: float = 1.0) -> None:
        self._lidar = sim_lidar
        self.true_pose = start
        self.wheelbase = wheelbase
        self.speed_scale = speed_scale     # команда 0..1 → m/s

    def sense(self):
        return self._lidar.scan(self.true_pose)

    def move(self, steer: float, speed: float, dt: float) -> None:
        self.true_pose = bicycle_step(
            self.true_pose, steer, speed * self.speed_scale, dt, self.wheelbase
        )


class RealRobot(Robot):  # pragma: no cover - тражи хардвер
    def __init__(self, scan_source, actuator, speed_scale: float = 1.0) -> None:
        self._scan = scan_source
        self._act = actuator
        self.speed_scale = speed_scale

    def sense(self):
        return self._scan.read()

    def move(self, steer: float, speed: float, dt: float) -> None:
        self._act.drive(steer, speed)

    def close(self) -> None:
        try:
            self._act.drive(0.0, 0.0)
            self._scan.close()
        except Exception:
            pass
