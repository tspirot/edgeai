"""Извори слике. Свака врати низ (frame, t_seconds).

- "sim"  → SimSource (без камере; frame је None, dummy детектор га игнорише)
- "0"…   → индекс камере (OpenCV)
- путања → видео фајл (OpenCV)
"""

from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)


class SimSource:
    def __init__(self, width: int = 1280, height: int = 720, fps: float = 30.0,
                 frames: int = 200) -> None:
        self.width = width
        self.height = height
        self.fps = fps
        self._n = frames

    def __iter__(self):
        for i in range(self._n):
            yield None, i / self.fps

    def close(self) -> None:
        pass


class CvSource:
    def __init__(self, cap, fps: float, realtime: bool) -> None:
        self._cap = cap
        self.fps = fps
        self._realtime = realtime
        self._i = 0

    def __iter__(self):
        import cv2  # noqa: F401  (осигурава да је OpenCV присутан)

        start = time.monotonic()
        while True:
            ok, frame = self._cap.read()
            if not ok:
                break
            t = self._i / self.fps
            self._i += 1
            if self._realtime:
                wait = t - (time.monotonic() - start)
                if wait > 0:
                    time.sleep(wait)
            yield frame, t

    def close(self) -> None:
        self._cap.release()


def open_source(cfg):
    src = str(cfg.video.source)
    if src == "sim":
        return SimSource(cfg.video.width, cfg.video.height, cfg.video.fps)

    import cv2

    is_camera = src.isdigit()
    cap = cv2.VideoCapture(int(src) if is_camera else src)
    if not cap.isOpened():
        raise RuntimeError(f"Не могу да отворим извор: {src}")
    if is_camera:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.video.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.video.height)
    fps = cap.get(cv2.CAP_PROP_FPS) or cfg.video.fps
    return CvSource(cap, fps, realtime=is_camera)
