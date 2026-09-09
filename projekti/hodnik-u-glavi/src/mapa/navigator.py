"""Навигација до тачке: SLAM → A* планер → pure pursuit → возило.

План се освежава сваких неколико корака (мапа расте, положај се исправља).
"""

from __future__ import annotations

import logging

import numpy as np

from mapa.planner import plan
from mapa.pursuit import pure_pursuit
from mapa.slam import Slam

log = logging.getLogger(__name__)


class Navigator:
    def __init__(self, cfg, robot, start=None) -> None:
        self.cfg = cfg
        self.robot = robot
        self.slam = Slam(cfg, start=start)
        self.path: list = []

    def drive_to(self, goal_xy, dt: float = 0.15, max_steps: int = 400, replan_every: int = 5):
        goal = np.asarray(goal_xy, dtype=float)
        reached = False
        for step in range(1, max_steps + 1):
            angles, ranges = self.robot.sense()
            pose = self.slam.update(angles, ranges)

            if step == 1 or step % replan_every == 0 or not self.path:
                self.path = plan(self.slam.grid, (pose.x, pose.y), tuple(goal), self.cfg.planner)

            if not self.path:
                log.warning("Нема пута до циља (корак %d) — стоп", step)
                self.robot.stop()
                return {"reached": False, "steps": step, "reason": "нема пута"}

            cmd = pure_pursuit(pose, self.path, self.cfg.pursuit)
            self.robot.move(cmd.steer, cmd.speed, dt)

            if cmd.done or np.linalg.norm(goal - np.array([pose.x, pose.y])) <= self.cfg.pursuit.goal_tol_m:
                reached = True
                break

        self.robot.stop()
        return {"reached": reached, "steps": step, "pose": self.slam.pose}
