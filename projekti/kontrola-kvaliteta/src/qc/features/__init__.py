"""Издвајање обележја по блоковима слике."""

from __future__ import annotations

from qc.features.base import BlockFeatures, FeatureExtractor

__all__ = ["BlockFeatures", "FeatureExtractor", "build_extractor"]


def build_extractor(cfg):
    backend = (cfg.backend or "").lower()
    if backend == "handcrafted":
        from qc.features.handcrafted import HandcraftedExtractor

        return HandcraftedExtractor(cfg)
    if backend == "torch":
        from qc.features.torch_backend import TorchExtractor

        return TorchExtractor(cfg)
    if backend == "dummy":
        from qc.features.handcrafted import HandcraftedExtractor

        return HandcraftedExtractor(cfg)
    raise ValueError(f"Непознат features backend: '{cfg.backend}'")
