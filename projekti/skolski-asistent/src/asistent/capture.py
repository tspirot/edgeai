"""Слика са камере или из фајла — увек као RGB низ (H, W, 3), uint8.

OpenCV се увози тек кад затреба, да тестови и rag/индексирање раде без њега.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_image(path: "str | Path") -> np.ndarray:
    """Учитај слику са диска у RGB uint8 низ (H, W, 3)."""
    from PIL import Image

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Слика не постоји: {p}")
    with Image.open(p) as im:
        return np.asarray(im.convert("RGB"), dtype=np.uint8)


class Camera:
    """Контекст менаџер око USB камере.

    with Camera(cfg) as cam:
        frame = cam.grab()      # RGB uint8
    """

    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._cap = None

    def __enter__(self) -> "Camera":
        import cv2

        cap = cv2.VideoCapture(self.cfg.index)
        if not cap.isOpened():
            raise RuntimeError(
                f"Камера {self.cfg.index} се не отвара. `asistent devices` за листу."
            )
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.height)
        self._cap = cap
        for _ in range(max(0, self.cfg.warmup_frames)):
            cap.read()
        return self

    def grab(self) -> np.ndarray:
        import cv2

        ok, bgr = self._cap.read()
        if not ok:
            raise RuntimeError("Не стиже слика са камере.")
        return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    def __exit__(self, *exc) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None


def list_cameras(max_index: int = 8) -> list[int]:
    """Индекси камера које се отварају (груба провера)."""
    import cv2

    found = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            found.append(i)
        cap.release()
    return found
