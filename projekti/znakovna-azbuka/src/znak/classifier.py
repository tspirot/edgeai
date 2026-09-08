"""k-НН класификатор над нормализованим векторима тачака шаке.

Једноставан намерно — цео смисао радионице је да ученици виде како тачност
расте кад додају своје снимке у скуп података.
"""

from __future__ import annotations

import numpy as np


class KnnClassifier:
    def __init__(self, k: int = 5) -> None:
        self.k = max(1, k)
        self.X: "np.ndarray | None" = None
        self.y: list[str] = []

    def fit(self, X, y) -> "KnnClassifier":
        self.X = np.asarray(X, dtype=np.float32)
        self.y = [str(v) for v in y]
        if len(self.y) != len(self.X):
            raise ValueError("X и y различите дужине")
        return self

    def predict(self, vec) -> tuple[str, float]:
        if self.X is None or len(self.y) == 0:
            raise RuntimeError("Класификатор није научен (позови fit).")
        v = np.asarray(vec, dtype=np.float32)
        dist = np.linalg.norm(self.X - v, axis=1)
        k = min(self.k, len(dist))
        idx = np.argsort(dist)[:k]

        weights: dict[str, float] = {}
        for i in idx:
            weights[self.y[i]] = weights.get(self.y[i], 0.0) + 1.0 / (float(dist[i]) + 1e-6)
        total = sum(weights.values())
        label = max(weights, key=weights.get)
        return label, weights[label] / total

    # ------------------------------------------------------------------
    def save(self, path: str) -> None:
        np.savez(path, X=self.X, y=np.array(self.y), k=np.array(self.k))

    @classmethod
    def load(cls, path: str) -> "KnnClassifier":
        d = np.load(path, allow_pickle=False)
        obj = cls(k=int(d["k"]))
        obj.X = np.asarray(d["X"], dtype=np.float32)
        obj.y = [str(v) for v in d["y"]]
        return obj

    @property
    def labels(self) -> list[str]:
        return sorted(set(self.y))
