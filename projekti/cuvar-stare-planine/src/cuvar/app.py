"""Склапање: кадар → окидач по покрету → класификација → (клима + чување)."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from cuvar.camera import open_source
from cuvar.classify import build_classifier
from cuvar.climate import build_sensor
from cuvar.storage import EventStore
from cuvar.trigger import MotionTrigger

log = logging.getLogger(__name__)


@dataclass
class Stats:
    frames: int
    triggers: int
    saved: int
    species_counts: dict


class App:
    def __init__(self, cfg, source=None, classifier=None, sensor=None, store=None) -> None:
        self.cfg = cfg
        self.source = source if source is not None else open_source(cfg)
        self.trigger = MotionTrigger(
            cfg.trigger.change_fraction, cfg.trigger.pixel_delta,
            cfg.trigger.cooldown_s, cfg.trigger.warmup_frames,
        )
        self.classifier = classifier if classifier is not None else build_classifier(cfg.classify)
        self.sensor = sensor if sensor is not None else build_sensor(cfg.climate)
        self.store = store if store is not None else EventStore(
            cfg.storage.dir, cfg.storage.keep_last, cfg.storage.save_images
        )

    def run(self, max_frames: int | None = None) -> Stats:
        frames = triggers = saved = 0
        try:
            for frame, t in self.source:
                frames += 1
                motion = self.trigger.update(frame, t)
                if motion["triggered"]:
                    triggers += 1
                    pred = self.classifier.classify(frame)
                    if pred is not None and pred.score >= self.cfg.classify.min_score:
                        climate = self.sensor.read().as_dict()
                        img = frame if self.cfg.storage.save_images else None
                        self.store.record(pred.label, pred.score, climate, img)
                        saved += 1
                        log.info("Снимак: %s (%.2f)", pred.label, pred.score)
                if max_frames and frames >= max_frames:
                    break
        finally:
            for obj in (self.source, self.classifier, self.sensor):
                if hasattr(obj, "close"):
                    obj.close()
        return Stats(frames, triggers, saved, dict(self.store.species_counts))
