from cuvar.app import App
from cuvar.camera import SimSource
from cuvar.classify.dummy_backend import DummyClassifier
from cuvar.climate.dummy_backend import DummySensor
from cuvar.config import Config
from cuvar.storage import EventStore


def _app(tmp_path, **overrides):
    cfg = Config()
    cfg.classify.backend = "dummy"
    cfg.climate.backend = "dummy"
    cfg.storage.save_images = False
    for k, v in overrides.items():
        setattr(cfg.trigger, k, v)
    return App(
        cfg,
        source=SimSource(320, 240, 10.0, frames=300),
        classifier=DummyClassifier(cfg.classify),
        sensor=DummySensor(),
        store=EventStore(tmp_path, save_images=False),
    )


def test_sim_camera_trap(tmp_path):
    app = _app(tmp_path)
    stats = app.run()

    assert stats.frames == 300
    assert stats.triggers >= 3
    assert stats.saved == stats.triggers
    assert sum(stats.species_counts.values()) == stats.saved
    # снимљени су само догађаји, не сваки кадар
    assert stats.saved < stats.frames


def test_climate_sidecar_written(tmp_path):
    app = _app(tmp_path)
    app.run()
    jsons = list(tmp_path.glob("*.json"))
    assert jsons
    import json

    data = json.loads(jsons[0].read_text(encoding="utf-8"))
    assert "temp_c" in data["climate"]
    assert "aqi" in data["climate"]
