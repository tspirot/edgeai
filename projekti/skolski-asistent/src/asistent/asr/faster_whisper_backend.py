"""faster-whisper — препознавање говора на самом уређају.

Модел се преузме једном (`asistent download-model --what asr`), после тога ради
офлајн. На Jetson Orin-у ставити `device: cuda` у конфигурацију.
"""

from __future__ import annotations

import logging

import numpy as np

from asistent.asr.base import AsrBackend

log = logging.getLogger(__name__)


class FasterWhisperAsr(AsrBackend):
    def __init__(self, whisper_cfg, samplerate: int = 16000) -> None:
        from faster_whisper import WhisperModel

        self.cfg = whisper_cfg
        self.sr = samplerate
        log.info("Учитавам Whisper '%s' (%s)…", whisper_cfg.model, whisper_cfg.compute_type)
        self._model = WhisperModel(
            whisper_cfg.model,
            device=whisper_cfg.device,
            compute_type=whisper_cfg.compute_type,
            download_root=whisper_cfg.download_root or None,
        )

    def transcribe(self, audio: np.ndarray) -> str:
        audio = np.asarray(audio, dtype=np.float32).reshape(-1)
        if audio.size < self.sr * 0.2:  # краће од 200 ms — нема питања
            return ""
        segments, _ = self._model.transcribe(
            audio,
            language=self.cfg.language,
            beam_size=1,
            vad_filter=True,
        )
        return " ".join(seg.text.strip() for seg in segments).strip()
