"""Записник сесија — само бројеви, никад слика.

`drzanje.csv`:  датум_време, трајање_s, лоше_s, епизоде, највећи_врат, највећи_труп
`skrining.csv`: датум, раме_нагиб, кук_нагиб  (просеци сесије)
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

DRZANJE_HEADER = ["datetime", "duration_s", "bad_s", "events", "max_neck_dev", "max_trunk_dev"]
SKRINING_HEADER = ["date", "shoulder_tilt", "hip_tilt"]


def _append(path: "str | Path", header, row) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    new = not p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new:
            w.writerow(header)
        w.writerow(row)


def log_session(path, duration_s, bad_s, events, max_neck_dev, max_trunk_dev) -> None:
    _append(path, DRZANJE_HEADER, [
        datetime.now().isoformat(timespec="seconds"),
        round(duration_s, 1), round(bad_s, 1), int(events),
        round(max_neck_dev, 1), round(max_trunk_dev, 1),
    ])


def log_screening(path, shoulder_tilt, hip_tilt) -> None:
    _append(path, SKRINING_HEADER, [
        datetime.now().date().isoformat(),
        round(shoulder_tilt, 2), round(hip_tilt, 2),
    ])


def read_csv(path: "str | Path") -> list:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Записник не постоји: {p}")
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
