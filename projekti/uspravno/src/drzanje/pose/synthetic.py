"""Синтетичке тачке тела за пробу и тестове.

`build_landmarks(neck_deg, trunk_deg, ...)` направи скелет (поглед са стране)
са задатим угловима врата и трупа. `SyntheticPose` их мења кроз време —
наизменично усправно и погрбљено.
"""

from __future__ import annotations

import numpy as np

from drzanje.landmarks import IDX, N_POINTS, Landmarks
from drzanje.pose.base import PoseBackend


def build_landmarks(
    neck_deg: float = 0.0,
    trunk_deg: float = 0.0,
    shoulder_tilt_deg: float = 0.0,
    hip_tilt_deg: float = 0.0,
    hip_y: float = 0.85,
    facing: str = "left",
    visibility: float = 0.95,
) -> Landmarks:
    """Направи скелет са задатим угловима (нормализоване координате)."""
    pts = np.zeros((N_POINTS, 3), dtype=float)
    pts[:, 2] = 0.1  # подразумевано ниска видљивост

    hip_mid = np.array([0.5, hip_y])
    trunk_len = 0.35
    tr = np.radians(trunk_deg)
    shoulder_mid = hip_mid + trunk_len * np.array([np.sin(tr), -np.cos(tr)])

    neck_len = 0.12
    nr = np.radians(neck_deg)
    # уво на видљивој страни; „напред“ је −x кад је facing='left'
    fwd = -1.0 if facing == "left" else 1.0
    ear = shoulder_mid + neck_len * np.array([fwd * np.sin(nr), -np.cos(nr)])

    half_sh = 0.09
    half_hip = 0.08
    st = np.radians(shoulder_tilt_deg)
    ht = np.radians(hip_tilt_deg)

    def put(name, xy, vis=visibility):
        i = IDX[name]
        pts[i, :2] = xy
        pts[i, 2] = vis

    put("nose", ear + np.array([fwd * 0.03, -0.02]))
    # видљива страна јасна, друга страна слабо видљива (профил)
    vis_far = 0.2
    if facing == "left":
        put("left_ear", ear)
        put("right_ear", ear + np.array([0.02, 0.0]), vis_far)
        put("left_shoulder", shoulder_mid + half_sh * np.array([np.cos(st), np.sin(st)]))
        put("right_shoulder", shoulder_mid - half_sh * np.array([np.cos(st), np.sin(st)]), vis_far)
        put("left_hip", hip_mid + half_hip * np.array([np.cos(ht), np.sin(ht)]))
        put("right_hip", hip_mid - half_hip * np.array([np.cos(ht), np.sin(ht)]), vis_far)
    else:
        put("right_ear", ear)
        put("left_ear", ear - np.array([0.02, 0.0]), vis_far)
        put("right_shoulder", shoulder_mid - half_sh * np.array([np.cos(st), np.sin(st)]))
        put("left_shoulder", shoulder_mid + half_sh * np.array([np.cos(st), np.sin(st)]), vis_far)
        put("right_hip", hip_mid - half_hip * np.array([np.cos(ht), np.sin(ht)]))
        put("left_hip", hip_mid + half_hip * np.array([np.cos(ht), np.sin(ht)]), vis_far)

    return Landmarks(pts)


class SyntheticPose(PoseBackend):
    """Наизменично усправно (~5 s) и погрбљено (~4 s)."""

    def __init__(self, pose_cfg=None, fps: int = 15, seed: int = 0) -> None:
        self.fps = fps
        self._n = 0
        self._rng = np.random.default_rng(seed)

    def detect(self, image):
        self._n += 1
        t = self._n / self.fps
        phase = t % 9.0
        slouch = phase >= 5.0
        neck = (22.0 if slouch else 4.0) + self._rng.normal(0, 1.0)
        trunk = (16.0 if slouch else 3.0) + self._rng.normal(0, 1.0)
        return build_landmarks(neck_deg=neck, trunk_deg=trunk)
