"""Од воксела до фајла за штампач.

Подразумевано се прави **блоковска мрежа**: свака страница воксела која гледа у
празно постаје два троугла. Мрежа је затворена по конструкцији (свака унутрашња
страница се појави тачно једном, споља), нема ниједну зависност и штампа се без
поправљања. Изглед је степенаст — и то је поштено: тако систем стварно види
предмет.

Ко хоће глатко, инсталира `scikit-image` и добије marching cubes
(`pip install -e ".[glatko]"`). Глаткија мрежа није тачнија — само лепша.

STL се пише у бинарном облику, јер текстуални за исти модел буде и пет пута већи.
"""

from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

# Странице воксела: (померај суседа, четири темена странице у јединичној коцки)
_STRANICE = (
    ((-1, 0, 0), ((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))),
    ((1, 0, 0),  ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))),
    ((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))),
    ((0, 1, 0),  ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))),
    ((0, 0, -1), ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))),
    ((0, 0, 1),  ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))),
)


def _prazan_sused(zauzeto: np.ndarray, pomeraj) -> np.ndarray:
    """Где воксел има празног суседа у датом смеру (изван мреже = празно)."""
    sused = np.zeros_like(zauzeto)
    dx, dy, dz = pomeraj
    izvor = [slice(None)] * 3
    cilj = [slice(None)] * 3
    for osa, d in enumerate((dx, dy, dz)):
        if d > 0:
            cilj[osa], izvor[osa] = slice(0, -1), slice(1, None)
        elif d < 0:
            cilj[osa], izvor[osa] = slice(1, None), slice(0, -1)
    sused[tuple(cilj)] = zauzeto[tuple(izvor)]
    return zauzeto & ~sused


def blokovska_mreza(zauzeto, granice, korak) -> tuple:
    """Заузети воксели → (темена (M, 3, 3) по троуглу) у милиметрима."""
    zauzeto = np.asarray(zauzeto, dtype=bool)
    if zauzeto.ndim != 3:
        raise ValueError(f"Очекивана мрежа воксела (nx, ny, nz), добијено: {zauzeto.shape}")
    if not zauzeto.any():
        return np.zeros((0, 3, 3), dtype=np.float64)

    xmin, _, ymin, _, zmin, _ = (float(g) for g in granice)
    kx, ky, kz = (float(k) for k in korak)
    poreklo = np.array([xmin, ymin, zmin])
    veličina = np.array([kx, ky, kz])

    trouglovi = []
    for pomeraj, temena in _STRANICE:
        na_povrsini = _prazan_sused(zauzeto, pomeraj)
        idx = np.argwhere(na_povrsini)
        if idx.size == 0:
            continue
        ugao = poreklo + idx * veličina                    # (K, 3)
        t = [ugao + np.array(v) * veličina for v in temena]  # четири темена
        trouglovi.append(np.stack([t[0], t[1], t[2]], axis=1))
        trouglovi.append(np.stack([t[0], t[2], t[3]], axis=1))
    return np.concatenate(trouglovi, axis=0)


def glatka_mreza(zauzeto, granice, korak) -> tuple:  # pragma: no cover
    """Marching cubes преко scikit-image — глатка површина уместо степеница."""
    try:
        from skimage import measure
    except ImportError as exc:
        raise RuntimeError(
            "Глатка мрежа тражи scikit-image — `pip install -e \".[glatko]\"`. "
            "Блоковска мрежа ради без ичега."
        ) from exc

    zauzeto = np.asarray(zauzeto, dtype=bool)
    # Оквир од празних воксела, да marching cubes затвори тело на ивицама.
    prosireno = np.pad(zauzeto.astype(np.float32), 1)
    verteksi, lica, _, _ = measure.marching_cubes(prosireno, level=0.5)

    xmin, _, ymin, _, zmin, _ = (float(g) for g in granice)
    verteksi = (verteksi - 1.0) * np.array(korak) + np.array([xmin, ymin, zmin])
    return verteksi[lica]


def _normale(trouglovi: np.ndarray) -> np.ndarray:
    a = trouglovi[:, 1] - trouglovi[:, 0]
    b = trouglovi[:, 2] - trouglovi[:, 0]
    n = np.cross(a, b)
    duzine = np.linalg.norm(n, axis=1, keepdims=True)
    return np.divide(n, np.where(duzine < 1e-12, 1.0, duzine))


def u_stl(trouglovi, putanja, naziv: str = "dvojnik") -> Path:
    """Упиши бинарни STL. Јединица је милиметар — то штампачи и очекују."""
    t = np.asarray(trouglovi, dtype=np.float32)
    if t.ndim != 3 or t.shape[1:] != (3, 3):
        raise ValueError(f"Очекивано (M, 3, 3), добијено: {t.shape}")

    p = Path(putanja)
    p.parent.mkdir(parents=True, exist_ok=True)
    n = _normale(t.astype(np.float64)).astype(np.float32)

    with p.open("wb") as f:
        f.write(naziv.encode("ascii", "replace")[:80].ljust(80, b"\0"))
        f.write(struct.pack("<I", t.shape[0]))
        for normala, trougao in zip(n, t):
            f.write(normala.tobytes())
            f.write(trougao.tobytes())
            f.write(struct.pack("<H", 0))
    return p


def skaliraj(trouglovi, faktor: float) -> np.ndarray:
    """Помножи цео модел — овим се реконструкција доводи на измерену величину."""
    if faktor <= 0:
        raise ValueError("Фактор размере мора бити позитиван")
    return np.asarray(trouglovi, dtype=np.float64) * float(faktor)


def gabarit(trouglovi) -> tuple:
    t = np.asarray(trouglovi, dtype=np.float64)
    if t.size == 0:
        return (0.0, 0.0, 0.0)
    tacke = t.reshape(-1, 3)
    return tuple(float(x) for x in (tacke.max(axis=0) - tacke.min(axis=0)))
