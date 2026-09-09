"""Заједнички уговор за детектор позе (кадар → тачке тела)."""

from __future__ import annotations

import numpy as np

from drzanje.landmarks import Landmarks


class PoseBackend:
    def detect(self, image: np.ndarray) -> "Landmarks | None":
        """Врати `Landmarks` или None ако особа није детектована."""
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        pass
