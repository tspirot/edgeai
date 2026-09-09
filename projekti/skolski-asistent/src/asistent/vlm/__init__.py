"""Избор VLM модула према конфигурацији."""

from __future__ import annotations

from asistent.vlm.base import Answer, VlmBackend, build_prompt

__all__ = ["Answer", "VlmBackend", "build_prompt", "build_vlm"]


def build_vlm(vlm_cfg) -> VlmBackend:
    backend = (vlm_cfg.backend or "").lower()

    if backend in ("qwen", "qwen2-vl", "qwen2_vl"):
        from asistent.vlm.qwen_backend import QwenVlm

        return QwenVlm(vlm_cfg)

    if backend == "dummy":
        from asistent.vlm.dummy_backend import DummyVlm

        return DummyVlm(vlm_cfg)

    raise ValueError(f"Непознат VLM backend: '{vlm_cfg.backend}'")
