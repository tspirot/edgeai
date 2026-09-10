"""Палета ћилима и свођење слике на њу.

Дифузиони модел даје меке прелазе и хиљаде нијанси. Ћилим их нема — има онолико
боја колико има клубади вуне. Свођење на палету није украшавање него први корак
ка нечему што се уопште може исткати.

Вредности испод су **приближне**. Тачне се добијају мерењем на стварним
клубадима у школској радионици: сними узорке под истим светлом, узми просек
средишта сваког узорка и упиши га овде.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Boja:
    id: str
    naziv: str
    rgb: tuple  # (r, g, b), 0–255


# Црвена преовлађује, у више нијанси — то је одлика пиротског ћилима, па су
# овде три црвене, а по једна од осталих.
PALETA = (
    Boja("rujna", "рујна црвена", (142, 36, 32)),
    Boja("ciglasta", "цигласта црвена", (180, 68, 58)),
    Boja("visnjeva", "вишњева", (104, 28, 40)),
    Boja("crna", "црна", (28, 26, 23)),
    Boja("bela", "бела", (239, 231, 214)),
    Boja("zuta", "жута", (216, 169, 60)),
    Boja("plava", "плава", (43, 74, 111)),
    Boja("zelena", "зелена", (74, 107, 62)),
)

CRVENE = ("rujna", "ciglasta", "visnjeva")


def niz_boja(paleta=PALETA) -> np.ndarray:
    """Палета као низ облика (N, 3), float, за рачун растојања."""
    return np.array([b.rgb for b in paleta], dtype=np.float64)


def indeks_boje(boja_id: str, paleta=PALETA) -> int:
    for i, b in enumerate(paleta):
        if b.id == boja_id:
            return i
    raise KeyError(f"Непозната боја: '{boja_id}'")


def kvantizuj(slika, paleta=PALETA) -> np.ndarray:
    """Слика (H, W, 3) → индекси палете (H, W), по најближој боји у RGB-у.

    Растојање се рачуна у обичном RGB простору. То није перцептивно тачно, али
    је предвидиво и лако објашњиво — а палета је толико разређена да финије
    мере ништа не мењају.
    """
    arr = np.asarray(slika)
    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError(f"Очекивана слика (H, W, 3), добијено: {arr.shape}")
    pikseli = arr[:, :, :3].astype(np.float64)
    p = niz_boja(paleta)
    # (H, W, 1, 3) - (N, 3) → (H, W, N)
    razlike = pikseli[:, :, None, :] - p[None, None, :, :]
    return np.argmin((razlike ** 2).sum(axis=3), axis=2).astype(np.int16)


def u_sliku(indeksi, paleta=PALETA) -> np.ndarray:
    """Индекси палете (H, W) → слика (H, W, 3), uint8."""
    p = np.array([b.rgb for b in paleta], dtype=np.uint8)
    idx = np.asarray(indeksi)
    if idx.min(initial=0) < 0 or idx.max(initial=0) >= len(paleta):
        raise ValueError("Индекс изван палете")
    return p[idx]


def udeo(indeksi, paleta=PALETA) -> dict:
    """Удео сваке боје у површини, као речник id → удео (0–1)."""
    idx = np.asarray(indeksi).ravel()
    broj = np.bincount(idx, minlength=len(paleta))
    ukupno = max(int(broj.sum()), 1)
    return {b.id: float(broj[i]) / ukupno for i, b in enumerate(paleta)}


def crvena_preovladjuje(indeksi, paleta=PALETA, prag: float = 0.35) -> bool:
    """Да ли црвене нијансе заједно заузимају бар `prag` површине.

    Провера одлике, не правило — шара може да прође и без ње, али онда јој
    треба образложење.
    """
    u = udeo(indeksi, paleta)
    return sum(u.get(c, 0.0) for c in CRVENE) >= prag
