"""Микрофон и WAV са диска. Издвојено да остатак ради без sounddevice-а."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from govor.korpus import ucitaj_wav


def load_audio(putanja) -> tuple:
    """WAV са диска → (сигнал float32 [-1,1], samplerate)."""
    p = Path(putanja)
    if not p.exists():
        raise FileNotFoundError(f"Звук не постоји: {p}")
    if p.suffix.lower() != ".wav":
        raise ValueError(f"Подржан је само WAV: {p.name}")
    return ucitaj_wav(p)


def isecak(audio, samplerate: int, pocetak: float, kraj: float) -> np.ndarray:
    """Део сигнала између две временске тачке (секунде)."""
    a = np.asarray(audio)
    i = max(int(pocetak * samplerate), 0)
    j = min(int(kraj * samplerate), a.size)
    if j <= i:
        raise ValueError(f"Празан исечак: {pocetak:.2f}–{kraj:.2f} s")
    return a[i:j]


def list_devices() -> list:  # pragma: no cover
    import sounddevice as sd

    return [
        {"index": i, "naziv": d["name"], "ulaza": d["max_input_channels"]}
        for i, d in enumerate(sd.query_devices())
        if d["max_input_channels"] > 0
    ]


def snimaj_do_tisine(cfg) -> np.ndarray:  # pragma: no cover — тражи микрофон
    """Снимај док говорник не заћути дуже од `audio.tisina_s`."""
    import sounddevice as sd

    sr = cfg.samplerate
    blok = int(sr * 0.1)
    tihо_blokova = 0
    treba_tihih = int(cfg.tisina_s / 0.1)
    maks_blokova = int(cfg.maks_s / 0.1)
    delovi = []

    with sd.InputStream(samplerate=sr, channels=cfg.kanali,
                        device=cfg.uredjaj, blocksize=blok, dtype="float32") as tok:
        cuo_govor = False
        for _ in range(maks_blokova):
            data, _ = tok.read(blok)
            uzorak = data[:, 0] if data.ndim > 1 else data
            delovi.append(uzorak.copy())
            rms = float(np.sqrt(np.mean(uzorak ** 2)))
            if rms >= cfg.prag_energije:
                cuo_govor = True
                tihо_blokova = 0
            elif cuo_govor:
                tihо_blokova += 1
                if tihо_blokova >= treba_tihih:
                    break
    return np.concatenate(delovi) if delovi else np.zeros(0, dtype=np.float32)
