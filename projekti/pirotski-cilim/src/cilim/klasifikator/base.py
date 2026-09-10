"""Заједнички облик за све класификаторе шара."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Nalaz:
    """Шта је класификатор видео."""

    motiv_id: str
    pouzdanost: float
    ostali: list = field(default_factory=list)  # [(motiv_id, pouzdanost), …]
    latencija_ms: float = 0.0

    @property
    def siguran(self) -> bool:
        return self.pouzdanost >= 0.45


class KlasifikatorBackend:
    def prepoznaj(self, slika) -> Nalaz:
        raise NotImplementedError

    def close(self) -> None:
        pass
