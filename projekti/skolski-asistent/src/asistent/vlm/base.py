"""Заједнички уговор за VLM модуле (слика + питање → одговор)."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Answer:
    """Одговор асистента.

    `text`          — одговор на српском.
    `used_context`  — исечци из материјала које је RAG приложио (ако их је било).
    `latency_ms`    — колико је трајала инференца VLM-а.
    """

    text: str = ""
    used_context: list = field(default_factory=list)
    latency_ms: float = 0.0


class VlmBackend:
    def answer(
        self,
        image: "np.ndarray | None",
        question: str,
        context: "list[str] | None" = None,
    ) -> Answer:  # pragma: no cover - интерфејс
        raise NotImplementedError

    def close(self) -> None:
        pass


def build_prompt(system_prompt: str, question: str, context: "list[str] | None") -> str:
    """Склопи текстуални део упита (систем + материјали + питање)."""
    parts = [system_prompt.strip()]
    if context:
        blocks = "\n\n".join(f"[{i + 1}] {c.strip()}" for i, c in enumerate(context))
        parts.append("Исечци из школских материјала:\n" + blocks)
    parts.append("Питање ученика: " + question.strip())
    return "\n\n".join(parts)
