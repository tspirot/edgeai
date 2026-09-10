"""Лажни класификатор — детерминистичан, без модела и без тежина.

Не препознаје ништа. Из просечне боје слике извуче број и по њему изабере шару
из каталога. Постоји да би цео ланац могао да се проба без обучене мреже и да
би тестови имали предвидив излаз.
"""

from __future__ import annotations

import numpy as np

from cilim.klasifikator.base import KlasifikatorBackend, Nalaz


class DummyKlasifikator(KlasifikatorBackend):
    def __init__(self, katalog, cfg=None) -> None:
        if len(katalog) == 0:
            raise ValueError("Каталог шара је празан")
        self.katalog = katalog
        self.cfg = cfg

    def prepoznaj(self, slika) -> Nalaz:
        arr = np.asarray(slika)
        if arr.size == 0:
            raise ValueError("Празна слика")

        # детерминистичан „потпис“ слике: просек по каналима + расипање
        prosek = arr.reshape(-1, arr.shape[-1]).mean(axis=0) if arr.ndim == 3 else arr.mean()
        potpis = int(abs(np.sum(prosek) * 7 + np.std(arr) * 13))

        imena = self.katalog.imena
        k = potpis % len(imena)
        drugi = (k + 1) % len(imena)
        # поузданост из истог потписа, у опсегу [0.35, 0.95) — да буде и „нисам сигуран“
        p = 0.35 + (potpis % 60) / 100.0
        return Nalaz(
            motiv_id=imena[k],
            pouzdanost=round(p, 2),
            ostali=[(imena[drugi], round(max(0.0, 0.95 - p), 2))],
            latencija_ms=0.0,
        )
