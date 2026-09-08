"""Извори звука: микрофон (уживо) и WAV фајл (проба/демо).

Оба враћају низ блокова: моно `numpy.float32` на 16 kHz, вредности у [-1, 1].
"""

from __future__ import annotations

import logging
import queue
import sys
import wave

import numpy as np

log = logging.getLogger(__name__)


def list_devices():
    import sounddevice as sd

    return sd.query_devices()


class Microphone:
    """Контекст-менаџер око `sounddevice.InputStream`."""

    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._q: "queue.Queue[np.ndarray]" = queue.Queue()
        self._stream = None

    def _callback(self, indata, frames, time_info, status) -> None:
        if status:
            log.warning("Аудио улаз: %s", status)
        mono = indata[:, 0] if indata.ndim > 1 else indata
        self._q.put(mono.astype(np.float32, copy=True))

    def __enter__(self) -> "Microphone":
        import sounddevice as sd

        block = max(1, int(self.cfg.samplerate * self.cfg.block_ms / 1000))
        self._stream = sd.InputStream(
            samplerate=self.cfg.samplerate,
            blocksize=block,
            device=self.cfg.device,
            channels=1,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()
        log.info("Микрофон отворен (%s Hz, блок %s узорака).",
                 self.cfg.samplerate, block)
        return self

    def __exit__(self, *exc) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def frames(self):
        while True:
            yield self._q.get()


def _resample_linear(x: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    if src_sr == dst_sr:
        return x
    n_dst = int(round(len(x) * dst_sr / src_sr))
    if n_dst <= 1:
        return x.astype(np.float32)
    src_t = np.linspace(0.0, 1.0, num=len(x), endpoint=False)
    dst_t = np.linspace(0.0, 1.0, num=n_dst, endpoint=False)
    return np.interp(dst_t, src_t, x).astype(np.float32)


def wav_frames(path: str, samplerate: int = 16000, block_ms: int = 100,
               realtime: bool = False):
    """Читај WAV (16-bit PCM) у блоковима, уз евентуално ресемпловање на 16 kHz."""
    import time

    with wave.open(path, "rb") as wf:
        src_sr = wf.getframerate()
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        if sampwidth != 2:
            raise ValueError("Подржан је само 16-битни PCM WAV.")
        block = max(1, int(src_sr * block_ms / 1000))
        while True:
            raw = wf.readframes(block)
            if not raw:
                break
            data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            if channels > 1:
                data = data.reshape(-1, channels).mean(axis=1)
            data = _resample_linear(data, src_sr, samplerate)
            if realtime:
                time.sleep(len(data) / samplerate)
            yield data


def print_devices(stream=sys.stdout) -> None:
    try:
        devs = list_devices()
    except Exception as e:  # pragma: no cover
        print(f"Не могу да прочитам аудио уређаје: {e}", file=stream)
        return
    print(devs, file=stream)
