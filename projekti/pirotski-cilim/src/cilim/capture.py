"""Камера и слике са диска.

Издвојено да остатак пакета ради и без OpenCV-а — тестови и `pravila` генератор
никад не додирну овај модул.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_image(putanja) -> np.ndarray:
    """Слика са диска као (H, W, 3) uint8, RGB."""
    from PIL import Image

    p = Path(putanja)
    if not p.exists():
        raise FileNotFoundError(f"Слика не постоји: {p}")
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.uint8)


def save_image(slika, putanja) -> Path:
    from PIL import Image

    p = Path(putanja)
    p.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.asarray(slika).astype(np.uint8), mode="RGB").save(p)
    return p


def list_cameras(maks: int = 5) -> list:  # pragma: no cover
    import cv2

    nadjene = []
    for i in range(maks):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            nadjene.append(i)
        cap.release()
    return nadjene


class Camera:  # pragma: no cover
    """USB камера изнад радне површине (C922)."""

    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.cap = None

    def __enter__(self) -> "Camera":
        import cv2

        self.cap = cv2.VideoCapture(self.cfg.index)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Камера {self.cfg.index} се не отвара. Провери `cilim devices`."
            )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.height)
        for _ in range(self.cfg.warmup_frames):
            self.cap.read()          # нека се аутофокус смири
        return self

    def grab(self) -> np.ndarray:
        import cv2

        ok, kadar = self.cap.read()
        if not ok:
            raise RuntimeError("Камера није дала кадар")
        return cv2.cvtColor(kadar, cv2.COLOR_BGR2RGB)

    def __exit__(self, *_) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None
