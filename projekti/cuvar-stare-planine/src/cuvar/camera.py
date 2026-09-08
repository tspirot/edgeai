"""Извор кадрова: камера, видео фајл, или "sim" (синтетичка сцена)."""

from __future__ import annotations

import numpy as np


class SimSource:
    """Тамна сцена; периодично „прође животиња" (светла мрља) па окидач ради."""

    def __init__(self, width=1280, height=720, fps=10.0, frames=300,
                 period=40, event_len=4) -> None:
        self.width, self.height, self.fps = width, height, fps
        self._n, self._period, self._event = frames, period, event_len

    def __iter__(self):
        h, w = self.height, self.width
        for i in range(self._n):
            frame = np.full((h, w, 3), 18, dtype=np.uint8)
            k = i % self._period
            if i > 10 and k < self._event:
                cx = int((k + 1) / (self._event + 1) * w)
                x0, x1 = max(0, cx - 70), min(w, cx + 70)
                frame[h // 3:2 * h // 3, x0:x1] = 205
            yield frame, i / self.fps

    def close(self) -> None:
        pass


class CvSource:
    def __init__(self, cap, fps) -> None:
        self._cap, self.fps = cap, fps
        self._i = 0

    def __iter__(self):
        import cv2  # noqa: F401

        while True:
            ok, frame = self._cap.read()
            if not ok:
                break
            yield frame, self._i / self.fps
            self._i += 1

    def close(self) -> None:
        self._cap.release()


def open_source(cfg):
    src = str(cfg.camera.source)
    if src == "sim":
        return SimSource(cfg.camera.width, cfg.camera.height, cfg.camera.fps)
    import cv2

    cap = cv2.VideoCapture(int(src) if src.isdigit() else src)
    if not cap.isOpened():
        raise RuntimeError(f"Не могу да отворим извор: {src}")
    return CvSource(cap, cap.get(cv2.CAP_PROP_FPS) or cfg.camera.fps)
