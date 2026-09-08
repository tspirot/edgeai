"""Пресловљавање латиница ⇄ ћирилица за српски језик.

Whisper за српски по правилу исписује латиницу. Пошто је ово школски пројекат
у Пироту, подразумевани приказ је ћирилица, па текст пресловљавамо пре приказа.
Пресловљавање је потпуно и обострано једнозначно (српски правопис, чл. 17).
"""

from __future__ import annotations

# Двословни знакови иду први да се не би поцепали на појединачна слова.
_LAT2CYR_DIGRAPHS = [
    ("Nj", "Њ"), ("NJ", "Њ"), ("nj", "њ"),
    ("Lj", "Љ"), ("LJ", "Љ"), ("lj", "љ"),
    ("Dž", "Џ"), ("DŽ", "Џ"), ("dž", "џ"),
]

_LAT2CYR_SINGLE = {
    "A": "А", "B": "Б", "V": "В", "G": "Г", "D": "Д", "Đ": "Ђ", "E": "Е",
    "Ž": "Ж", "Z": "З", "I": "И", "J": "Ј", "K": "К", "L": "Л", "M": "М",
    "N": "Н", "O": "О", "P": "П", "R": "Р", "S": "С", "T": "Т", "Ć": "Ћ",
    "U": "У", "F": "Ф", "H": "Х", "C": "Ц", "Č": "Ч", "Š": "Ш",
}

_LAT2CYR: dict[str, str] = {}
for _k, _v in _LAT2CYR_SINGLE.items():
    _LAT2CYR[_k] = _v
    _LAT2CYR[_k.lower()] = _v.lower()

_CYR2LAT: dict[str, str] = {
    "Љ": "Lj", "Њ": "Nj", "Џ": "Dž", "љ": "lj", "њ": "nj", "џ": "dž",
}
for _k, _v in _LAT2CYR_SINGLE.items():
    _CYR2LAT[_v] = _k
    _CYR2LAT[_v.lower()] = _k.lower()


def latin_to_cyrillic(text: str) -> str:
    for lat, cyr in _LAT2CYR_DIGRAPHS:
        text = text.replace(lat, cyr)
    return "".join(_LAT2CYR.get(ch, ch) for ch in text)


def cyrillic_to_latin(text: str) -> str:
    return "".join(_CYR2LAT.get(ch, ch) for ch in text)
