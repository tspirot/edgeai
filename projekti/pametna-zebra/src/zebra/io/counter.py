"""Бројач — јединствени трагови по типу и по зони, ред у CSV на сваких N секунди.

Не памти слику ни путање — само бројеве. То је оно што иде граду.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Counter:
    log_file: "str | Path | None" = None
    interval_s: float = 60.0

    total: dict = field(default_factory=lambda: {"person": 0, "vehicle": 0})
    zones: dict = field(default_factory=lambda: {"crosswalk": set(), "roadway": set()})
    rows: list = field(default_factory=list)

    _seen: set = field(default_factory=set, repr=False)
    _window: dict = field(default_factory=lambda: {"person": 0, "vehicle": 0}, repr=False)
    _next_flush: "float | None" = field(default=None, repr=False)

    def update(self, tracks, scene, now: float) -> None:
        if self._next_flush is None:
            self._next_flush = now + self.interval_s

        # прво затвори протекле прозоре, па тек онда броји нове трагове
        while now >= self._next_flush:
            self._flush(self._next_flush)
            self._next_flush += self.interval_s

        for tr in tracks:
            if tr.id not in self._seen:
                self._seen.add(tr.id)
                self.total[tr.kind] = self.total.get(tr.kind, 0) + 1
                self._window[tr.kind] = self._window.get(tr.kind, 0) + 1
            zone = scene.where(tr.center)
            if zone in self.zones:
                self.zones[zone].add(tr.id)

    def _flush(self, at: float) -> None:
        row = {
            "vreme": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "sekunda": round(at, 1),
            "pesaci": self._window["person"],
            "vozila": self._window["vehicle"],
        }
        self.rows.append(row)
        self._window = {"person": 0, "vehicle": 0}
        if self.log_file:
            path = Path(self.log_file)
            new = not path.exists()
            with path.open("a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
                if new:
                    writer.writeheader()
                writer.writerow(row)

    def close(self, now: float | None = None) -> None:
        if now is not None and self._next_flush is not None and self._window != {"person": 0, "vehicle": 0}:
            self._flush(now)
