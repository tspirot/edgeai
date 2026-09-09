"""Спаја кораке: слика + питање → (RAG) → VLM → говор.

Сваки корак је заменљив модул. Са свим `dummy`/`console` модулима цео ланац
ради без камере, микрофона и модела — за пробу и тестове.
"""

from __future__ import annotations

import logging

from asistent.asr import build_asr
from asistent.tts import build_tts
from asistent.vlm import Answer, build_vlm

log = logging.getLogger(__name__)


class _NullTts:
    """Ништа не изговара — када је `tts.speak` искључен."""

    def say(self, text: str) -> None:
        pass

    def close(self) -> None:
        pass


class Assistant:
    def __init__(self, cfg, *, asr=None, vlm=None, tts=None) -> None:
        self.cfg = cfg
        self.asr = asr or build_asr(cfg.asr)
        self.vlm = vlm or build_vlm(cfg.vlm)
        self.tts = tts or (build_tts(cfg.tts) if cfg.tts.speak else _NullTts())
        self._index = None
        self._embedder = None
        if cfg.rag.enabled:
            from asistent.rag import build_embedder, load_index

            self._index = load_index(cfg.rag.index_path)
            self._embedder = build_embedder(cfg.rag)
            log.info("RAG укључен: %d исечака у индексу", len(self._index.entries))

    # --- појединачни кораци ------------------------------------------------

    def transcribe(self, audio) -> str:
        return self.asr.transcribe(audio)

    def retrieve(self, question: str) -> list:
        if self._index is None:
            return []
        hits = self._index.search(
            question, self._embedder, self.cfg.rag.top_k, self.cfg.rag.min_score
        )
        for score, entry in hits:
            log.info("  RAG %.2f  %s", score, entry.source)
        return [entry.text for _, entry in hits]

    # --- цео одговор -----------------------------------------------------

    def ask(self, image, question: str) -> Answer:
        question = (question or "").strip()
        if not question:
            return Answer(text="Нисам чуо питање. Понови, молим те.")
        context = self.retrieve(question)
        answer = self.vlm.answer(image, question, context)
        if self.cfg.tts.speak:
            self.tts.say(answer.text)
        return answer

    def close(self) -> None:
        for part in (self.asr, self.vlm, self.tts):
            try:
                part.close()
            except Exception:  # pragma: no cover
                pass
