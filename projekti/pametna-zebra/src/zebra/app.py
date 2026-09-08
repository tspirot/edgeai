"""Склапање: слика → детекција → праћење → бројач + правило упозорења → LED/приказ."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from zebra.detect import build_detector
from zebra.io.counter import Counter
from zebra.io.gpio_led import WarningLight
from zebra.safety.policy import WarningPolicy
from zebra.safety.zone import Scene
from zebra.track import ByteTracker
from zebra.video.source import open_source

log = logging.getLogger(__name__)


@dataclass
class Stats:
    frames: int
    counts: dict
    warning_frames: int
    warning_events: int


def load_scene(cfg) -> Scene:
    path = Path(cfg.zone.file)
    if path.exists():
        log.info("Зоне из %s", path)
        return Scene.from_file(path)
    log.info("Нема %s — користим подразумеване зоне (покрени `zebra calibrate`).", path)
    return Scene.default(cfg.video.width, cfg.video.height)


class App:
    def __init__(self, cfg, source=None, detector=None, scene=None,
                 display=None, light=None) -> None:
        self.cfg = cfg
        self.source = source if source is not None else open_source(cfg)
        self.fps = getattr(self.source, "fps", cfg.video.fps) or cfg.video.fps
        self.detector = detector if detector is not None else build_detector(cfg.detect)
        self.scene = scene if scene is not None else load_scene(cfg)
        self.tracker = ByteTracker(
            cfg.track.iou_match, cfg.track.max_age, cfg.track.min_hits, self.fps
        )
        self.policy = WarningPolicy(cfg.safety)
        self.counter = Counter(cfg.io.log_file, cfg.io.log_interval_s)
        self.light = light if light is not None else WarningLight(cfg.io)
        self.display = display

    def run(self, max_frames: int | None = None) -> Stats:
        frames = warn_frames = events = 0
        prev_warn = False
        last_t = 0.0
        try:
            for frame, t in self.source:
                last_t = t
                detections = self.detector.detect(frame)
                tracks = self.tracker.update(
                    detections, self.cfg.detect.conf, self.cfg.detect.conf_low
                )
                self.counter.update(tracks, self.scene, t)
                state = self.policy.evaluate(tracks, self.scene, t, self.fps)
                self.light.set(state.active)

                if state.active:
                    warn_frames += 1
                    if not prev_warn:
                        events += 1
                        log.info("УПОЗОРЕЊЕ: %s", state.reason)
                prev_warn = state.active

                if self.display is not None:
                    if self.display.render(frame, tracks, state, self.counter, self.scene) is False:
                        break

                frames += 1
                if max_frames and frames >= max_frames:
                    break
        finally:
            self.counter.close(last_t)
            self.light.close()
            self.detector.close()
            for obj in (self.source, self.display):
                if obj is not None and hasattr(obj, "close"):
                    obj.close()

        return Stats(frames, dict(self.counter.total), warn_frames, events)
