"""Заједнички уговор за синтезу говора."""

from __future__ import annotations


class TtsBackend:
    def say(self, text: str) -> None:  # pragma: no cover - интерфејс
        raise NotImplementedError

    def close(self) -> None:
        pass
