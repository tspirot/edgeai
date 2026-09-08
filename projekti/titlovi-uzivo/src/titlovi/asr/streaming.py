"""LocalAgreement — како од Whisper-а (који није стриминг) добити титл уживо.

Идеја (Liu et al. 2020, „streaming policies"; касније Whisper-Streaming, ÚFAL):
Whisper се покреће сваких неколико секунди на растућем прозору звука. Његова
хипотеза се на крају мења, али почетак се брзо „слегне". Реч проглашавамо
ПОТВРЂЕНОМ тек кад се појави на истом месту у ДВЕ узастопне хипотезе. Остатак
се приказује као несигуран.
"""

from __future__ import annotations


class LocalAgreement:
    def __init__(self) -> None:
        self._prev: list[str] = []
        self._committed = 0  # број речи од почетка прозора које су потврђене

    def insert(self, words: list[str]) -> tuple[list[str], list[str]]:
        """Убаци нову пуну хипотезу. Врати (нове_потврђене_речи, несигуран_реп)."""
        common = 0
        for a, b in zip(self._prev, words):
            if a == b:
                common += 1
            else:
                break

        newly = words[self._committed:common]
        self._committed = max(self._committed, common)
        self._prev = list(words)
        partial = words[self._committed:]
        return newly, partial

    def flush(self) -> list[str]:
        """Потврди све преостало из последње хипотезе (крај целине)."""
        rest = self._prev[self._committed:]
        self._committed = len(self._prev)
        return rest

    def reset(self) -> None:
        self._prev = []
        self._committed = 0
