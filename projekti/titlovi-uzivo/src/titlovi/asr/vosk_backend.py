"""ASR преко Vosk-а (Kaldi). Прави стриминг, најмање кашњење.

ВАЖНО: Vosk (проверено 08.09.2026) НЕМА званичан модел за српски. Овај backend
је ту за радионичке демонстрације на језицима који имају модел (руски,
украјински, енглески…) и за будући модел заједнице за српски. За српски
користите подразумевани `faster-whisper`.
"""

from __future__ import annotations

import json
import logging
import os

import numpy as np

from titlovi.asr.base import AsrBackend, Transcript

log = logging.getLogger(__name__)


class VoskBackend(AsrBackend):
    def __init__(self, cfg, samplerate: int = 16000) -> None:
        from vosk import KaldiRecognizer, Model, SetLogLevel

        SetLogLevel(-1)
        if not os.path.isdir(cfg.model_path):
            raise FileNotFoundError(
                f"Vosk модел није пронађен: {cfg.model_path}\n"
                f"Преузмите га са https://alphacephei.com/vosk/models и "
                f"распакујте у ту фасциклу."
            )
        log.info("Учитавам Vosk модел из %s…", cfg.model_path)
        self.model = Model(cfg.model_path)
        self.rec = KaldiRecognizer(self.model, samplerate)

    def accept(self, pcm_f32) -> "Transcript | None":
        frame = np.asarray(pcm_f32, dtype=np.float32).reshape(-1)
        pcm16 = (np.clip(frame, -1.0, 1.0) * 32767.0).astype(np.int16).tobytes()

        if self.rec.AcceptWaveform(pcm16):
            text = json.loads(self.rec.Result()).get("text", "").strip()
            if not text:
                return None
            return Transcript(text_add=text, partial="", endpoint=True)

        partial = json.loads(self.rec.PartialResult()).get("partial", "").strip()
        return Transcript(text_add="", partial=partial)

    def flush(self) -> "Transcript | None":
        text = json.loads(self.rec.FinalResult()).get("text", "").strip()
        if not text:
            return None
        return Transcript(text_add=text, partial="", endpoint=True)
