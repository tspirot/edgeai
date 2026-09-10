"""faster-whisper на Jetson-у.

Овде је намерно очекивано да транскрипт буде ЛОШ. Стандардни Whisper је учен на
стандардном српском и пиротски говор своди ка њему — „лебац“ постане „хлеб“,
постпозитивни члан нестане. Тај лош препис је полазна тачка коју говорник
исправља; исправљени парови (звук, текст) су оно због чега пројекат постоји.

После неколико стотина парова, Whisper се дообучи на рачунару са GPU (LoRA,
`docs/doobuka.md`) и врати на станицу. Тежине не долазе уз пакет.
"""

from __future__ import annotations

import logging
import time

import numpy as np

from govor.asr.base import AsrBackend, Segment, Transkript

log = logging.getLogger(__name__)


class WhisperAsr(AsrBackend):
    def __init__(self, cfg) -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Нема faster-whisper — `pip install -e \".[asr]\"`. "
                "За рад без модела: --asr dummy"
            ) from exc

        self.cfg = cfg
        putanja = cfg.model_dir or cfg.model
        log.info("Учитавам Whisper '%s' (%s, %s)…", putanja, cfg.device, cfg.compute_type)
        self.model = WhisperModel(
            putanja, device=cfg.device, compute_type=cfg.compute_type,
            download_root=cfg.download_root or None,
        )

    def transkribuj(self, audio, samplerate: int) -> Transkript:
        a = np.asarray(audio, dtype=np.float32)
        if a.ndim > 1:
            a = a.mean(axis=1)
        if samplerate != 16000:
            raise ValueError(
                f"Whisper тражи 16 kHz, добијено {samplerate}. Пресемплуј пре преписа."
            )
        if a.size == 0:
            return Transkript(segmenti=[], model=self.cfg.model)

        t0 = time.perf_counter()
        segmenti_iter, info = self.model.transcribe(
            a, language=self.cfg.language or None,
            beam_size=self.cfg.beam_size,
            vad_filter=self.cfg.vad_filter,
            condition_on_previous_text=False,   # спречава да модел „упегла“ дијалекат
        )
        segmenti = [
            Segment(pocetak=round(s.start, 2), kraj=round(s.end, 2), tekst=s.text.strip())
            for s in segmenti_iter
        ]
        log.info("Препис: %d сегмената, %.1f s звука за %.1f s",
                 len(segmenti), segmenti[-1].kraj if segmenti else 0.0,
                 time.perf_counter() - t0)
        return Transkript(segmenti=segmenti, jezik=info.language, model=self.cfg.model)
