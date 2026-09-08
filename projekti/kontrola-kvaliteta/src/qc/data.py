"""Учитавање слика из фасцикли и синтетички узорци за пробу/тестове."""

from __future__ import annotations

from pathlib import Path

import numpy as np

_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


def load_folder(directory: "str | Path") -> list[np.ndarray]:
    import cv2

    out = []
    for p in sorted(Path(directory).iterdir()):
        if p.suffix.lower() in _EXT:
            img = cv2.imread(str(p))
            if img is not None:
                out.append(img)
    return out


def synthetic_ok(n: int, size: int = 256, seed: int = 0, texture: float = 8.0):
    """Исправан комад: равномерна сива подлога са ситном текстуром (шум + пруге)."""
    rng = np.random.default_rng(seed)
    imgs = []
    xx = np.linspace(0, 6 * np.pi, size)
    stripes = 6.0 * np.sin(xx)[None, :]
    for _ in range(n):
        base = 128.0 + stripes + rng.normal(0, texture, (size, size))
        imgs.append(np.clip(base, 0, 255).astype(np.uint8))
    return imgs


def synthetic_defect(size: int = 256, seed: int = 100, kind: str = "hole"):
    """Комад са маном: рупа (тамна мрља), страно тело (светла мрља) или прекид пруга."""
    img = synthetic_ok(1, size, seed)[0].astype(np.float32)
    rng = np.random.default_rng(seed)
    cy, cx = rng.integers(40, size - 40, 2)
    r = rng.integers(12, 22)
    ys, xs = np.ogrid[:size, :size]
    mask = (ys - cy) ** 2 + (xs - cx) ** 2 <= r * r
    if kind == "hole":
        img[mask] = 20
    elif kind == "foreign":
        img[mask] = 245
    else:  # "smudge" — размазан део
        img[mask] = img[mask].mean()
    return np.clip(img, 0, 255).astype(np.uint8)
