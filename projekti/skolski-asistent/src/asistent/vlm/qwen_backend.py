"""Qwen2-VL — визуелно-језички модел на самом уређају (transformers).

Препоручено: Qwen2-VL-2B-Instruct, int4 квантизација — стаје у ~6 GB и ради
уживо на Jetson Orin Nano (8 GB). Модел се преузме једном, после тога офлајн.
"""

from __future__ import annotations

import logging
import time

import numpy as np

from asistent.vlm.base import Answer, VlmBackend, build_prompt

log = logging.getLogger(__name__)


class QwenVlm(VlmBackend):
    def __init__(self, vlm_cfg) -> None:
        import torch
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

        self.cfg = vlm_cfg
        self._torch = torch

        kwargs = {"torch_dtype": "auto", "device_map": vlm_cfg.device}
        if vlm_cfg.quantization in ("int4", "int8"):
            from transformers import BitsAndBytesConfig

            kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=vlm_cfg.quantization == "int4",
                load_in_8bit=vlm_cfg.quantization == "int8",
                bnb_4bit_compute_dtype=torch.float16,
            )

        log.info("Учитавам VLM '%s' (%s)…", vlm_cfg.model, vlm_cfg.quantization)
        self._model = Qwen2VLForConditionalGeneration.from_pretrained(
            vlm_cfg.model, cache_dir=vlm_cfg.download_root or None, **kwargs
        )
        self._processor = AutoProcessor.from_pretrained(
            vlm_cfg.model, cache_dir=vlm_cfg.download_root or None
        )

    def answer(self, image, question, context=None) -> Answer:
        from PIL import Image

        prompt = build_prompt(self.cfg.system_prompt, question, context)
        content = []
        pil = None
        if image is not None:
            pil = Image.fromarray(np.asarray(image, dtype=np.uint8))
            content.append({"type": "image"})
        content.append({"type": "text", "text": prompt})
        messages = [{"role": "user", "content": content}]

        text = self._processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self._processor(
            text=[text],
            images=[pil] if pil is not None else None,
            return_tensors="pt",
        ).to(self._model.device)

        t0 = time.perf_counter()
        with self._torch.inference_mode():
            out = self._model.generate(
                **inputs,
                max_new_tokens=self.cfg.max_new_tokens,
                do_sample=self.cfg.temperature > 0,
                temperature=max(self.cfg.temperature, 1e-4),
            )
        latency = (time.perf_counter() - t0) * 1000

        trimmed = out[:, inputs["input_ids"].shape[1]:]
        answer = self._processor.batch_decode(trimmed, skip_special_tokens=True)[0].strip()
        return Answer(text=answer, used_context=list(context or []), latency_ms=latency)
