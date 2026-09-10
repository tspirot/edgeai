"""Лажни ASR — детерминистичан, без модела.

Не слуша ништа. Из дужине и енергије сигнала бира реченицу из уграђеног списка
и сегментише је по времену. Постоји да цео ланац (снимање → препис → исправка →
корпус) ради без модела и хардвера и да тестови имају предвидив излаз.

Реченице у списку су намерно писане пиротским говором — да оцена торлачности
има шта да ухвати кад се проба ланац.
"""

from __future__ import annotations

import numpy as np

from govor.asr.base import AsrBackend, Segment, Transkript

_RECENICE = (
    "Съга че идем у град да купим лебац.",
    "Тъг беше по-убаво него съга, море.",
    "Комшика ми рече да че работи цел дьн.",
    "Детето седи крај пенџер и гледа напоље.",
    "Оћу да ти вревим нешто важно.",
    "Той човекат нај-убаво пее у село.",
)


class DummyAsr(AsrBackend):
    def __init__(self, cfg=None) -> None:
        self.cfg = cfg

    def transkribuj(self, audio, samplerate: int) -> Transkript:
        a = np.asarray(audio, dtype=np.float64)
        if a.size == 0:
            return Transkript(segmenti=[], model="dummy")

        trajanje = a.size / max(samplerate, 1)
        energija = float(np.sqrt(np.mean(a ** 2))) if a.size else 0.0
        potpis = int(abs(a.size * 3 + energija * 9973))

        # једна до три реченице, према трајању
        koliko = min(1 + int(trajanje // 3), 3)
        izabrane = [_RECENICE[(potpis + i) % len(_RECENICE)] for i in range(koliko)]

        segmenti = []
        t = 0.0
        korak = max(trajanje / koliko, 0.5)
        for recenica in izabrane:
            segmenti.append(Segment(pocetak=round(t, 2),
                                    kraj=round(t + korak, 2),
                                    tekst=recenica))
            t += korak
        return Transkript(segmenti=segmenti, jezik="sr", model="dummy")
