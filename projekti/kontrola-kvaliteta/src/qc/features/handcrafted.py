"""Ручно прављена обележја по блоку — без тешких библиотека, ради на Pi-ју.

За сваки од G×G блокова: [средња светлина, стд, средњи градијент, стд градијента,
хоризонтална и вертикална енергија ивица]. Мана (рупа, страно тело, прекид у
ткању) мења текстуру блока → дескриптор одскаче од научених исправних.
"""

from __future__ import annotations

import numpy as np

from qc.features.base import BlockFeatures, FeatureExtractor, resize, to_gray


class HandcraftedExtractor(FeatureExtractor):
    def __init__(self, cfg) -> None:
        self.size = cfg.image_size
        self.grid = cfg.grid

    def extract(self, image) -> BlockFeatures:
        gray = resize(to_gray(image), self.size) / 255.0
        gy, gx = np.gradient(gray)
        grad = np.hypot(gx, gy)

        g = self.grid
        step = self.size // g
        vecs = np.empty((g * g, 6), dtype=np.float32)
        idx = 0
        for by in range(g):
            for bx in range(g):
                ys = slice(by * step, (by + 1) * step)
                xs = slice(bx * step, (bx + 1) * step)
                b = gray[ys, xs]
                bg = grad[ys, xs]
                vecs[idx] = (
                    b.mean(), b.std(),
                    bg.mean(), bg.std(),
                    np.abs(gx[ys, xs]).mean(), np.abs(gy[ys, xs]).mean(),
                )
                idx += 1
        return BlockFeatures(vectors=vecs, grid=g)
