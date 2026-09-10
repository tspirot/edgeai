"""Заједнички облик за све генераторе шара."""

from __future__ import annotations


class GeneratorBackend:
    def napravi(self, skica=None, motiv_id=None, seed: int = 0):
        """Врати слику (H, W, 3) uint8 — предлог шаре.

        `skica` је груб цртеж ученика (H, W) или (H, W, 3); тамно = потез.
        `motiv_id` је шара из каталога на коју се предлог ослања.
        """
        raise NotImplementedError

    def close(self) -> None:
        pass
