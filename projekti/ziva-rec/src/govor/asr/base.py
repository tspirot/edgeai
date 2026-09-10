"""Заједнички облик за све ASR модуле.

Транскрипт носи временски поравнате сегменте — то је важно за исправку: клик на
реч у вебу (касније, засебан пројекат) пушта тај тренутак снимка. Овде се та
поравнања чувају од самог почетка.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Segment:
    pocetak: float        # секунде
    kraj: float
    tekst: str

    def __post_init__(self):
        if self.kraj < self.pocetak:
            raise ValueError(f"Сегмент се завршава пре почетка: {self.pocetak}–{self.kraj}")

    @property
    def trajanje(self) -> float:
        return self.kraj - self.pocetak


@dataclass
class Transkript:
    segmenti: list = field(default_factory=list)
    jezik: str = "sr"
    model: str = ""

    @property
    def tekst(self) -> str:
        return " ".join(s.tekst.strip() for s in self.segmenti if s.tekst.strip())

    @property
    def trajanje(self) -> float:
        return self.segmenti[-1].kraj if self.segmenti else 0.0

    def recenice(self) -> list:
        """Груба подела на реченице по интерпункцији, за оцену торлачности."""
        import re

        delovi = re.split(r"(?<=[.!?…])\s+", self.tekst)
        return [d.strip() for d in delovi if d.strip()]


class AsrBackend:
    def transkribuj(self, audio, samplerate: int) -> Transkript:
        raise NotImplementedError

    def close(self) -> None:
        pass
