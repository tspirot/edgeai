"""Лажни backend — исписује унапред задат текст сразмерно трајању звука.

Служи за пробу целог ланца (аудио → приказ) без микрофона и без модела,
и за аутоматске тестове.
"""

from __future__ import annotations

import numpy as np

from titlovi.asr.base import AsrBackend, Transcript

_SCRIPT = (
    "ovo je demonstracija titlova uzivo koji rade lokalno na uredjaju "
    "bez slanja zvuka u oblak zvuk se obradjuje na samom raspberry pi uredjaju "
    "i nikada ne napusta ucionicu"
).split()


class DummyBackend(AsrBackend):
    def __init__(self, cfg=None, samplerate: int = 16000,
                 words_per_second: float = 2.2) -> None:
        self.sr = samplerate
        self.wps = words_per_second
        self._elapsed = 0.0
        self._emitted = 0

    def accept(self, pcm_f32) -> "Transcript | None":
        self._elapsed += len(np.asarray(pcm_f32).reshape(-1)) / self.sr
        target = min(len(_SCRIPT), int(self._elapsed * self.wps))
        if target <= self._emitted:
            return None
        # све осим последње постаје потврђено, последња је "несигуран реп"
        confirmed = _SCRIPT[self._emitted:max(self._emitted, target - 1)]
        self._emitted = max(self._emitted, target - 1)
        partial = _SCRIPT[self._emitted] if self._emitted < len(_SCRIPT) else ""
        return Transcript(text_add=" ".join(confirmed), partial=partial)

    def flush(self) -> "Transcript | None":
        if self._emitted >= len(_SCRIPT):
            return None
        rest = _SCRIPT[self._emitted:]
        self._emitted = len(_SCRIPT)
        return Transcript(text_add=" ".join(rest), partial="", endpoint=True)
