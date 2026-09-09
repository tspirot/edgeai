"""MediaPipe Pose — 33 тачке тела, локално на процесору.

Ради ~15 FPS на Raspberry Pi 5. Модел се преузме уз пакет `mediapipe`.
"""

from __future__ import annotations

import logging

import numpy as np

from drzanje.landmarks import N_POINTS, Landmarks
from drzanje.pose.base import PoseBackend

log = logging.getLogger(__name__)


class MediaPipePose(PoseBackend):
    def __init__(self, pose_cfg) -> None:
        import mediapipe as mp

        self.cfg = pose_cfg
        self._pose = mp.solutions.pose.Pose(
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def detect(self, image: np.ndarray) -> "Landmarks | None":
        res = self._pose.process(np.asarray(image, dtype=np.uint8))
        if not res.pose_landmarks:
            return None
        pts = np.zeros((N_POINTS, 3), dtype=float)
        for i, lm in enumerate(res.pose_landmarks.landmark):
            pts[i] = (lm.x, lm.y, lm.visibility)
        return Landmarks(pts)

    def close(self) -> None:  # pragma: no cover
        self._pose.close()
