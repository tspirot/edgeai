#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                    МОДЕЛ ПИРОТСКОГ ГОВОРА (API)
================================================================================
Овај модул учитава и користи научни речник САНУ (Драгољуб Златковић):
преко 2.700 аутентичних пиротских одредница, значења и реченица са терена.
Омогућава:
  - Брзу претрагу пиротских речи и израза
  - Обратну претрагу (српски појам -> пиротска реч)
  - Насумичне пиротске мудрости и примере
  - Обогаћивање AI одговора аутентичним дијалекатским корпусом
================================================================================
"""

import json
import re
import random
from pathlib import Path


def _cisti(txt: str) -> str:
    t = txt.lower()
    t = t.replace("ь", "")
    t = t.replace("`", "").replace("´", "").replace("’", "").replace("'", "")
    t = re.sub(r'[\,\.\;\:\!\?\"\(\)\[\]]', '', t)
    return t.strip()


class ModelPirotskogGovora:
    """Модел за рад са пиротским речником и корпусом примера."""

    def __init__(self, model_fajl: str | Path | None = None) -> None:
        if model_fajl is None:
            root = Path(__file__).resolve().parent
            model_fajl = root / "pirotski_model.json"
        
        self.putanja = Path(model_fajl)
        self.podaci = {}
        self.odrednice = []
        self.indeks_pirotski = {}
        self.indeks_srpski = {}
        self.svi_primeri = []
        self.ucitaj()

    def ucitaj(self) -> bool:
        if not self.putanja.exists():
            return False
        try:
            with open(self.putanja, "r", encoding="utf-8") as f:
                self.podaci = json.load(f)
            self.odrednice = self.podaci.get("odrednice", [])
            self.indeks_pirotski = self.podaci.get("indeks_pirotski", {})
            self.indeks_srpski = self.podaci.get("indeks_srpski", {})
            self.svi_primeri = self.podaci.get("svi_primeri", [])
            return True
        except Exception:
            return False

    @property
    def broj_odrednica(self) -> int:
        return len(self.odrednice)

    def nadji_pirotsku_rec(self, upit: str) -> list[dict]:
        """Тражи одредницу по пиротској речи или почетку речи."""
        cist_upit = _cisti(upit)
        if not cist_upit:
            return []

        rezultati = []
        # 1. Тачно поклапање у индексу
        if cist_upit in self.indeks_pirotski:
            for idx in self.indeks_pirotski[cist_upit]:
                rezultati.append(self.odrednice[idx])
            return rezultati

        # 2. Почетак речи (prefix match)
        for rec_k, indeksi in self.indeks_pirotski.items():
            if rec_k.startswith(cist_upit) or cist_upit in rec_k:
                for idx in indeksi:
                    if self.odrednice[idx] not in rezultati:
                        rezultati.append(self.odrednice[idx])
            if len(rezultati) >= 5:
                break

        return rezultati

    def nadji_srpski_pojam(self, pojam: str) -> list[dict]:
        """Обратна претрага: српска реч -> пиротска реч и значење."""
        cist = _cisti(pojam)
        if not cist:
            return []

        rezultati = []
        if cist in self.indeks_srpski:
            for idx in self.indeks_srpski[cist]:
                rezultati.append(self.odrednice[idx])
            return rezultati

        # Тражење унутар значења
        for odr in self.odrednice:
            if cist in odr["znacenje"].lower():
                rezultati.append(odr)
                if len(rezultati) >= 5:
                    break

        return rezultati

    def slucajna_odrednica(self) -> dict | None:
        """Враћа насумичну одредницу из речника."""
        if not self.odrednice:
            return None
        return random.choice(self.odrednice)

    def slucajan_primer(self) -> dict | None:
        """Враћа насумичну забележену реченицу са терена."""
        if not self.svi_primeri:
            return None
        return random.choice(self.svi_primeri)

    def formatiraj_odgovor(self, odr: dict) -> str:
        """Лепо форматира речнички запис за приказ у апликацији."""
        rec = odr.get("rec", "")
        vrsta = odr.get("vrsta", "")
        znacenje = odr.get("znacenje", "")
        primeri = odr.get("primeri", [])

        linije = [f"• {rec.upper()} ({vrsta}): {znacenje}"]
        if primeri:
            pr = primeri[0]
            if len(pr) > 120:
                pr = pr[:117] + "..."
            linije.append(f"  Пример: \"{pr}\"")
        return "\n".join(linije)


def main():
    m = ModelPirotskogGovora()
    print(f"Учитано одредница: {m.broj_odrednica}")
    if m.broj_odrednica > 0:
        odr = m.slucajna_odrednica()
        print("\nСлучајна одредница:")
        print(m.formatiraj_odgovor(odr))


if __name__ == "__main__":
    main()
