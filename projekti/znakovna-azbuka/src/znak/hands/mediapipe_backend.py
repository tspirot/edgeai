"""Тачке шаке преко MediaPipe Hands (21 тачка).

`mediapipe` ради на Raspberry Pi 5 на процесору. Ако није инсталиран, `build_detector`
подигне грешку — за рад без камере користи `--backend dummy` / `--sim`.
"""

from __future__ import annotations

import numpy as np

from znak.hands.base import HandDetector


class MediaPipeHands(HandDetector):
    def __init__(self, cfg) -> None:  # pragma: no cover - тешка зависност
        import mediapipe as mp

        self._hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=cfg.min_detection_conf,
            min_tracking_confidence=cfg.min_tracking_conf,
        )

    def detect(self, frame):  # pragma: no cover - тешка зависност
        import cv2

        h, w = frame.shape[:2]
        res = self._hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if not res.multi_hand_landmarks:
            return None
        lm = res.multi_hand_landmarks[0].landmark
        return np.array([[p.x * w, p.y * h] for p in lm], dtype=np.float64)

    def close(self) -> None:  # pragma: no cover
        self._hands.close()
