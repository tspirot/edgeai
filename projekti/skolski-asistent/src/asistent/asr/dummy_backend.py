"""Лажни ASR — врати унапред задато питање, без микрофона и без модела.

За пробу целог ланца и за аутоматске тестове.
"""

from __future__ import annotations

import numpy as np

from asistent.asr.base import AsrBackend


class DummyAsr(AsrBackend):
    def __init__(self, asr_cfg=None, text: str = "Шта показује ова шема?") -> None:
        self.text = getattr(asr_cfg, "dummy_text", None) or text

    def transcribe(self, audio: np.ndarray) -> str:
        return self.text
