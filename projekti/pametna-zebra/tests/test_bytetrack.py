from zebra.detect.base import Detection
from zebra.track import ByteTracker


def _box(x, y, kind="person", score=0.9, w=40, h=100):
    return Detection(x - w / 2, y - h / 2, x + w / 2, y + h / 2, score, kind)


def test_track_confirm_and_id_stability():
    tr = ByteTracker(iou_match=0.2, max_age=5, min_hits=3, fps=30)
    active = []
    for i in range(6):
        active = tr.update([_box(100 + i * 5, 200)], conf_high=0.5, conf_low=0.1)
    assert len(active) == 1
    assert active[0].hits >= 3
    assert active[0].id == 1


def test_low_score_detection_rescues_track():
    tr = ByteTracker(iou_match=0.2, max_age=5, min_hits=2, fps=30)
    for i in range(3):
        tr.update([_box(100 + i * 4, 200, score=0.9)], 0.5, 0.1)
    # сада стиже само слаба детекција — не сме да направи нови траг, него спасава стари
    active = tr.update([_box(112, 200, score=0.3)], 0.5, 0.1)
    assert len(active) == 1
    assert active[0].id == 1
    assert tr._next_id == 2  # ниједан нови траг


def test_track_expires_after_max_age():
    tr = ByteTracker(iou_match=0.2, max_age=3, min_hits=2, fps=30)
    for _ in range(3):
        tr.update([_box(100, 200)], 0.5, 0.1)
    for _ in range(4):
        tr.update([], 0.5, 0.1)
    assert tr.tracks == []


def test_person_and_vehicle_do_not_mix():
    tr = ByteTracker(iou_match=0.05, max_age=5, min_hits=1, fps=30)
    active = tr.update(
        [_box(100, 200, "person"), _box(105, 205, "vehicle", w=60, h=60)], 0.5, 0.1
    )
    kinds = sorted(t.kind for t in active)
    assert kinds == ["person", "vehicle"]


def test_velocity_estimate():
    tr = ByteTracker(iou_match=0.2, max_age=5, min_hits=1, fps=10)
    for i in range(6):
        tr.update([_box(100 + i * 20, 200)], 0.5, 0.1)
    vx, vy = tr.tracks[0].velocity(fps=10)
    assert vx > 0 and abs(vy) < 1e-6
