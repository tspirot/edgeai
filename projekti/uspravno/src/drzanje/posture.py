"""Праћење држања кроз време: добро/лоше стање, хистереза, бројање и подсетник.

Ниједна неуронска мрежа — прагови и тајмери. Може да се објасни и тестира.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Reference:
    """Лична калибрација — углови у усправном положају."""

    neck_deg: float = 0.0
    trunk_deg: float = 0.0

    def save(self, path: "str | Path") -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self)), encoding="utf-8")

    @classmethod
    def load(cls, path: "str | Path") -> "Reference":
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(
                f"Референца не постоји: {p}. Прво `drzanje calibrate`."
            )
        d = json.loads(p.read_text(encoding="utf-8"))
        return cls(float(d["neck_deg"]), float(d["trunk_deg"]))


@dataclass
class Status:
    bad: bool
    neck_dev: float          # одступање угла врата од референце
    trunk_dev: float         # одступање угла трупа од референце
    bad_streak_s: float      # колико тренутно траје лош низ
    total_bad_s: float       # укупно лошег времена у сесији
    events: int              # колико пута је држање „склизнуло“
    alert: bool              # укључити подсетник у овом кораку


class PostureMonitor:
    def __init__(self, cfg, reference: "Reference | None" = None) -> None:
        self.cfg = cfg
        self.ref = reference or Reference()
        self._bad = False
        self._streak_s = 0.0
        self._counted = False          # да ли је текући низ већ ушао у бројач
        self.total_bad_s = 0.0
        self.events = 0
        self._last_alert_t: float | None = None
        self._t: float | None = None

    def update(self, neck_deg: float, trunk_deg: float, t: float) -> Status:
        dt = 0.0 if self._t is None else max(0.0, t - self._t)
        self._t = t

        neck_dev = abs(neck_deg - self.ref.neck_deg)
        trunk_dev = abs(trunk_deg - self.ref.trunk_deg)

        over = (neck_dev > self.cfg.neck_threshold_deg
                or trunk_dev > self.cfg.trunk_threshold_deg)
        under = (neck_dev < self.cfg.neck_threshold_deg - self.cfg.clear_margin_deg
                 and trunk_dev < self.cfg.trunk_threshold_deg - self.cfg.clear_margin_deg)

        if self._bad:
            if under:
                self._bad = False
                self._streak_s = 0.0
                self._counted = False
        elif over:
            self._bad = True
            self._streak_s = 0.0
            self._counted = False

        alert = False
        if self._bad:
            self._streak_s += dt
            if self._streak_s >= self.cfg.bad_after_s:
                self.total_bad_s += dt
                if not self._counted:
                    self.events += 1
                    self._counted = True
                if (self._streak_s >= self.cfg.alert_after_s
                        and self._can_alert(t)):
                    alert = True
                    self._last_alert_t = t

        return Status(
            bad=self._bad, neck_dev=neck_dev, trunk_dev=trunk_dev,
            bad_streak_s=self._streak_s, total_bad_s=self.total_bad_s,
            events=self.events, alert=alert,
        )

    def _can_alert(self, t: float) -> bool:
        return (self._last_alert_t is None
                or t - self._last_alert_t >= self.cfg.alert_cooldown_s)

    def summary(self) -> dict:
        return {
            "total_bad_s": round(self.total_bad_s, 1),
            "events": self.events,
        }
