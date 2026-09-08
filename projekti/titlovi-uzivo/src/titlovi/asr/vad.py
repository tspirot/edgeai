"""Најједноставнија детекција говора: праг енергије (RMS).

Довољно за одређивање краја реченице у учионици са пристојним микрофоном.
За бучне услове касније се може заменити Silero VAD-ом.
"""

from __future__ import annotations

import math


def rms(frame_f32) -> float:
    n = len(frame_f32)
    if n == 0:
        return 0.0
    total = 0.0
    for x in frame_f32:
        total += float(x) * float(x)
    return math.sqrt(total / n)


class EnergyVad:
    def __init__(self, samplerate: int = 16000, silence_seconds: float = 0.7,
                 threshold: float = 0.010) -> None:
        self.samplerate = samplerate
        self.silence_needed = silence_seconds
        self.threshold = threshold
        self._silence = 0.0
        self._had_speech = False

    def update(self, frame_f32) -> dict:
        """Врати {'rms', 'speech', 'endpoint'} за дати блок узорака."""
        try:
            import numpy as np
            level = float(np.sqrt(np.mean(np.square(np.asarray(frame_f32, dtype="float64"))))) \
                if len(frame_f32) else 0.0
        except Exception:  # pragma: no cover - fallback без numpy
            level = rms(frame_f32)

        duration = len(frame_f32) / self.samplerate
        is_speech = level >= self.threshold

        if is_speech:
            self._silence = 0.0
            self._had_speech = True
        else:
            self._silence += duration

        endpoint = self._had_speech and self._silence >= self.silence_needed
        if endpoint:
            self._had_speech = False
            self._silence = 0.0

        return {"rms": level, "speech": is_speech, "endpoint": endpoint}

    def reset(self) -> None:
        self._silence = 0.0
        self._had_speech = False
