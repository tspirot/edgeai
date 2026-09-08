"""Извор кадрова: камера, видео фајл, или "sim" (кадрови нису битни — dummy шаке)."""

from __future__ import annotations


class SimSource:
    def __init__(self, frames: int = 120, fps: float = 30.0) -> None:
        self._n = frames
        self.fps = fps

    def __iter__(self):
        for i in range(self._n):
            yield None, i / self.fps

    def close(self) -> None:
        pass


class CvSource:
    def __init__(self, cap, fps) -> None:
        self._cap, self.fps = cap, fps
        self._i = 0

    def __iter__(self):
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
        return SimSource()
    import cv2

    cap = cv2.VideoCapture(int(src) if src.isdigit() else src)
    if not cap.isOpened():
        raise RuntimeError(f"Не могу да отворим извор: {src}")
    return CvSource(cap, cap.get(cv2.CAP_PROP_FPS) or cfg.camera.fps)
