"""Спаја кораке: силуете → резбарење → мрежа → размера → STL.

Размера је издвојена намерно: из слика се добија **облик**, не величина. Док се
не унесе једна измерена дужина, модел може бити и напрстак и буре.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from dvojnik import karving, mreza as m_mod, siluete as sil
from dvojnik.config import kamera_iz

log = logging.getLogger(__name__)


@dataclass
class Skeniranje:
    rezultat: karving.Rezultat
    trouglovi: np.ndarray
    faktor_razmere: float = 1.0
    izmerena_visina_mm: "float | None" = None

    @property
    def gabarit_mm(self) -> tuple:
        return m_mod.gabarit(self.trouglovi)

    @property
    def razmera_poznata(self) -> bool:
        return self.izmerena_visina_mm is not None

    def __str__(self) -> str:
        dx, dy, dz = self.gabarit_mm
        redovi = [
            f"Воксела: {self.rezultat.voksela}  "
            f"(запремина омотача {self.rezultat.zapremina_mm3 / 1000:.1f} cm³)",
            f"Троуглова: {len(self.trouglovi)}",
            f"Габарит: {dx:.1f} × {dy:.1f} × {dz:.1f} mm",
        ]
        if self.razmera_poznata:
            redovi.append(f"Размера постављена по измереној висини "
                          f"{self.izmerena_visina_mm:.1f} mm (×{self.faktor_razmere:.3f})")
        else:
            redovi.append(
                "РАЗМЕРА НИЈЕ ПОСТАВЉЕНА — величина је изведена из подешене "
                "геометрије камере. Измери предмет шублером и додај --visina-mm."
            )
        return "\n".join(redovi)


class Skener:
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self.kamera = kamera_iz(cfg)

    @property
    def granice(self) -> tuple:
        z = self.cfg.zapremina
        return karving.granice_oko_stola(z.precnik, z.visina)

    @property
    def podela(self) -> tuple:
        n = int(self.cfg.zapremina.podela)
        return (n, n, n)

    # --- кораци -----------------------------------------------------------

    def izdvoj_siluete(self, kadrovi, pozadina) -> list:
        s = self.cfg.silueta
        out = []
        for i, kadar in enumerate(kadrovi):
            m = sil.silueta(kadar, pozadina, s.prag, s.zatvaranje, s.samo_najveca)
            if not m.any():
                raise ValueError(
                    f"Кадар {i}: силуета је празна. Предмет се не разликује од "
                    f"позадине — спусти silueta.prag (сад {s.prag}) или промени позадину."
                )
            if sil.dodiruje_ivicu(m):
                log.warning(
                    "Кадар %d: предмет додирује ивицу слике. Резбарење ће га "
                    "одсећи — одмакни камеру или смањи предмет.", i
                )
            out.append(m)
        return out

    def slozi(self, siluete, uglovi, visina_mm: "float | None" = None) -> Skeniranje:
        """Силуете → воксели → троуглови, па по потреби на измерену висину."""
        rez = karving.izrezbari(
            siluete, uglovi, self.kamera, self.granice, self.podela,
            van_kadra_rezi=self.cfg.zapremina.van_kadra_rezi,
        )
        if not rez.zauzeto.any():
            raise ValueError(
                "После резбарења није остало ништа. Најчешће: предмет излази из "
                "кадра, праг силуете је превисок, или радни простор не поклапа сто."
            )
        if rez.odsecenih_van_kadra:
            log.warning("Одсечено %d воксела јер су испали из кадра",
                        rez.odsecenih_van_kadra)

        vrsta = self.cfg.mreza.vrsta
        if vrsta not in ("blokovska", "glatka"):
            raise ValueError(f"Непозната мрежа: '{vrsta}' (има: blokovska, glatka)")
        napravi = m_mod.glatka_mreza if vrsta == "glatka" else m_mod.blokovska_mreza
        trouglovi = napravi(rez.zauzeto, rez.granice, rez.korak)

        faktor = 1.0
        if visina_mm is not None:
            sirova = rez.visina_mm()
            if sirova <= 0:
                raise ValueError("Реконструкција нема висину — нема шта да се скалира")
            faktor = float(visina_mm) / sirova
            trouglovi = m_mod.skaliraj(trouglovi, faktor)
            log.info("Размера: реконструкција %.1f mm → измерено %.1f mm (×%.3f)",
                     sirova, visina_mm, faktor)

        return Skeniranje(
            rezultat=rez, trouglovi=trouglovi,
            faktor_razmere=faktor, izmerena_visina_mm=visina_mm,
        )

    # --- цео пут ----------------------------------------------------------

    def skeniraj(self, kadrovi, pozadina, uglovi,
                 visina_mm: "float | None" = None) -> Skeniranje:
        return self.slozi(self.izdvoj_siluete(kadrovi, pozadina), uglovi, visina_mm)
