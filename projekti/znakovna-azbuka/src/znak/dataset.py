"""Скуп података: CSV са редовима `label, x0, y0, ..., x20, y20` (сирове тачке).

Нормализација се ради при учитавању, да сирови подаци остану читљиви и
поново употребљиви кад се промени нормализација.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from znak.normalize import normalize_landmarks

_HEADER = ["label"] + [f"{ax}{i}" for i in range(21) for ax in ("x", "y")]


def append_sample(path: "str | Path", label: str, points) -> None:
    path = Path(path)
    pts = np.asarray(points, dtype=float).reshape(21, 2)
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(_HEADER)
        w.writerow([label] + [f"{v:.5f}" for v in pts.reshape(-1)])


def load_dataset(path: "str | Path") -> tuple[np.ndarray, list[str]]:
    rows = list(csv.reader(Path(path).open(encoding="utf-8")))
    if not rows:
        return np.empty((0, 42), dtype=np.float32), []
    body = rows[1:] if rows[0] and rows[0][0] == "label" else rows
    X, y = [], []
    for r in body:
        if len(r) < 43:
            continue
        y.append(r[0])
        pts = np.array(r[1:43], dtype=float).reshape(21, 2)
        X.append(normalize_landmarks(pts))
    return np.asarray(X, dtype=np.float32), y


def counts(path: "str | Path") -> dict[str, int]:
    _, y = load_dataset(path)
    out: dict[str, int] = {}
    for label in y:
        out[label] = out.get(label, 0) + 1
    return out
