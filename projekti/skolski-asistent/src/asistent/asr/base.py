"""Заједнички уговор за ASR модуле (говор → текст питања)."""

from __future__ import annotations

import numpy as np


class AsrBackend:
    """Апстрактни модул. `transcribe` добија моно float32 снимак на 16 kHz."""

    def transcribe(self, audio: np.ndarray) -> str:  # pragma: no cover - интерфејс
        raise NotImplementedError

    def close(self) -> None:
        pass
