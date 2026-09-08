"""Временско гласање — стабилизује излаз преко више кадрова.

Слово се исписује тек кад се исти предлог понови довољно пута у прозору,
и то само предлози изнад прага поузданости. Тако слово не „поскакује".
"""

from __future__ import annotations

from collections import Counter, deque


class Vote:
    def __init__(self, window: int = 8, min_count: int = 5, min_confidence: float = 0.55) -> None:
        self.min_count = min_count
        self.min_confidence = min_confidence
        self._buf: deque = deque(maxlen=window)
        self._current: "str | None" = None

    def push(self, label: str, confidence: float) -> "str | None":
        self._buf.append(label if confidence >= self.min_confidence else None)
        counts = Counter(x for x in self._buf if x is not None)
        if counts:
            label, n = counts.most_common(1)[0]
            if n >= self.min_count:
                self._current = label
        return self._current

    @property
    def current(self) -> "str | None":
        return self._current

    def reset(self) -> None:
        self._buf.clear()
        self._current = None
