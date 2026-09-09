"""Ланац: камера → детектор позе → углови → монитор држања → подсетник + записник.

Са `dummy` модулима ради без камере и без модела — за пробу и тестове.
"""

from __future__ import annotations

import logging
import time

import numpy as np

from drzanje.angles import neck_angle, shoulder_tilt, hip_tilt, trunk_angle
from drzanje.landmarks import Landmarks
from drzanje.posture import PostureMonitor, Reference

log = logging.getLogger(__name__)


class Monitor:
    def __init__(self, cfg, *, camera=None, pose=None, feedback=None, reference=None) -> None:
        self.cfg = cfg
        self.camera = camera or _camera(cfg)
        self.pose = pose or _pose(cfg)
        self.feedback = feedback or _feedback(cfg)
        self.monitor = PostureMonitor(cfg.posture, reference)
        self._smooth: "Landmarks | None" = None
        self.max_neck_dev = 0.0
        self.max_trunk_dev = 0.0
        self._tilt_samples: list = []
        self._t0: float | None = None

    def _read_pose(self) -> "Landmarks | None":
        lm = self.pose.detect(self.camera.read())
        if lm is None:
            return None
        a = self.cfg.pose.smoothing
        if a > 0 and self._smooth is not None:
            lm = self._smooth.lerp(lm, 1.0 - a)   # a = тежина старог
        self._smooth = lm
        return lm

    def step(self, t: "float | None" = None):
        t = time.monotonic() if t is None else t
        if self._t0 is None:
            self._t0 = t
        lm = self._read_pose()
        if lm is None:
            return None

        side = self.cfg.pose.side
        neck = neck_angle(lm, side)
        trunk = trunk_angle(lm, side)
        status = self.monitor.update(neck, trunk, t)

        self.max_neck_dev = max(self.max_neck_dev, status.neck_dev)
        self.max_trunk_dev = max(self.max_trunk_dev, status.trunk_dev)
        if self.cfg.screening.enabled:
            self._tilt_samples.append((shoulder_tilt(lm), hip_tilt(lm)))
        if status.alert:
            self.feedback.remind()
        return status

    def run(self, seconds: "float | None" = None, max_steps: "int | None" = None):
        period = 1.0 / max(1, self.cfg.camera.fps)
        steps = 0
        t_end = None if seconds is None else time.monotonic() + seconds
        try:
            while True:
                if max_steps is not None and steps >= max_steps:
                    break
                if t_end is not None and time.monotonic() >= t_end:
                    break
                self.step()
                steps += 1
                time.sleep(period)  # pragma: no cover
        except KeyboardInterrupt:  # pragma: no cover
            pass
        return steps

    def session_summary(self) -> dict:
        dur = 0.0 if self._t0 is None else max(0.0, (self.monitor._t or self._t0) - self._t0)
        s = self.monitor.summary()
        s.update({
            "duration_s": round(dur, 1),
            "max_neck_dev": round(self.max_neck_dev, 1),
            "max_trunk_dev": round(self.max_trunk_dev, 1),
        })
        if self._tilt_samples:
            arr = np.asarray(self._tilt_samples)
            s["shoulder_tilt"] = round(float(arr[:, 0].mean()), 2)
            s["hip_tilt"] = round(float(arr[:, 1].mean()), 2)
        return s

    def close(self) -> None:
        for part in (self.camera, self.pose, self.feedback):
            try:
                part.close()
            except Exception:  # pragma: no cover
                pass


def calibrate(cfg, *, camera=None, pose=None, samples: int = 30) -> Reference:
    """Просек углова док ученик седи усправно → лична референца."""
    cam = camera or _camera(cfg)
    det = pose or _pose(cfg)
    necks, trunks = [], []
    try:
        for _ in range(samples * 3):
            lm = det.detect(cam.read())
            if lm is None:
                continue
            necks.append(neck_angle(lm, cfg.pose.side))
            trunks.append(trunk_angle(lm, cfg.pose.side))
            if len(necks) >= samples:
                break
    finally:
        if camera is None:
            cam.close()
        if pose is None:
            det.close()
    if len(necks) < max(3, samples // 3):
        raise RuntimeError("Премало добрих кадрова за калибрацију — провери камеру и осветљење.")
    return Reference(float(np.median(necks)), float(np.median(trunks)))


def _camera(cfg):
    from drzanje.camera import build_camera

    return build_camera(cfg.camera)


def _pose(cfg):
    from drzanje.pose import build_pose

    return build_pose(cfg.pose, fps=cfg.camera.fps)


def _feedback(cfg):
    from drzanje.feedback import build_feedback

    return build_feedback(cfg.feedback)
