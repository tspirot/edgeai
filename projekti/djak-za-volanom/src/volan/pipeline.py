"""Петља вожње: камера → политика → сигурносни арбитар (лидар) → актуатори.

Са `dummy` модулима цео ланац ради без хардвера — за пробу и тестове.
"""

from __future__ import annotations

import logging
import time

from volan.lidar import build_lidar, nearest_in_cone
from volan.policy import build_policy
from volan.safety import SafetyArbiter

log = logging.getLogger(__name__)


class DriveLoop:
    def __init__(self, cfg, *, camera=None, policy=None, lidar=None, actuator=None) -> None:
        self.cfg = cfg
        self.camera = camera or _default_camera(cfg)
        self.policy = policy or build_policy(cfg.model)
        self.lidar = lidar or build_lidar(cfg.lidar)
        self.actuator = actuator or _default_actuator(cfg)
        self.arbiter = SafetyArbiter(cfg.safety, cfg.drive.max_throttle)
        self._stop = False

    def _shape_steer(self, steer: float) -> float:
        d = self.cfg.drive
        s = steer * d.steer_gain + d.steer_trim
        if d.invert_steer:
            s = -s
        return max(-1.0, min(1.0, s))

    def step(self):
        """Један циклус одлучивања. Враћа Decision."""
        image = self.camera.read()
        m_steer, m_throttle = self.policy.predict(image)

        scan, ts = self.lidar.latest()
        nearest = nearest_in_cone(
            scan, self.cfg.lidar.cone_deg, self.cfg.lidar.forward_offset_deg,
            self.cfg.lidar.min_valid_mm, self.cfg.lidar.max_range_mm,
        )
        age = max(0.0, time.monotonic() - ts) if ts else 999.0

        decision = self.arbiter.step(self._shape_steer(m_steer), m_throttle, nearest, age)
        self.actuator.drive(decision.steer, decision.throttle)
        return decision

    def run(self, max_steps: "int | None" = None) -> int:
        period = 1.0 / self.cfg.drive.hz
        steps = 0
        try:
            while not self._stop and (max_steps is None or steps < max_steps):
                t0 = time.monotonic()
                d = self.step()
                steps += 1
                if steps % int(self.cfg.drive.hz) == 0:
                    log.info("волан %+.2f  гас %.2f  %s", d.steer, d.throttle, d.reason)
                dt = time.monotonic() - t0
                if dt < period and max_steps is None:  # pragma: no cover
                    time.sleep(period - dt)
        except KeyboardInterrupt:  # pragma: no cover
            pass
        finally:
            self.close()
        return steps

    def stop(self) -> None:
        self._stop = True

    def close(self) -> None:
        for part in (self.actuator, self.camera, self.lidar, self.policy):
            try:
                part.close()
            except Exception:  # pragma: no cover
                pass


def _default_camera(cfg):
    from volan.camera import build_camera

    return build_camera(cfg.camera)


def _default_actuator(cfg):
    from volan.actuators import build_actuator

    return build_actuator(cfg.actuator)
