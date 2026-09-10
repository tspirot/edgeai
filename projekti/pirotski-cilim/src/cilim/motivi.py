"""Каталог шара — учитавање, провера и опрезан испис.

Пројекат не сме да измишља номенклатуру. Свака одредница носи извор назива и
ознаку да ли ју је потврдила школска радионица ћилима. Док потврде нема,
значење се исписује са оградом — и то намерно упадљиво, да ученику буде јасно
шта је проверено а шта преписано.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

PODRAZUMEVANI_KATALOG = Path(__file__).with_name("motivi.yaml")

DELOVI = {"поље", "бордура", "ћенар", "непознато"}


@dataclass(frozen=True)
class Motiv:
    id: str
    naziv: str
    znacenje: str
    deo: str
    izvor: tuple
    potvrdila_radionica: bool

    def opis(self) -> str:
        """Значење са оградом ако радионица још није потврдила."""
        if self.potvrdila_radionica:
            return f"{self.naziv}: {self.znacenje}"
        izvori = ", ".join(self.izvor) or "без извора"
        return (
            f"{self.naziv}: {self.znacenje} "
            f"[НЕПОТВРЂЕНО — назив преузет из: {izvori}; "
            f"проверити у радионици]"
        )


class Katalog:
    def __init__(self, motivi) -> None:
        self.motivi = tuple(motivi)
        self._po_id = {m.id: m for m in self.motivi}
        if len(self._po_id) != len(self.motivi):
            raise ValueError("Каталог има две одреднице са истим `id`")

    def __len__(self) -> int:
        return len(self.motivi)

    def __iter__(self):
        return iter(self.motivi)

    def __contains__(self, motiv_id) -> bool:
        return motiv_id in self._po_id

    @property
    def imena(self) -> tuple:
        return tuple(m.id for m in self.motivi)

    def nadji(self, motiv_id: str) -> Motiv:
        try:
            return self._po_id[motiv_id]
        except KeyError:
            raise KeyError(
                f"Нема шаре '{motiv_id}' у каталогу. Има: {', '.join(self.imena)}"
            ) from None

    @property
    def potvrdjenih(self) -> int:
        return sum(1 for m in self.motivi if m.potvrdila_radionica)

    def upozorenje(self) -> "str | None":
        """Порука коју CLI исписује док каталог није проверен у радионици."""
        n = len(self.motivi) - self.potvrdjenih
        if n == 0:
            return None
        return (
            f"Пажња: {n} од {len(self.motivi)} одредница у каталогу још није "
            "потврдила радионица. Значења су преузета из литературе и могу бити "
            "нетачна — проверити пре него што се покажу јавно."
        )


def _motiv_iz(stavka, redni: int) -> Motiv:
    if not isinstance(stavka, dict):
        raise ValueError(f"Одредница {redni}: очекиван објекат, добијено {type(stavka).__name__}")
    for polje in ("id", "naziv", "znacenje"):
        if not stavka.get(polje):
            raise ValueError(f"Одредница {redni}: недостаје '{polje}'")
    deo = stavka.get("deo", "непознато")
    if deo not in DELOVI:
        raise ValueError(
            f"Одредница '{stavka['id']}': непознат део ћилима '{deo}'. "
            f"Дозвољено: {', '.join(sorted(DELOVI))}"
        )
    izvor = stavka.get("izvor") or []
    if isinstance(izvor, str):
        izvor = [izvor]
    return Motiv(
        id=str(stavka["id"]),
        naziv=str(stavka["naziv"]),
        znacenje=str(stavka["znacenje"]),
        deo=deo,
        izvor=tuple(str(i) for i in izvor),
        potvrdila_radionica=bool(stavka.get("potvrdila_radionica", False)),
    )


def ucitaj(putanja=None) -> Katalog:
    """Учитај каталог из YAML фајла (подразумевано: онај уз пакет)."""
    p = Path(putanja) if putanja else PODRAZUMEVANI_KATALOG
    if not p.exists():
        raise FileNotFoundError(f"Каталог шара не постоји: {p}")
    if yaml is None:  # pragma: no cover
        raise RuntimeError("PyYAML није инсталиран — `pip install pyyaml`")
    podaci = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    stavke = podaci.get("motivi")
    if not stavke:
        raise ValueError(f"Каталог {p} нема ниједну одредницу под кључем 'motivi'")
    return Katalog(_motiv_iz(s, i) for i, s in enumerate(stavke, 1))
