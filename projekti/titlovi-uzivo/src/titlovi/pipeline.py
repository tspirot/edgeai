"""Спаја аудио → ASR → приказ.

Аудио и препознавање раде у засебној нити; приказ (pygame мора на главној нити)
чита резултате из реда. Приказани текст се пресловљава према `text.script`.
"""

from __future__ import annotations

import logging
import queue
import threading

from titlovi.asr import build_backend
from titlovi.display import build_display
from titlovi.text import cyrillic_to_latin, latin_to_cyrillic

log = logging.getLogger(__name__)


def _tail_chars(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[-limit:]
    space = cut.find(" ")
    return cut[space + 1:] if space != -1 else cut


class Pipeline:
    def __init__(self, cfg, frames=None, display=None) -> None:
        self.cfg = cfg
        self._frames = frames        # низ блокова float32; None → микрофон
        self._display = display      # ubačен приказ (тестови)
        self._backend = build_backend(cfg.asr, cfg.audio.samplerate)
        self._queue: "queue.Queue" = queue.Queue()
        self._stop = threading.Event()

    def _to_script(self, text: str) -> str:
        script = self.cfg.text.script
        if script == "cyrillic":
            return latin_to_cyrillic(text)
        if script == "latin":
            return cyrillic_to_latin(text)
        return text

    def _worker(self, frames) -> None:
        try:
            for frame in frames:
                if self._stop.is_set():
                    break
                result = self._backend.accept(frame)
                if result is not None:
                    self._queue.put(result)
            final = self._backend.flush()
            if final is not None:
                self._queue.put(final)
        except BaseException as exc:  # noqa: BLE001 - прослеђујемо главној нити
            log.exception("Грешка у ASR нити")
            self._queue.put(exc)
        finally:
            self._queue.put(None)

    def run(self) -> str:
        display = self._display or build_display(self.cfg.display)
        mic = None
        if self._frames is not None:
            frames = self._frames
        else:
            from titlovi.audio import Microphone

            mic = Microphone(self.cfg.audio)
            mic.__enter__()
            frames = mic.frames()

        display.start()
        worker = threading.Thread(target=self._worker, args=(frames,), daemon=True)
        worker.start()

        committed = ""
        partial = ""
        try:
            while not display.should_quit():
                try:
                    item = self._queue.get(timeout=0.05)
                except queue.Empty:
                    display.render(self._to_script(committed), self._to_script(partial))
                    continue

                if item is None:
                    break
                if isinstance(item, BaseException):
                    raise item

                if item.text_add:
                    joined = f"{committed} {item.text_add}".strip()
                    committed = _tail_chars(joined, self.cfg.text.max_chars)
                partial = item.partial
                display.render(self._to_script(committed), self._to_script(partial))
        finally:
            self._stop.set()
            display.stop()
            if mic is not None:
                mic.__exit__(None, None, None)
            self._backend.close()

        return committed
