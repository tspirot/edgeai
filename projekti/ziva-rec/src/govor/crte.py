"""Торлачке црте као правила — мерење „колико је реченица пиротска“.

Ниједан неурон. Свака црта је правило са примером, тежином и тестом. Скор није
оцена тачности него мера удаљености од стандардног српског.

**Ова провера је намерно ГРУБА и опрезна.** Поуздано препознавање дијалекта из
текста тражи дообучен модел (Tang & Vuković, „NLP for preserving Torlak“,
COLING 2025) — правила промаше и лажно погоде. Зато:
- јаки знаци (полугласник, /ѕ/, по-/нај- са цртицом) носе велику тежину,
- остало иде преко списка речи, не преко „паметних“ образаца,
- скор се увек тумачи као „вреди погледати“, никад као пресуда.

Чему служи: издвајање сегмената за исправку који су ЈАКО дијалекатски, и провера
да дообучени Whisper није „упеглао“ говор ка стандарду.

Изворне црте: чланак „Пиротски говор“ (Википедија), Живковић „Говор Пирота“
(Пиротски зборник 39), Златковић „Речник пиротског говора“.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

_LAT2CIR = str.maketrans({
    "a": "а", "b": "б", "c": "ц", "d": "д", "e": "е", "f": "ф", "g": "г",
    "h": "х", "i": "и", "j": "ј", "k": "к", "l": "л", "m": "м", "n": "н",
    "o": "о", "p": "п", "r": "р", "s": "с", "t": "т", "u": "у", "v": "в",
    "z": "з",
})

_RX_REC = re.compile(r"[а-шђјљњћџѕъ]+(?:-[а-шђјљњћџѕъ]+)*")


def preslovi(tekst: str) -> str:
    """Груба латиница → ћирилица, само за уједначавање уноса (не диграфи)."""
    return unicodedata.normalize("NFC", tekst).lower().translate(_LAT2CIR)


def reci(tekst: str) -> list:
    """Издвоји речи — ћирилица плус цртица (за по-убав, нај-стар)."""
    return _RX_REC.findall(preslovi(tekst))


# --- једна црта ---------------------------------------------------------

@dataclass(frozen=True)
class Crta:
    id: str
    opis: str
    primer: str
    tezina: float
    _proveri: object = field(compare=False, repr=False)

    def pogodak(self, rec: str, sledeca: "str | None") -> bool:
        return bool(self._proveri(rec, sledeca))


def _rx(obrazac: str):
    r = re.compile(obrazac)
    return lambda rec, sledeca=None: r.search(rec)


def _u_skupu(*reci_skup):
    s = frozenset(reci_skup)
    return lambda rec, sledeca=None: rec in s


def _par(prva: str, obrazac_druge: str):
    r = re.compile(obrazac_druge)
    return lambda rec, sledeca=None: rec == prva and sledeca is not None and r.search(sledeca)


# Списак се лако прошири — свака ставка је (id, опис, пример, тежина, провера).
CRTE = tuple(
    Crta(cid, opis, primer, tez, prov)
    for cid, opis, primer, tez, prov in (
        ("poluglas",
         "Чуван полугласник у писању: ъ",
         "със, дън, тъг, съга, лъжа", 2.0,
         _rx(r"ъ")),
        ("dz",
         "Африката /ѕ/ (dz) тамо где стандард има /з/",
         "ѕвезда, ѕид, ѕвоно", 1.8,
         _rx(r"ѕ")),
        ("komparativ-po",
         "Аналитички компаратив: по- + придев/прилог (са цртицом)",
         "по-убав, по-голем, по-убаво", 1.8,
         _rx(r"^по-[а-шђјљњћџ]{3,}$")),
        ("superlativ-naj",
         "Аналитички суперлатив: нај- + придев/прилог (са цртицом)",
         "нај-убав, нај-стар, нај-убаво", 1.4,
         _rx(r"^нај-[а-шђјљњћџ]{3,}$")),
        ("clan-m",
         "Постпозитивни члан мушког рода -ат/-от на познатим именицама",
         "човекат, ножот, зубат, путот", 1.6,
         _u_skupu("човекат", "човеко", "ножот", "ножат", "зубат", "путот",
                  "путат", "градат", "градот", "снегот", "домат", "домот",
                  "столат", "столот", "прстенат")),
        ("clan-z",
         "Постпозитивни члан женског рода -та/-на на познатим именицама",
         "женaта, кућата, главата, руката", 1.4,
         _u_skupu("жената", "кућата", "главата", "руката", "ногата", "водата",
                  "земјата", "мајката", "бабата", "сестрата", "снаата")),
        ("clan-s",
         "Постпозитивни члан средњег рода -то на познатим именицама",
         "детето, млекото, сунцето, селото", 1.6,
         _u_skupu("детето", "млекото", "сунцето", "селото", "полето",
                  "срцето", "детиштето", "местото")),
        ("izgubljeno-h",
         "Изгубљено /х/ у честим речима",
         "леб (хлеб), оћу (хоћу), ладно (хладно), ора (орах)", 1.4,
         _u_skupu("леб", "лебац", "лебо", "оћу", "оћеш", "оће", "оћемо", "оћете",
                  "ладно", "ладовина", "ладовин", "снаа", "снау", "ора", "ораси",
                  "уватим", "уватиш", "увати", "ич", "муа")),
        ("aorist-imperfekat",
         "Аорист/имперфекат у 1. лицу без -х: дадо, реко, видо, беше, идеше",
         "ја дадо, ја реко, ми видомо, тъг беше", 1.3,
         _u_skupu("дадо", "надо", "реко", "рекомо", "видо", "видомо", "чуо",
                  "отидо", "дојдо", "дојдомо", "почемо", "узо", "уватимо",
                  "беше", "беше", "идеше", "работеше", "имаше", "седеше")),
        ("enklitika",
         "Енклитике ги/гу/ђи/не/ве место их/јој/нас/вас",
         "ги видим, кажи гу, дадо не", 1.0,
         _u_skupu("ги", "гу", "ђи", "не", "ве", "ни", "ву")),
        ("zamenica",
         "Заменице торлачког облика: тија, оној, онија, ники, никој",
         "тија човек, оној дете, ники не дошја", 1.1,
         _u_skupu("тија", "тија", "оној", "онеј", "онија", "овија", "ники",
                  "никој", "нечији", "секој", "свак", "какъв", "такъв")),
        ("radni-pridev",
         "Радни глаг. придев м. рода: дошја, отишја, реклъ, могъл",
         "он дошја (дошао), она дошла, они дошли", 1.4,
         _rx(r"(шја|шъл|кја|къл|гја|гъл)$")),
        ("da-prezent",
         "„да“ + презент уместо инфинитива",
         "оћу да идем (не: хоћу ићи), почеја да работи", 0.7,
         _par("да", r"[а-шђјљњћџ]{2,}(м|ш|мо|те|у|е|и)$")),
        ("ce-futur",
         "Футур са „че“ уместо „ће“",
         "че идем, че работи, че дојде", 1.2,
         _u_skupu("че", "чу", "чемо", "чете")),
    )
)

CRTA_PO_ID = {c.id: c for c in CRTE}


# --- резултат --------------------------------------------------------

@dataclass
class Nalaz:
    reci: list
    oznake: list                       # за сваку реч: листа id-jeva црта
    recnik_pogoci: list = field(default_factory=list)

    @property
    def torlackih_reci(self) -> int:
        gadja = set(self.recnik_pogoci)
        return sum(1 for k, o in enumerate(self.oznake) if o or k in gadja)

    @property
    def skor(self) -> float:
        """0–1: збир тежина погођених црта, подељен бројем речи, ограничен на 1.

        Реченица од пет речи са два јака облика (тежине 2.0) даје 4/5 = 0.8.
        """
        if not self.reci:
            return 0.0
        tezina = sum(CRTA_PO_ID[i].tezina for o in self.oznake for i in o)
        tezina += len(set(self.recnik_pogoci)) * 1.0
        return min(tezina / len(self.reci), 1.0)

    @property
    def jako_dijalekatska(self) -> bool:
        return self.skor >= 0.35

    def sazetak(self) -> str:
        broj: dict = {}
        for o in self.oznake:
            for i in o:
                broj[i] = broj.get(i, 0) + 1
        delovi = [f"скор {self.skor:.2f}", f"{self.torlackih_reci}/{len(self.reci)} речи"]
        if broj:
            delovi.append("црте: " + ", ".join(f"{k}×{v}" for k, v in sorted(broj.items())))
        if self.recnik_pogoci:
            delovi.append(f"речник: {len(set(self.recnik_pogoci))}")
        return "  ".join(delovi)


def oceni(tekst: str, recnik=None) -> Nalaz:
    """Реченица → `Nalaz` са ознакама по речи и укупним скором."""
    r = reci(tekst)
    oznake = []
    for k, rec in enumerate(r):
        sledeca = r[k + 1] if k + 1 < len(r) else None
        oznake.append([c.id for c in CRTE if c.pogodak(rec, sledeca)])

    recnik_pogoci = []
    if recnik is not None:
        recnik_pogoci = [k for k, rec in enumerate(r) if rec in recnik]

    return Nalaz(reci=r, oznake=oznake, recnik_pogoci=recnik_pogoci)


def oceni_vise(recenice, recnik=None) -> list:
    return [oceni(s, recnik) for s in recenice]
