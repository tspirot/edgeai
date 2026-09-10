"""Речник пиротског говора — учитавање, претрага и опрезан испис.

Исти принцип као каталог шара код пројекта 10: свака одредница носи извор, а
значење се исписује са оградом док га говорник не потврди. Станица не тврди
како се шта каже — она нуди оно што је записано и означава одакле је.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

from govor.crte import preslovi

PODRAZUMEVANI_RECNIK = Path(__file__).with_name("recnik.yaml")


@dataclass(frozen=True)
class Odrednica:
    rec: str
    znaci: str
    napomena: str
    izvor: tuple
    potvrdio_govornik: bool

    def opis(self) -> str:
        osnova = f"{self.rec} — {self.znaci}"
        if self.napomena:
            osnova += f" ({self.napomena})"
        if self.potvrdio_govornik:
            return osnova
        izvori = ", ".join(self.izvor) or "без извора"
        return f"{osnova} [НЕПОТВРЂЕНО — из: {izvori}; проверити код говорника]"


class Recnik:
    def __init__(self, odrednice) -> None:
        self.odrednice = tuple(odrednice)
        self._po_reci = {preslovi(o.rec): o for o in self.odrednice}
        if len(self._po_reci) != len(self.odrednice):
            raise ValueError("Речник има две одреднице са истом речи")

    def __len__(self) -> int:
        return len(self.odrednice)

    def __iter__(self):
        return iter(self.odrednice)

    def __contains__(self, rec: str) -> bool:
        return preslovi(rec) in self._po_reci

    def nadji(self, rec: str) -> "Odrednica | None":
        return self._po_reci.get(preslovi(rec))

    @property
    def potvrdjenih(self) -> int:
        return sum(1 for o in self.odrednice if o.potvrdio_govornik)

    def upozorenje(self) -> "str | None":
        n = len(self.odrednice) - self.potvrdjenih
        if n == 0:
            return None
        return (
            f"Пажња: {n} од {len(self.odrednice)} одредница речника још није "
            "потврдио говорник. Значења су из литературе и могу бити нетачна за "
            "баш овај крај."
        )


def _odrednica_iz(stavka, redni: int) -> Odrednica:
    if not isinstance(stavka, dict):
        raise ValueError(f"Одредница {redni}: очекиван објекат")
    for polje in ("rec", "znaci"):
        if not stavka.get(polje):
            raise ValueError(f"Одредница {redni}: недостаје '{polje}'")
    izvor = stavka.get("izvor") or []
    if isinstance(izvor, str):
        izvor = [izvor]
    if not izvor:
        raise ValueError(
            f"Одредница '{stavka['rec']}': нема извор. Реч без извора је "
            "измишљена реч — то овде не сме."
        )
    return Odrednica(
        rec=str(stavka["rec"]),
        znaci=str(stavka["znaci"]),
        napomena=str(stavka.get("napomena", "")),
        izvor=tuple(str(i) for i in izvor),
        potvrdio_govornik=bool(stavka.get("potvrdio_govornik", False)),
    )


def ucitaj(putanja=None) -> Recnik:
    p = Path(putanja) if putanja else PODRAZUMEVANI_RECNIK
    if not p.exists():
        raise FileNotFoundError(f"Речник не постоји: {p}")
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML није инсталиран — `pip install pyyaml`")
    podaci = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    stavke = podaci.get("odrednice")
    if not stavke:
        raise ValueError(f"Речник {p} нема ниједну одредницу под кључем 'odrednice'")
    return Recnik(_odrednica_iz(s, i) for i, s in enumerate(stavke, 1))
