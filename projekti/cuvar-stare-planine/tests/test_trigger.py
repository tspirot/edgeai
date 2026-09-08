import numpy as np

from cuvar.trigger import MotionTrigger


def _dark(h=120, w=160):
    return np.full((h, w, 3), 18, dtype=np.uint8)


def _with_blob(h=120, w=160):
    f = _dark(h, w)
    f[40:80, 40:120] = 200
    return f


def test_no_trigger_on_static_scene():
    tr = MotionTrigger(change_fraction=0.02, warmup_frames=2, cooldown_s=0)
    out = [tr.update(_dark(), t) for t in range(10)]
    assert not any(o["triggered"] for o in out)


def test_trigger_on_motion_after_warmup():
    tr = MotionTrigger(change_fraction=0.02, warmup_frames=3, cooldown_s=0)
    for t in range(4):
        tr.update(_dark(), t)
    out = tr.update(_with_blob(), 4)
    assert out["triggered"] is True
    assert out["motion"] > 0.02


def test_cooldown_blocks_repeat():
    tr = MotionTrigger(change_fraction=0.02, warmup_frames=1, cooldown_s=5.0)
    tr.update(_dark(), 0)
    assert tr.update(_with_blob(), 1)["triggered"] is True
    assert tr.update(_with_blob(), 2)["triggered"] is False   # у cooldown-у
    assert tr.update(_with_blob(), 7)["triggered"] is True    # после cooldown-а


def test_warmup_suppresses_early_frames():
    tr = MotionTrigger(change_fraction=0.02, warmup_frames=5, cooldown_s=0)
    assert tr.update(_with_blob(), 0)["triggered"] is False
