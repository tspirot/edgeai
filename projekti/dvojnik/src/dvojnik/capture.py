"""Камера и слике са диска. Издвојено да остатак ради и без OpenCV-а."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_image(putanja) -> np.ndarray:
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


def ucitaj_snimak(folder) -> tuple:
    """Фолдер снимања → (кадрови, позадина, углови).

    Очекује `pozadina.png` и `kadar_000_ugao_0.0.png` какве пише `dvojnik snimi`.
    """
    p = Path(folder)
    pozadina = p / "pozadina.png"
    if not pozadina.exists():
        raise FileNotFoundError(
            f"Нема {pozadina}. Снимак увек почиње празном позадином — без ње се "
            "силуета не може издвојити."
        )
    kadrovi, uglovi = [], []
    for fajl in sorted(p.glob("kadar_*.png")):
        delovi = fajl.stem.split("_")
        try:
            uglovi.append(float(delovi[delovi.index("ugao") + 1]))
        except (ValueError, IndexError):
            raise ValueError(
                f"Име кадра нема угао: {fajl.name} "
                "(очекивано: kadar_000_ugao_0.0.png)"
            ) from None
        kadrovi.append(load_image(fajl))
    if not kadrovi:
        raise FileNotFoundError(f"У {p} нема ниједног kadar_*.png")
    return kadrovi, load_image(pozadina), uglovi


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
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.cap = None

    def __enter__(self) -> "Camera":
        import cv2

        self.cap = cv2.VideoCapture(self.cfg.index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Камера {self.cfg.index} се не отвара.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cfg.sirina)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cfg.visina)
        # Аутофокус и аутоекспозиција морају да мирују: ако се слика мења између
        # кадрова, одузимање позадине пријави ту промену као део предмета.
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        for _ in range(self.cfg.zagrevanje):
            self.cap.read()
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
