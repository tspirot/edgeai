"""Лажни класификатор — за симулацију и тестове.

Позива се тек кад окидач по покрету пријави да нешто пролази. У симулацији то
значи да у кадру има светла мрља („животиња"); тада враћа врсту (ротира кроз
листу да галерија буде шаролика). За тестове се може дати `script`.
"""

from __future__ import annotations

import numpy as np

from cuvar.classify.base import Classifier, Prediction


class DummyClassifier(Classifier):
    def __init__(self, cfg=None, labels=None, script=None) -> None:
        self.labels = list(labels or (cfg.labels if cfg else ("srna", "lisica", "zec")))
        self.min_score = cfg.min_score if cfg else 0.5
        self.script = script
        self._i = -1

    def classify(self, frame) -> "Prediction | None":
        self._i += 1
        if self.script is not None:
            item = self.script[self._i] if self._i < len(self.script) else None
            return Prediction(*item) if item else None

        if frame is None or float(np.asarray(frame).max()) < 150:
            return None
        label = self.labels[self._i % len(self.labels)]
        score = round(0.7 + 0.2 * ((self._i * 37) % 10) / 10.0, 3)
        return Prediction(label, score) if score >= self.min_score else None
