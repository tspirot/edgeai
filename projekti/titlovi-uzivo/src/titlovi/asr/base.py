"""Заједнички уговор за све ASR модуле (backend-ове)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Transcript:
    """Инкрементални резултат препознавања.

    `text_add`  — нови, потврђени текст који се ДОДАЈЕ на досадашњи титл.
    `partial`   — тренутни несигурни "реп" који ЗАМЕЊУЈЕ претходни несигурни део.
    `endpoint`  — тачно кад је говорник завршио целину (реченицу/паузу).
    """

    text_add: str = ""
    partial: str = ""
    endpoint: bool = False


class AsrBackend:
    """Апстрактни модул. `accept` добија моно float32 узорке на 16 kHz."""

    def accept(self, pcm_f32) -> "Transcript | None":  # pragma: no cover - интерфејс
        raise NotImplementedError

    def flush(self) -> "Transcript | None":
        """Заврши текућу целину (нпр. на крају фајла)."""
        return None

    def close(self) -> None:
        pass
