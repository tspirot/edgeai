"""Дифузиони генератор: Stable Diffusion 1.5 + ControlNet, локално на Orin-у.

ControlNet држи скицу ученика као ограничење — без њега модел одлута у нешто
што личи на теписи уопште, а не на оно што је ученик замислио. LoRA дообучена на
школском скупу шара даје потез; она се, као и тежине класификатора, не преузима
него настаје у радионици.

Излаз овог модула је обична слика са меким прелазима. Правила заната се на њу
примењују тек у `cilim.pipeline` — овде се ништа не намеће.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np

from cilim.generator.base import GeneratorBackend

log = logging.getLogger(__name__)


def _uredjaj(trazeno: str):
    import torch

    if trazeno != "auto":
        return torch.device(trazeno)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


class DifuzijaGenerator(GeneratorBackend):
    def __init__(self, katalog, cfg) -> None:
        try:
            import torch
            from diffusers import (
                ControlNetModel,
                StableDiffusionControlNetPipeline,
                UniPCMultistepScheduler,
            )
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Недостају diffusers и torch — `pip install -e \".[difuzija]\"`. "
                "На Jetson-у torch иде из NVIDIA-иног build-а, не са PyPI-ја."
            ) from exc

        self.katalog = katalog
        self.cfg = cfg
        self.torch = torch
        self.device = _uredjaj(cfg.device)
        dtype = torch.float16 if self.device.type == "cuda" else torch.float32

        controlnet = ControlNetModel.from_pretrained(
            cfg.controlnet, torch_dtype=dtype, cache_dir=cfg.download_root or None
        )
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            cfg.model,
            controlnet=controlnet,
            torch_dtype=dtype,
            safety_checker=None,
            cache_dir=cfg.download_root or None,
        )
        self.pipe.scheduler = UniPCMultistepScheduler.from_config(self.pipe.scheduler.config)
        self.pipe.to(self.device)

        lora = Path(cfg.lora)
        if lora.exists():
            self.pipe.load_lora_weights(str(lora))
            log.info("LoRA учитана: %s", lora)
        else:
            log.warning(
                "Нема LoRA тежина у %s — модел ће дати уопштен тепих, не пиротску шару. "
                "LoRA се обучава на школском скупу (docs/obuka.md).",
                lora,
            )

        if self.device.type == "cuda":
            self.pipe.enable_attention_slicing()   # 8 GB је 8 GB

    def _kontrola(self, skica, n: int):
        """Скица → црно-бела контролна слика какву scribble ControlNet очекује."""
        from PIL import Image

        if skica is None:
            # без скице: празно платно, модел бира сам
            return Image.new("RGB", (n, n), "black")
        arr = np.asarray(skica)
        if arr.ndim == 3:
            arr = arr[:, :, :3].mean(axis=2)
        potez = (arr < arr.mean()).astype(np.uint8) * 255   # бели потез на црном
        return Image.fromarray(potez).convert("RGB").resize((n, n))

    def napravi(self, skica=None, motiv_id=None, seed: int = 0) -> np.ndarray:
        if motiv_id is not None and motiv_id not in self.katalog:
            raise KeyError(f"Нема шаре '{motiv_id}' у каталогу")

        n = int(self.cfg.velicina)
        uput = self.cfg.uput
        if motiv_id is not None:
            uput = f"{self.katalog.nadji(motiv_id).naziv}, {uput}"

        t0 = time.perf_counter()
        slika = self.pipe(
            prompt=uput,
            negative_prompt=self.cfg.ne_zelim,
            image=self._kontrola(skica, n),
            num_inference_steps=int(self.cfg.koraka),
            controlnet_conditioning_scale=float(self.cfg.jacina_skice),
            generator=self.torch.Generator(device=self.device).manual_seed(int(seed)),
            height=n,
            width=n,
        ).images[0]
        log.info("Дифузија: %.0f ms", (time.perf_counter() - t0) * 1000)
        return np.asarray(slika.convert("RGB"), dtype=np.uint8)

    def close(self) -> None:
        self.pipe = None
        if self.torch.cuda.is_available():  # pragma: no cover
            self.torch.cuda.empty_cache()
