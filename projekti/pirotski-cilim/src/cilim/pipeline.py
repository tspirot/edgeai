"""Спаја кораке: камера → класификатор → генератор → правила → картон.

Сваки корак је заменљив модул. Са `--klasifikator dummy --generator pravila`
цео ланац ради без камере, без CUDA и без иједне преузете тежине.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from cilim import OGRADA, motivi as mot
from cilim import paleta as pal
from cilim import pravila as prv
from cilim.generator import build_generator
from cilim.karton import Karton
from cilim.klasifikator import Nalaz, build_klasifikator

log = logging.getLogger(__name__)


@dataclass
class Predlog:
    """Оно што уређај понуди ткаљи."""

    slika: np.ndarray        # (H, W, 3) uint8 — увећан картон, оно што се тка
    indeksi: np.ndarray      # (H, W) — исти садржај као индекси палете
    karton: Karton
    izvestaj: prv.Izvestaj
    motiv_id: "str | None"

    def __str__(self) -> str:
        red = [OGRADA, "", str(self.izvestaj), "", self.karton.rezime()]
        return "\n".join(red)


class Radionica:
    def __init__(self, cfg, *, katalog=None, klasifikator=None, generator=None) -> None:
        self.cfg = cfg
        self.katalog = katalog or mot.ucitaj(cfg.katalog or None)
        self._klasifikator = klasifikator
        self._generator = generator

    # Класификатор и генератор се праве тек кад затребају — читање шаре не
    # учитава дифузиони модел, ни обрнуто.
    @property
    def klasifikator(self):
        if self._klasifikator is None:
            self._klasifikator = build_klasifikator(self.katalog, self.cfg.klasifikator)
        return self._klasifikator

    @property
    def generator(self):
        if self._generator is None:
            self._generator = build_generator(self.katalog, self.cfg)
        return self._generator

    # --- читање шаре -------------------------------------------------------

    def procitaj(self, slika) -> "tuple[Nalaz, str]":
        """Препознај шару на слици и врати налаз плус текст за екран."""
        nalaz = self.klasifikator.prepoznaj(slika)
        prag = self.cfg.klasifikator.min_pouzdanost
        motiv = self.katalog.nadji(nalaz.motiv_id)

        if nalaz.pouzdanost < prag:
            tekst = (
                f"Нисам сигуран ({nalaz.pouzdanost:.0%}). "
                f"Личи на: {motiv.naziv}. Питај ткаљу."
            )
        else:
            tekst = f"{motiv.opis()} (поузданост {nalaz.pouzdanost:.0%})"
        return nalaz, tekst

    # --- предлог нове шаре -------------------------------------------------

    def smisli(self, skica=None, motiv_id=None, seed: int = 0) -> Predlog:
        """Скица → предлог шаре → правила заната → картон за ткање."""
        sirova = self.generator.napravi(skica=skica, motiv_id=motiv_id, seed=seed)
        indeksi = prv.primeni(sirova, self.cfg.pravila)

        k = self.cfg.karton
        karton = Karton.iz_indeksa(
            indeksi, k.redova, k.kolona, niti_po_celiji=k.niti_po_celiji
        )
        # Правило о најкраћем потезу важи тамо где се и мери — на мрежи картона,
        # не на пикселима. Дифузиони модел ситан детаљ провуче кроз пиксел-меру,
        # а овде му се сажимањем ионако губи траг; ово чисти оно што остане.
        karton.mreza = prv.ujednaci_simetricno(
            karton.mreza,
            self.cfg.pravila.min_niti,
            self.cfg.pravila.ogledalo_uspravno,
            self.cfg.pravila.ogledalo_vodoravno,
        )
        izvestaj = prv.proveri(karton.mreza, self.cfg.pravila.min_niti)
        if not izvestaj.izvodljivo():
            log.warning("Предлог је тешко изводљив на разбоју: %s", izvestaj)

        # Слика се цртa ИЗ картона, а не из шаре пре сажимања. Иначе посетилац
        # гледа једно а ткаља тка друго — чишћење картона заобли углове које
        # слика пуне резолуције још има.
        f = max(
            min(indeksi.shape[0] // karton.redova, indeksi.shape[1] // karton.kolona), 1
        )
        uvecan = np.repeat(np.repeat(karton.mreza, f, axis=0), f, axis=1)

        return Predlog(
            slika=pal.u_sliku(uvecan),
            indeksi=uvecan,
            karton=karton,
            izvestaj=izvestaj,
            motiv_id=motiv_id,
        )

    def close(self) -> None:
        for deo in (self._klasifikator, self._generator):
            if deo is None:
                continue
            try:
                deo.close()
            except Exception:  # pragma: no cover
                pass
