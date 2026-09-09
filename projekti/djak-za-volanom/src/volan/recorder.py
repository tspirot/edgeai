"""Снимање и читање скупа вожњи (tub).

Формат: `data/<sesija>/` са `record_000001.jpg` и `record_000001.json`
(`{"steer": ..., "throttle": ..., "ts": ...}`). Једноставно намерно — ученици
могу да прегледају и обришу лоше кадрове ручно.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np


class TubWriter:
    def __init__(self, out_dir: "str | Path", jpg_quality: int = 90, session: str = "") -> None:
        session = session or time.strftime("%Y%m%d-%H%M%S")
        self.dir = Path(out_dir) / session
        self.dir.mkdir(parents=True, exist_ok=True)
        self.jpg_quality = jpg_quality
        self._n = 0

    def add(self, image: np.ndarray, steer: float, throttle: float) -> None:
        from PIL import Image

        self._n += 1
        stem = f"record_{self._n:06d}"
        Image.fromarray(np.asarray(image, dtype=np.uint8)).save(
            self.dir / f"{stem}.jpg", quality=self.jpg_quality
        )
        (self.dir / f"{stem}.json").write_text(
            json.dumps({"steer": float(steer), "throttle": float(throttle), "ts": time.time()}),
            encoding="utf-8",
        )

    @property
    def count(self) -> int:
        return self._n


def read_tub(path: "str | Path"):
    """Врати (X, y) где је X низ слика (N,H,W,3) uint8, y низ [steer, throttle]."""
    from PIL import Image

    root = Path(path)
    jsons = sorted(root.rglob("record_*.json"))
    if not jsons:
        raise FileNotFoundError(f"Нема record_*.json у {root}")
    images, labels = [], []
    for jp in jsons:
        meta = json.loads(jp.read_text(encoding="utf-8"))
        ip = jp.with_suffix(".jpg")
        if not ip.exists():
            continue
        with Image.open(ip) as im:
            images.append(np.asarray(im.convert("RGB"), dtype=np.uint8))
        labels.append([meta.get("steer", 0.0), meta.get("throttle", 0.0)])
    return np.stack(images), np.asarray(labels, dtype=np.float32)
