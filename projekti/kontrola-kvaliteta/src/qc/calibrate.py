"""Одређивање прага из резултата на исправним комадима (валидациони скуп)."""

from __future__ import annotations

import numpy as np


def threshold_from_ok(ok_scores, method: str = "sigma", sigma_k: float = 4.0,
                      percentile: float = 99.0) -> float:
    s = np.asarray(list(ok_scores), dtype=np.float64)
    if s.size == 0:
        raise ValueError("Нема резултата исправних комада за калибрацију.")
    if method == "percentile":
        return float(np.percentile(s, percentile))
    if method == "sigma":
        return float(s.mean() + sigma_k * s.std())
    raise ValueError(f"Непознат метод прага: '{method}'")
