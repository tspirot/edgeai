"""Детектор аномалија: екстрактор обележја + меморија + праг + топлотна мапа."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from qc.bank import MemoryBank
from qc.calibrate import threshold_from_ok
from qc.features import build_extractor


@dataclass
class Result:
    is_anomaly: bool
    score: float
    threshold: float
    heatmap: np.ndarray  # G×G резултат по блоку


class AnomalyDetector:
    def __init__(self, cfg, extractor=None) -> None:
        self.cfg = cfg
        self.extractor = extractor if extractor is not None else build_extractor(cfg.features)
        self.bank = MemoryBank(k=cfg.bank.k)
        self.threshold: float = float("inf")
        self.grid = cfg.features.grid

    def fit(self, ok_images, val_images=None) -> "AnomalyDetector":
        all_vectors = [self.extractor.extract(im).vectors for im in ok_images]
        if not all_vectors:
            raise ValueError("Нема исправних слика за учење.")
        self.bank.fit(np.vstack(all_vectors), self.cfg.bank.coreset_fraction)

        calib = val_images if val_images is not None else ok_images
        ok_scores = [self.bank.image_score(self.extractor.extract(im).vectors) for im in calib]
        self.threshold = threshold_from_ok(
            ok_scores, self.cfg.threshold.method,
            self.cfg.threshold.sigma_k, self.cfg.threshold.percentile,
        )
        return self

    def predict(self, image) -> Result:
        vecs = self.extractor.extract(image).vectors
        block_scores = self.bank.score_vectors(vecs)
        score = float(block_scores.max())
        heatmap = block_scores.reshape(self.grid, self.grid)
        return Result(score > self.threshold, score, self.threshold, heatmap)

    # ------------------------------------------------------------------
    def save(self, path: str) -> None:
        d = self.bank.to_dict()
        np.savez(path, threshold=np.array(self.threshold), grid=np.array(self.grid), **d)

    @classmethod
    def load(cls, path: str, cfg, extractor=None) -> "AnomalyDetector":
        data = np.load(path, allow_pickle=False)
        obj = cls(cfg, extractor=extractor)
        obj.bank = MemoryBank.from_dict(
            {"bank": data["bank"], "mean": data["mean"], "std": data["std"], "k": data["k"]}
        )
        obj.threshold = float(data["threshold"])
        obj.grid = int(data["grid"])
        return obj
