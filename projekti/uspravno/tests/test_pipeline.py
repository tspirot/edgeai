from drzanje.config import Config
from drzanje.pipeline import Monitor, calibrate
from drzanje.pose.base import PoseBackend
from drzanje.pose.synthetic import build_landmarks
from drzanje.posture import Reference


class ScriptedPose(PoseBackend):
    """Врати задату секвенцу углова (neck, trunk) по кораку."""

    def __init__(self, seq):
        self.seq = seq
        self.i = 0

    def detect(self, image):
        n, t = self.seq[min(self.i, len(self.seq) - 1)]
        self.i += 1
        return build_landmarks(neck_deg=n, trunk_deg=t)


class RecordingFeedback:
    def __init__(self):
        self.count = 0

    def remind(self):
        self.count += 1

    def close(self):
        pass


def _cfg():
    cfg = Config()
    cfg.camera.backend = "dummy"
    cfg.pose.backend = "dummy"
    cfg.pose.smoothing = 0.0
    cfg.posture.bad_after_s = 1.0
    cfg.posture.alert_after_s = 3.0
    cfg.camera.fps = 10
    return cfg


def test_sim_runs_and_summarizes():
    cfg = _cfg()
    mon = Monitor(cfg)
    for i in range(120):
        mon.step(t=i * 0.1)
    s = mon.session_summary()
    mon.close()
    assert s["duration_s"] > 5
    assert s["total_bad_s"] > 0        # синтетичка поза се повремено грби
    assert s["events"] >= 1


def test_good_posture_no_alert():
    cfg = _cfg()
    fb = RecordingFeedback()
    mon = Monitor(cfg, pose=ScriptedPose([(4.0, 3.0)] * 50), feedback=fb,
                  reference=Reference(4.0, 3.0))
    for i in range(50):
        mon.step(t=i * 0.5)
    assert fb.count == 0
    assert mon.session_summary()["total_bad_s"] == 0.0


def test_sustained_slouch_triggers_feedback():
    cfg = _cfg()
    fb = RecordingFeedback()
    mon = Monitor(cfg, pose=ScriptedPose([(28.0, 18.0)] * 40), feedback=fb,
                  reference=Reference(4.0, 3.0))
    for i in range(40):
        mon.step(t=i * 1.0)
    assert fb.count >= 1


def test_calibrate_returns_reference_near_truth():
    cfg = _cfg()
    ref = calibrate(cfg, pose=ScriptedPose([(6.0, 4.0)] * 60), samples=20)
    assert abs(ref.neck_deg - 6.0) < 2.0
    assert abs(ref.trunk_deg - 4.0) < 2.0


def test_reference_save_load(tmp_path):
    p = tmp_path / "ref.json"
    Reference(7.5, 4.2).save(p)
    r = Reference.load(p)
    assert r.neck_deg == 7.5 and r.trunk_deg == 4.2
