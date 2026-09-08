"""Склапање: кадар → тачке шаке → нормализација → k-НН → временско гласање."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from znak.classifier import KnnClassifier
from znak.hands import build_detector
from znak.normalize import normalize_landmarks
from znak.vote import Vote

log = logging.getLogger(__name__)


@dataclass
class Stats:
    frames: int
    hands_seen: int
    recognized: list = field(default_factory=list)  # редослед исписаних слова


class App:
    def __init__(self, cfg, classifier: KnnClassifier, source=None, detector=None) -> None:
        self.cfg = cfg
        self.classifier = classifier
        self.source = source if source is not None else _open(cfg)
        self.detector = detector if detector is not None else build_detector(cfg.hands)
        self.vote = Vote(cfg.vote.window, cfg.vote.min_count, cfg.vote.min_confidence)

    def run(self, max_frames: int | None = None) -> Stats:
        frames = hands = 0
        recognized: list[str] = []
        last_output: "str | None" = None
        try:
            for frame, _t in self.source:
                frames += 1
                pts = self.detector.detect(frame)
                if pts is None:
                    self.vote.push("", 0.0)
                else:
                    hands += 1
                    vec = normalize_landmarks(pts)
                    label, conf = self.classifier.predict(vec)
                    if conf < self.cfg.classifier.min_confidence:
                        label, conf = "", 0.0
                    out = self.vote.push(label, conf)
                    if out and out != last_output:
                        recognized.append(out)
                        last_output = out
                        log.info("Слово: %s", out)
                if max_frames and frames >= max_frames:
                    break
        finally:
            for obj in (self.source, self.detector):
                if hasattr(obj, "close"):
                    obj.close()
        return Stats(frames, hands, recognized)


def _open(cfg):
    from znak.camera import open_source

    return open_source(cfg)
