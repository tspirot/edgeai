"""Заједнички интерфејс за приказ титлова."""

from __future__ import annotations


class Display:
    def start(self) -> None:
        pass

    def render(self, committed: str, partial: str) -> None:  # pragma: no cover - интерфејс
        raise NotImplementedError

    def should_quit(self) -> bool:
        return False

    def stop(self) -> None:
        pass
