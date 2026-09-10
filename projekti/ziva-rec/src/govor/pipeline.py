"""Спаја кораке: снимак → препис → оцена торлачности → предлог за исправку → корпус.

Исправка се овде не ради (то је ствар CLI-ја или, касније, веба) — pipeline само
припреми све што исправљачу треба и, кад добије исправљен текст, упише пар у
корпус.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import numpy as np

from govor import crte as crte_mod
from govor import recnik as recnik_mod
from govor.asr import Transkript, build_asr
from govor.audio import isecak
from govor.korpus import Korpus, Unos

log = logging.getLogger(__name__)


@dataclass
class StavkaZaIspravku:
    """Један сегмент преписа спреман да га говорник погледа."""

    redni: int
    pocetak: float
    kraj: float
    tekst_asr: str
    nalaz: crte_mod.Nalaz
    recnik_beleske: list = field(default_factory=list)  # ["съга — сада [...]", …]

    @property
    def skor(self) -> float:
        return self.nalaz.skor

    def __str__(self) -> str:
        red = [f"[{self.redni}] {self.pocetak:.1f}–{self.kraj:.1f}s  {self.tekst_asr}",
               f"    {self.nalaz.sazetak()}"]
        for b in self.recnik_beleske:
            red.append(f"    речник: {b}")
        return "\n".join(red)


@dataclass
class Sesija:
    transkript: Transkript
    stavke: list
    govornik_id: str
    samplerate: int

    @property
    def prosecan_skor(self) -> float:
        if not self.stavke:
            return 0.0
        return sum(s.skor for s in self.stavke) / len(self.stavke)

    def istaknute(self, prag: float) -> list:
        return [s for s in self.stavke if s.skor >= prag]


class Stanica:
    def __init__(self, cfg, *, asr=None, recnik=None) -> None:
        self.cfg = cfg
        self._asr = asr
        self.recnik = recnik if recnik is not None else recnik_mod.ucitaj(cfg.recnik or None)

    @property
    def asr(self):
        if self._asr is None:
            self._asr = build_asr(self.cfg.asr)
        return self._asr

    # --- препис + оцена --------------------------------------------------

    def obradi(self, audio, samplerate: int, govornik_id: str) -> Sesija:
        transkript = self.asr.transkribuj(audio, samplerate)
        stavke = []
        for i, seg in enumerate(transkript.segmenti):
            nalaz = crte_mod.oceni(seg.tekst, self.recnik)
            beleske = []
            for k in nalaz.recnik_pogoci:
                odr = self.recnik.nadji(nalaz.reci[k])
                if odr is not None:
                    beleske.append(odr.opis())
            stavke.append(StavkaZaIspravku(
                redni=i, pocetak=seg.pocetak, kraj=seg.kraj,
                tekst_asr=seg.tekst, nalaz=nalaz, recnik_beleske=beleske,
            ))
        return Sesija(transkript=transkript, stavke=stavke,
                      govornik_id=govornik_id, samplerate=samplerate)

    # --- упис у корпус ------------------------------------------------

    def sacuvaj_ispravku(self, korpus: Korpus, sesija: Sesija, audio,
                         redni: int, tekst_ispravljen: str,
                         odobreno: bool = False) -> Unos:
        """Један исправљен сегмент → нови унос у корпусу (са исечком звука)."""
        if redni < 0 or redni >= len(sesija.stavke):
            raise IndexError(f"Нема сегмента {redni} (има их {len(sesija.stavke)})")
        stavka = sesija.stavke[redni]

        trajanje = stavka.kraj - stavka.pocetak
        if trajanje < self.cfg.korpus.min_trajanje_s:
            raise ValueError(
                f"Сегмент траје {trajanje:.2f} s — краће од "
                f"{self.cfg.korpus.min_trajanje_s} s не иде у корпус"
            )
        if not tekst_ispravljen.strip():
            raise ValueError("Исправљен текст је празан")

        nalaz = crte_mod.oceni(tekst_ispravljen, self.recnik)
        crte_broj: dict = {}
        for oznake in nalaz.oznake:
            for cid in oznake:
                crte_broj[cid] = crte_broj.get(cid, 0) + 1

        unos = Unos(
            id=korpus._sledeci_id(),
            govornik_id=sesija.govornik_id,
            tekst_asr=stavka.tekst_asr,
            tekst_ispravljen=tekst_ispravljen.strip(),
            pocetak=stavka.pocetak,
            kraj=stavka.kraj,
            samplerate=sesija.samplerate,
            skor_torlacnosti=round(nalaz.skor, 3),
            crte=crte_broj,
            odobreno=odobreno,
        )
        deo = isecak(audio, sesija.samplerate, stavka.pocetak, stavka.kraj)
        korpus.dodaj_unos(unos, deo)
        log.info("Унос %s: „%s“ (скор %.2f)", unos.id,
                 tekst_ispravljen.strip()[:50], nalaz.skor)
        return unos

    def close(self) -> None:
        if self._asr is not None:
            try:
                self._asr.close()
            except Exception:  # pragma: no cover
                pass
