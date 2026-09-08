"""ByteTrack асоцијација — двостепено упаривање (високе па ниске детекције).

То је суштина ByteTrack-а: детекције ниског поуздања се не бацају одмах, него
се њима покушава спасавање трагова који нису упарени у првој рунди. Модел
кретања је прост (брзина из историје центара) — довољно за пешаке и возила
на фиксној камери.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from zebra.detect.base import Detection, iou

_HISTORY = 30


@dataclass
class Track:
    id: int
    kind: str
    bbox: tuple[float, float, float, float]
    score: float
    hits: int = 1
    age: int = 0
    time_since_update: int = 0
    confirmed: bool = False
    history: list[tuple[int, float, float]] = field(default_factory=list)

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)

    def velocity(self, fps: float) -> tuple[float, float]:
        """Брзина центра у пикселима у секунди, из последњих тачака историје."""
        if len(self.history) < 2 or fps <= 0:
            return (0.0, 0.0)
        t0, x0, y0 = self.history[max(0, len(self.history) - 5)]
        t1, x1, y1 = self.history[-1]
        dt = (t1 - t0) / fps
        if dt <= 0:
            return (0.0, 0.0)
        return ((x1 - x0) / dt, (y1 - y0) / dt)


def _match(tracks: list[Track], dets: list[Detection], iou_thresh: float):
    """Похлепно упаривање по IoU уз услов истог типа. Врати (парови, слоб_трагови, слоб_дет)."""
    pairs = []
    for ti, tr in enumerate(tracks):
        for di, det in enumerate(dets):
            if tr.kind != det.kind:
                continue
            score = iou(tr.bbox, det.bbox)
            if score >= iou_thresh:
                pairs.append((score, ti, di))
    pairs.sort(reverse=True)

    used_t: set[int] = set()
    used_d: set[int] = set()
    matches = []
    for _, ti, di in pairs:
        if ti in used_t or di in used_d:
            continue
        used_t.add(ti)
        used_d.add(di)
        matches.append((ti, di))

    free_t = [i for i in range(len(tracks)) if i not in used_t]
    free_d = [i for i in range(len(dets)) if i not in used_d]
    return matches, free_t, free_d


class ByteTracker:
    def __init__(self, iou_match: float = 0.2, max_age: int = 30,
                 min_hits: int = 3, fps: float = 30.0) -> None:
        self.iou_match = iou_match
        self.max_age = max_age
        self.min_hits = min_hits
        self.fps = fps
        self.tracks: list[Track] = []
        self._next_id = 1
        self._frame = 0

    def update(self, detections: list[Detection], conf_high: float,
               conf_low: float) -> list[Track]:
        self._frame += 1
        for tr in self.tracks:
            tr.age += 1
            tr.time_since_update += 1

        high = [d for d in detections if d.score >= conf_high]
        low = [d for d in detections if conf_low <= d.score < conf_high]

        # рунда 1: сви трагови ↔ поуздане детекције
        m1, free_t, free_high = _match(self.tracks, high, self.iou_match)
        for ti, di in m1:
            self._absorb(self.tracks[ti], high[di])

        # рунда 2: преостали трагови ↔ слабе детекције
        remaining = [self.tracks[i] for i in free_t]
        m2, _, _ = _match(remaining, low, self.iou_match)
        for ti, di in m2:
            self._absorb(remaining[ti], low[di])

        # нови трагови из неупарених поузданих детекција
        for di in free_high:
            self._spawn(high[di])

        # избаци застареле
        self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]

        for t in self.tracks:
            if t.hits >= self.min_hits:
                t.confirmed = True

        return [t for t in self.tracks if t.confirmed and t.time_since_update == 0]

    # ------------------------------------------------------------------
    def _absorb(self, track: Track, det: Detection) -> None:
        track.bbox = det.bbox
        track.score = det.score
        track.hits += 1
        track.time_since_update = 0
        cx, cy = det.center
        track.history.append((self._frame, cx, cy))
        if len(track.history) > _HISTORY:
            track.history.pop(0)

    def _spawn(self, det: Detection) -> None:
        cx, cy = det.center
        self.tracks.append(
            Track(
                id=self._next_id,
                kind=det.kind,
                bbox=det.bbox,
                score=det.score,
                history=[(self._frame, cx, cy)],
            )
        )
        self._next_id += 1
