"""SLAM: од низа скенова до положаја возила и мапе.

Сваки нови скен се ICP-ом поравна на „мапу“ (последњих неколико скенова у
светском оквиру). Из поравнања се исправи процена положаја, па се скен уцрта
у occupancy grid. Scan-to-map, без одометрије.
"""

from __future__ import annotations

import logging
from collections import deque

import numpy as np

from mapa.grid import OccupancyGrid
from mapa.icp import icp
from mapa.pose import Pose, from_matrix
from mapa.scan import clean_scan, polar_to_points

log = logging.getLogger(__name__)


class Slam:
    def __init__(self, cfg, start: "Pose | None" = None) -> None:
        self.cfg = cfg
        self.grid = OccupancyGrid(cfg.grid)
        self.pose = start or Pose()   # почетни положај у оквиру мапе (подразумевано исходиште)
        self._keyframes: deque = deque(maxlen=cfg.slam.keyframes)
        self._last_delta = Pose()      # померај возила у претходном кораку (његов оквир)
        self.last_fitness = 0.0

    def update(self, angles_deg, ranges_mm) -> Pose:
        ang, rng = clean_scan(angles_deg, ranges_mm, self.cfg.lidar.min_mm, self.cfg.lidar.max_mm)
        pts_vehicle = polar_to_points(ang, rng, self.cfg.lidar.forward_offset_deg)
        if len(pts_vehicle) < self.cfg.icp.min_points:
            log.warning("Скен са само %d тачака — прескачем", len(pts_vehicle))
            return self.pose

        prev_pose = self.pose
        # константна брзина: претпостави да се возило кретало као у прошлом кораку
        predicted = self.pose.compose(self._last_delta)

        if self._keyframes:
            stride = max(1, len(pts_vehicle) // 70)   # ICP на проређеном скену — брже
            guess_world = predicted.transform(pts_vehicle[::stride])
            map_pts = np.vstack(list(self._keyframes))
            if len(map_pts) > 700:
                map_pts = map_pts[np.linspace(0, len(map_pts) - 1, 700).astype(int)]
            res = icp(
                guess_world, map_pts, init=None,
                max_iter=self.cfg.icp.max_iter, tol=self.cfg.icp.tol,
                max_pairs_dist=self.cfg.icp.max_pairs_dist,
            )
            self.last_fitness = res.fitness
            if res.fitness >= self.cfg.slam.min_fitness:
                self.pose = from_matrix(res.pose.as_matrix() @ predicted.as_matrix())
            else:
                log.warning("ICP слаб (fitness %.2f) — користим предвиђање", res.fitness)
                self.pose = predicted
        else:
            self.pose = predicted

        # ажурирај процену брзине (померај у оквиру претходног положаја)
        m = np.linalg.inv(prev_pose.as_matrix()) @ self.pose.as_matrix()
        self._last_delta = from_matrix(m)

        world_pts = self.pose.transform(pts_vehicle)
        self.grid.integrate((self.pose.x, self.pose.y), world_pts)
        self._keyframes.append(world_pts[:: self.cfg.slam.subsample])
        return self.pose
