"""ViT класификатор шара — дообучен на скупу који праве ученици.

Тежине не долазе уз пакет. Настају у радионици: ученици сликају ћилиме и разбој,
означавају исечке, па се мали ViT дообучи на том скупу (`docs/obuka.md`).
"""

from __future__ import annotations

import logging
import time

import numpy as np

from cilim.klasifikator.base import KlasifikatorBackend, Nalaz

log = logging.getLogger(__name__)


def _uredjaj(trazeno: str):
    import torch

    if trazeno != "auto":
        return torch.device(trazeno)
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


class VitKlasifikator(KlasifikatorBackend):
    def __init__(self, katalog, cfg) -> None:
        try:
            import timm
            import torch
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "Недостају torch и timm — `pip install -e \".[klasifikator]\"`. "
                "На Jetson-у torch иде из NVIDIA-иног build-а, не са PyPI-ја."
            ) from exc

        from pathlib import Path

        self.katalog = katalog
        self.cfg = cfg
        self.torch = torch
        self.device = _uredjaj(cfg.device)

        tezine = Path(cfg.tezine)
        if not tezine.exists():  # pragma: no cover
            raise FileNotFoundError(
                f"Нема тежина класификатора: {tezine}\n"
                "Оне се не преузимају — праве се обуком на школском скупу шара. "
                "За пробу без модела: --klasifikator dummy"
            )

        self.model = timm.create_model(
            cfg.model, pretrained=False, num_classes=len(katalog)
        )
        stanje = torch.load(str(tezine), map_location="cpu")
        self.model.load_state_dict(stanje.get("model", stanje))
        self.model.eval().to(self.device)

        # редослед класа мора да прати каталог — иначе модел говори туђа имена
        sacuvana = stanje.get("klase") if isinstance(stanje, dict) else None
        if sacuvana is not None and tuple(sacuvana) != katalog.imena:
            raise ValueError(
                "Редослед класа у тежинама се не поклапа са каталогом шара. "
                "Тежине су обучене на другом каталогу — поново обучи или врати стари каталог."
            )
        log.info("ViT класификатор: %s, %d класа, %s", cfg.model, len(katalog), self.device)

    def _pripremi(self, slika):
        from PIL import Image

        n = self.cfg.velicina
        img = Image.fromarray(np.asarray(slika).astype(np.uint8)).convert("RGB").resize((n, n))
        x = np.asarray(img, dtype=np.float32) / 255.0
        x = (x - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        return self.torch.from_numpy(x.transpose(2, 0, 1)[None]).float().to(self.device)

    def prepoznaj(self, slika) -> Nalaz:
        t0 = time.perf_counter()
        with self.torch.no_grad():
            izlaz = self.model(self._pripremi(slika))
            verovatnoce = self.torch.softmax(izlaz[0], dim=0).cpu().numpy()

        redosled = np.argsort(verovatnoce)[::-1]
        imena = self.katalog.imena
        return Nalaz(
            motiv_id=imena[int(redosled[0])],
            pouzdanost=float(verovatnoce[redosled[0]]),
            ostali=[(imena[int(i)], float(verovatnoce[i])) for i in redosled[1:4]],
            latencija_ms=(time.perf_counter() - t0) * 1000,
        )
