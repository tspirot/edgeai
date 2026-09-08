"""Меморија обележја исправних комада (PatchCore-идеја).

Чувамо дескрипторе свих блокова са исправних слика. Резултат аномалије блока =
растојање до најближег запамћеног дескриптора. Никад не видимо ману у тренингу —
па све што „изгледа нормално" даје мали резултат, а свако одступање велики.
"""

from __future__ import annotations

import numpy as np


class MemoryBank:
    def __init__(self, k: int = 1) -> None:
        self.k = max(1, k)
        self._bank: "np.ndarray | None" = None
        self.mean_: "np.ndarray | None" = None
        self.std_: "np.ndarray | None" = None

    # ------------------------------------------------------------------
    def fit(self, vectors: np.ndarray, coreset_fraction: float = 1.0) -> "MemoryBank":
        v = np.asarray(vectors, dtype=np.float32)
        self.mean_ = v.mean(axis=0)
        self.std_ = v.std(axis=0) + 1e-6
        v = self._normalize(v)
        if 0.0 < coreset_fraction < 1.0:
            v = _greedy_coreset(v, max(1, int(len(v) * coreset_fraction)))
        self._bank = v
        return self

    def score_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Резултат аномалије по блоку (растојање до k најближих у меморији)."""
        if self._bank is None:
            raise RuntimeError("MemoryBank није научен (позови fit).")
        q = self._normalize(np.asarray(vectors, dtype=np.float32))
        # (Nq, Nb) матрица растојања
        d2 = (
            np.sum(q * q, axis=1)[:, None]
            - 2.0 * q @ self._bank.T
            + np.sum(self._bank * self._bank, axis=1)[None, :]
        )
        d2 = np.maximum(d2, 0.0)
        k = min(self.k, d2.shape[1])
        nearest = np.partition(d2, k - 1, axis=1)[:, :k]
        return np.sqrt(nearest.mean(axis=1))

    def image_score(self, vectors: np.ndarray) -> float:
        return float(self.score_vectors(vectors).max())

    # ------------------------------------------------------------------
    def _normalize(self, v: np.ndarray) -> np.ndarray:
        return (v - self.mean_) / self.std_

    def to_dict(self) -> dict:
        return {"bank": self._bank, "mean": self.mean_, "std": self.std_, "k": np.array(self.k)}

    @classmethod
    def from_dict(cls, d) -> "MemoryBank":
        obj = cls(k=int(d["k"]))
        obj._bank = np.asarray(d["bank"], dtype=np.float32)
        obj.mean_ = np.asarray(d["mean"], dtype=np.float32)
        obj.std_ = np.asarray(d["std"], dtype=np.float32)
        return obj


def _greedy_coreset(v: np.ndarray, n: int) -> np.ndarray:
    """Приближан min-max подскуп: сваки нови узорак најдаљи од већ изабраних."""
    if n >= len(v):
        return v
    chosen = [0]
    dist = np.linalg.norm(v - v[0], axis=1)
    for _ in range(n - 1):
        idx = int(np.argmax(dist))
        chosen.append(idx)
        dist = np.minimum(dist, np.linalg.norm(v - v[idx], axis=1))
    return v[np.array(chosen)]
