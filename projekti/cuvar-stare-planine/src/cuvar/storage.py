"""Складиштење догађаја — снима само оно што је препознато, уз ротацију.

Уз сваки кадар иде JSON са врстом, поузданошћу и мерењима климе. Стари кадрови
се бришу кад се пређе `keep_last` (картица на терену траје данима).
"""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Event:
    time: str
    species: str
    score: float
    climate: dict
    image: "str | None" = None


@dataclass
class EventStore:
    directory: "str | Path" = "snimci"
    keep_last: int = 500
    save_images: bool = True

    events: list = field(default_factory=list)
    species_counts: dict = field(default_factory=dict)
    _event_files: deque = field(default_factory=deque, repr=False)

    def __post_init__(self) -> None:
        self._dir = Path(self.directory)

    def record(self, species: str, score: float, climate: dict, frame=None) -> Event:
        stamp = datetime.now(timezone.utc)
        name = stamp.strftime("%Y%m%dT%H%M%S_%f_") + species.replace(" ", "-")
        ev = Event(stamp.isoformat(timespec="seconds"), species, round(score, 3), dict(climate))

        self._dir.mkdir(parents=True, exist_ok=True)
        files: list[Path] = []
        if self.save_images and frame is not None:
            img_path = self._dir / f"{name}.jpg"
            self._write_image(frame, img_path)
            ev.image = img_path.name
            files.append(img_path)

        json_path = self._dir / f"{name}.json"
        json_path.write_text(
            json.dumps(ev.__dict__, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        files.append(json_path)

        self._event_files.append(files)
        self.events.append(ev)
        self.species_counts[species] = self.species_counts.get(species, 0) + 1
        self._rotate()
        return ev

    def _rotate(self) -> None:
        while len(self._event_files) > self.keep_last:
            for old in self._event_files.popleft():
                try:
                    old.unlink()
                except OSError:
                    pass

    @staticmethod
    def _write_image(frame, path: Path) -> None:
        try:
            import cv2

            cv2.imwrite(str(path), frame)
        except Exception:  # pragma: no cover - без OpenCV
            path.write_bytes(b"")
