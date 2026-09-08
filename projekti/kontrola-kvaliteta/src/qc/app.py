"""Обука из фасцикли и оцена на тест скупу."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from qc.detect import AnomalyDetector

log = logging.getLogger(__name__)


@dataclass
class EvalResult:
    ok_total: int
    defect_total: int
    true_pos: int      # мана препозната
    false_pos: int     # исправан означен као мана
    threshold: float

    @property
    def recall(self) -> float:
        return self.true_pos / self.defect_total if self.defect_total else 0.0

    @property
    def false_alarm_rate(self) -> float:
        return self.false_pos / self.ok_total if self.ok_total else 0.0


def train(cfg, ok_images, val_images=None) -> AnomalyDetector:
    det = AnomalyDetector(cfg)
    det.fit(ok_images, val_images)
    log.info("Праг: %.4f (%d блокова у меморији)", det.threshold, len(det.bank._bank))
    return det


def evaluate(detector: AnomalyDetector, ok_images, defect_images) -> EvalResult:
    tp = sum(1 for im in defect_images if detector.predict(im).is_anomaly)
    fp = sum(1 for im in ok_images if detector.predict(im).is_anomaly)
    return EvalResult(len(ok_images), len(defect_images), tp, fp, detector.threshold)
