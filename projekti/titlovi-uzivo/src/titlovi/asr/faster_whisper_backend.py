"""ASR на самом уређају преко faster-whisper (CTranslate2).

Модел се преузме једном (`titlovi download-model`), после тога ради потпуно
офлајн — звук никад не напушта уређај. Ово је подразумевани backend јер Vosk
нема модел за српски, а Whisper подржава српски у оквиру вишејезичног модела.
"""

from __future__ import annotations

import logging

import numpy as np

from titlovi.asr.base import AsrBackend, Transcript
from titlovi.asr.streaming import LocalAgreement
from titlovi.asr.vad import EnergyVad

log = logging.getLogger(__name__)


class FasterWhisperBackend(AsrBackend):
    def __init__(self, cfg, samplerate: int = 16000) -> None:
        from faster_whisper import WhisperModel

        self.cfg = cfg
        self.sr = samplerate
        log.info("Учитавам Whisper модел '%s' (%s, %s)…",
                 cfg.model, cfg.device, cfg.compute_type)
        self.model = WhisperModel(
            cfg.model,
            device=cfg.device,
            compute_type=cfg.compute_type,
            download_root=cfg.download_root or None,
        )

        self._buf = np.zeros(0, dtype=np.float32)
        self._window = int(cfg.window_seconds * samplerate)
        self._step = int(cfg.step_seconds * samplerate)
        self._since_step = 0
        self._agree = LocalAgreement()
        self._vad = EnergyVad(samplerate, cfg.silence_seconds, cfg.energy_threshold)

    # ------------------------------------------------------------------
    def accept(self, pcm_f32) -> "Transcript | None":
        frame = np.asarray(pcm_f32, dtype=np.float32).reshape(-1)
        self._buf = np.concatenate([self._buf, frame])
        self._since_step += len(frame)

        info = self._vad.update(frame)
        overflow = len(self._buf) >= self._window
        due = self._since_step >= self._step

        if not (due or info["endpoint"] or overflow):
            return None
        self._since_step = 0

        words = self._transcribe(self._buf)
        newly, partial = self._agree.insert(words)

        if info["endpoint"] or overflow:
            # Заврши целину: потврди све, испразни прозор.
            newly = newly + self._agree.flush()
            partial_words: list[str] = []
            self._buf = np.zeros(0, dtype=np.float32)
            self._agree.reset()
            return Transcript(text_add=" ".join(newly), partial="", endpoint=True)

        return Transcript(text_add=" ".join(newly), partial=" ".join(partial))

    def flush(self) -> "Transcript | None":
        if len(self._buf) < int(0.2 * self.sr):
            return None
        words = self._transcribe(self._buf)
        self._agree.insert(words)
        rest = self._agree.flush()
        self._buf = np.zeros(0, dtype=np.float32)
        self._agree.reset()
        if not rest:
            return None
        return Transcript(text_add=" ".join(rest), partial="", endpoint=True)

    # ------------------------------------------------------------------
    def _transcribe(self, audio: np.ndarray) -> list[str]:
        if len(audio) < int(0.3 * self.sr):
            return []
        segments, _ = self.model.transcribe(
            audio,
            language=self.cfg.language,
            beam_size=self.cfg.beam_size,
            word_timestamps=False,
            condition_on_previous_text=False,
            vad_filter=False,
        )
        text = " ".join(seg.text.strip() for seg in segments).strip()
        return text.split()
