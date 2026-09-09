"""Снимање питања са микрофона до тишине. `sounddevice` се увози лениво."""

from __future__ import annotations

import numpy as np


def _rms(block: np.ndarray) -> float:
    if block.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(block, dtype=np.float64))))


def record_question(asr_cfg) -> np.ndarray:
    """Слушај микрофон, врати моно float32 снимак питања (16 kHz).

    Снимање креће на први говор изнад прага и стаје после `silence_seconds`
    тишине или на `max_seconds`.
    """
    import sounddevice as sd

    sr = asr_cfg.samplerate
    block = max(1, int(sr * asr_cfg.block_ms / 1000))
    w = asr_cfg.whisper
    max_blocks = int(w.max_seconds * sr / block)
    silence_blocks = max(1, int(w.silence_seconds * sr / block))

    collected: list[np.ndarray] = []
    speaking = False
    quiet = 0

    with sd.InputStream(samplerate=sr, channels=1, dtype="float32", blocksize=block) as stream:
        for _ in range(max_blocks):
            data, _ = stream.read(block)
            mono = np.asarray(data, dtype=np.float32).reshape(-1)
            loud = _rms(mono) >= w.energy_threshold
            if loud:
                speaking = True
                quiet = 0
            elif speaking:
                quiet += 1
            if speaking:
                collected.append(mono)
            if speaking and quiet >= silence_blocks:
                break

    if not collected:
        return np.zeros(0, dtype=np.float32)
    return np.concatenate(collected)


def print_devices() -> None:
    import sounddevice as sd

    for i, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:
            print(f"[{i}] {dev['name']}  ({dev['max_input_channels']} ул. канала)")
