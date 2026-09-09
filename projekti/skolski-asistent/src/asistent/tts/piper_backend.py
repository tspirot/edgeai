"""Piper TTS — синтеза говора на српском, локално.

Глас (нпр. `sr_RS-serbian-medium`) се преузме једном у `models/piper`.
Ако звучник није доступан, одговор се и даље исписује у терминал.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from asistent.tts.base import TtsBackend

log = logging.getLogger(__name__)


class PiperTts(TtsBackend):
    def __init__(self, tts_cfg) -> None:
        from piper import PiperVoice

        self.cfg = tts_cfg
        onnx = Path(tts_cfg.model_path) / f"{tts_cfg.voice}.onnx"
        if not onnx.exists():
            raise FileNotFoundError(
                f"Piper глас не постоји: {onnx}. "
                "`asistent download-model --what tts`"
            )
        self._voice = PiperVoice.load(str(onnx))

    def say(self, text: str) -> None:
        print(f"\n🔊 {text}\n")
        pcm = np.frombuffer(b"".join(self._voice.synthesize_stream_raw(text)), dtype=np.int16)
        try:
            import sounddevice as sd

            sd.play(pcm, samplerate=self._voice.config.sample_rate)
            sd.wait()
        except Exception as exc:  # pragma: no cover - зависи од звучника
            log.warning("Не могу да пустим звук (%s); одговор је исписан.", exc)
