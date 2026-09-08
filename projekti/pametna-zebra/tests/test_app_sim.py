from zebra.app import App
from zebra.config import Config
from zebra.detect.dummy_backend import DummyDetector
from zebra.video.source import SimSource


def _cfg():
    cfg = Config()
    cfg.video.source = "sim"
    cfg.detect.backend = "dummy"
    cfg.io.gpio = False
    cfg.io.log_file = None
    cfg.track.min_hits = 3
    return cfg


def test_sim_pipeline_counts_and_warns():
    cfg = _cfg()
    app = App(
        cfg,
        source=SimSource(cfg.video.width, cfg.video.height, cfg.video.fps, frames=120),
        detector=DummyDetector(cfg, cfg.video.width, cfg.video.height),
    )
    stats = app.run()

    assert stats.frames == 120
    assert stats.counts.get("person", 0) == 1
    assert stats.counts.get("vehicle", 0) == 1
    # путеви пешака и возила се секу у симулацији → бар једно упозорење
    assert stats.warning_events >= 1


def test_scripted_scene_no_warning_without_vehicle():
    from zebra.detect.base import Detection

    cfg = _cfg()
    # пешак корача, нема возила
    script = [
        [Detection(100 + i * 6, 300, 140 + i * 6, 420, 0.9, "person")]
        for i in range(40)
    ]
    app = App(
        cfg,
        source=SimSource(cfg.video.width, cfg.video.height, frames=len(script)),
        detector=DummyDetector(cfg, script=script),
    )
    stats = app.run()
    assert stats.counts.get("person", 0) == 1
    assert stats.counts.get("vehicle", 0) == 0
    assert stats.warning_events == 0
