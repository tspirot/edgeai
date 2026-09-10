"""Резбарење воксела — језгро реконструкције.

Замисли коцку глине у радном простору. За сваки снимљени угао: све што се
пројектује ван силуете **није** предмет, па се одреже. После пуног круга остаје
оно што је у свакој силуети било унутра.

То је „визуелни омотач“ (visual hull) — најмање тело које баца исте сенке као
оригинал. Важно и поштено: удубљење које се са стране не види остаје попуњено.
Није грешка у коду него граница методе, и има свој тест који то тврди
(`test_karving.py::test_solja_ostaje_puna`).

Посао је очигледно паралелан — сваки воксел независно — што је тачно оно за шта
су CUDA језгра направљена. Овде је писано у NumPy-ју да се види шта се ради;
на Jetson-у се исти израз пребаци на GPU (`docs/na-jetsonu.md`).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from dvojnik.geometrija import Kamera, resetka, rotacija_z

log = logging.getLogger(__name__)


@dataclass
class Rezultat:
    zauzeto: np.ndarray        # (nx, ny, nz) bool
    granice: tuple
    korak: tuple
    odsecenih_van_kadra: int   # колико воксела је одсечено јер су испали из слике

    @property
    def voksela(self) -> int:
        return int(self.zauzeto.sum())

    @property
    def zapremina_mm3(self) -> float:
        kx, ky, kz = self.korak
        return self.voksela * kx * ky * kz

    def gabarit_mm(self) -> tuple:
        """Димензије оквира око преосталог тела (dx, dy, dz)."""
        if not self.zauzeto.any():
            return (0.0, 0.0, 0.0)
        kx, ky, kz = self.korak
        out = []
        for osa, korak in zip(range(3), (kx, ky, kz)):
            ose = tuple(i for i in range(3) if i != osa)
            ima = self.zauzeto.any(axis=ose)
            gde = np.flatnonzero(ima)
            out.append(float((gde[-1] - gde[0] + 1) * korak))
        return tuple(out)

    def visina_mm(self) -> float:
        return self.gabarit_mm()[2]


def izrezbari(siluete, uglovi, kamera: Kamera, granice, podela,
              van_kadra_rezi: bool = True) -> Rezultat:
    """Силуете + углови стола → заузети воксели.

    `van_kadra_rezi=True` значи: воксел који се не види ни у једном кадру не
    постоји. То тражи да предмет буде цео у слици на сваком углу — ако није,
    реконструкција ће бити одсечена, па се на то и упозорава.
    """
    siluete = list(siluete)
    uglovi = list(uglovi)
    if not siluete:
        raise ValueError("Нема ниједне силуете — нема шта да се резбари")
    if len(siluete) != len(uglovi):
        raise ValueError(
            f"Силуета има {len(siluete)}, а углова {len(uglovi)} — мора исто"
        )

    centri, korak = resetka(granice, podela)
    oblik = centri.shape[:3]
    tacke = centri.reshape(-1, 3)

    zauzeto = np.ones(tacke.shape[0], dtype=bool)
    odsecenih = 0

    for maska, ugao in zip(siluete, uglovi):
        m = np.asarray(maska, dtype=bool)
        if m.shape != (kamera.visina, kamera.sirina):
            raise ValueError(
                f"Силуета је {m.shape}, а камера даје "
                f"{(kamera.visina, kamera.sirina)}"
            )

        # Предмет се врти, камера мирује — исто као да се тачке заврте.
        u, v, dubina = kamera.projektuj(tacke @ rotacija_z(ugao).T)
        vidi_se = kamera.u_kadru(u, v, dubina)

        unutra = np.zeros_like(zauzeto)
        if vidi_se.any():
            uu = u[vidi_se].astype(np.int32)
            vv = v[vidi_se].astype(np.int32)
            unutra[vidi_se] = m[vv, uu]

        if not van_kadra_rezi:
            unutra |= ~vidi_se        # невиђено се не дира
        else:
            odsecenih += int((zauzeto & ~vidi_se).sum())

        zauzeto &= unutra
        if not zauzeto.any():
            log.warning("Све је одрезано на углу %.1f° — провери праг силуете "
                        "и границе радног простора", ugao)
            break

    return Rezultat(
        zauzeto=zauzeto.reshape(oblik),
        granice=tuple(float(g) for g in granice),
        korak=korak,
        odsecenih_van_kadra=odsecenih,
    )


def granice_oko_stola(precnik_mm: float, visina_mm: float) -> tuple:
    """Радни простор: ваљак око осе стола, задат пречником и висином."""
    if precnik_mm <= 0 or visina_mm <= 0:
        raise ValueError("Пречник и висина радног простора морају бити позитивни")
    r = precnik_mm / 2.0
    return (-r, r, -r, r, 0.0, float(visina_mm))
