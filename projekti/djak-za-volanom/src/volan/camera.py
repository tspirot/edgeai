"""Извор слике: Picamera2, OpenCV или синтетичка трака. RGB uint8 (H, W, 3)."""

from __future__ import annotations

import logging

import numpy as np

log = logging.getLogger(__name__)


class Camera:
    def read(self) -> np.ndarray:
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        pass


class DummyCamera(Camera):
    """Синтетичка стаза: светла трака која се благо помера лево-десно."""

    def __init__(self, cfg) -> None:
        self.w, self.h = cfg.width, cfg.height
        self._t = 0

    def read(self) -> np.ndarray:
        self._t += 1
        img = np.full((self.h, self.w, 3), 30, dtype=np.uint8)
        center = int(self.w / 2 + 0.25 * self.w * np.sin(self._t / 25.0))
        half = max(2, self.w // 12)
        lo, hi = max(0, center - half), min(self.w, center + half)
        img[int(self.h * 0.5):, lo:hi, :] = 220
        return img


class OpenCvCamera(Camera):  # pragma: no cover - тражи хардвер
    def __init__(self, cfg) -> None:
        import cv2

        self._cv2 = cv2
        self._cap = cv2.VideoCapture(cfg.index)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, cfg.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cfg.height)
        if not self._cap.isOpened():
            raise RuntimeError(f"Камера {cfg.index} се не отвара")

    def read(self) -> np.ndarray:
        ok, bgr = self._cap.read()
        if not ok:
            raise RuntimeError("Нема слике са камере")
        return self._cv2.cvtColor(bgr, self._cv2.COLOR_BGR2RGB)

    def close(self) -> None:
        self._cap.release()


class Picamera2Camera(Camera):  # pragma: no cover - тражи хардвер
    def __init__(self, cfg) -> None:
        from picamera2 import Picamera2

        self._cam = Picamera2()
        c = self._cam.create_preview_configuration(
            main={"format": "RGB888", "size": (cfg.width, cfg.height)}
        )
        self._cam.configure(c)
        self._cam.start()

    def read(self) -> np.ndarray:
        return np.asarray(self._cam.capture_array())

    def close(self) -> None:
        self._cam.stop()


def build_camera(cfg) -> Camera:
    backend = (cfg.backend or "auto").lower()
    if backend == "dummy":
        return DummyCamera(cfg)
    if backend == "opencv":
        return OpenCvCamera(cfg)
    if backend == "picamera2":
        return Picamera2Camera(cfg)
    if backend == "auto":  # pragma: no cover
        for build in (Picamera2Camera, OpenCvCamera):
            try:
                return build(cfg)
            except Exception as exc:
                log.debug("%s недоступна: %s", build.__name__, exc)
        log.warning("Ниједна камера — DummyCamera")
        return DummyCamera(cfg)
    raise ValueError(f"Непознат camera backend: '{cfg.backend}'")
