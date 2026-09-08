from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Prediction:
    label: str
    score: float


class Classifier:
    def classify(self, frame) -> "Prediction | None":  # pragma: no cover - интерфејс
        raise NotImplementedError

    def close(self) -> None:
        pass
