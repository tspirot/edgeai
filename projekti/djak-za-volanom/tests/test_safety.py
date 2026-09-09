from volan.config import SafetyConfig
from volan.safety import SafetyArbiter


def _arb(max_throttle=0.5):
    return SafetyArbiter(SafetyConfig(), max_throttle)


def test_free_road_passes_model_through():
    d = _arb().step(model_steer=0.3, model_throttle=0.5, nearest_mm=2000, scan_age_s=0.0)
    assert not d.braking
    assert d.steer == 0.3
    assert d.throttle == 0.5


def test_throttle_clamped_to_max():
    d = _arb(0.4).step(0.0, 1.0, nearest_mm=2000, scan_age_s=0.0)
    assert d.throttle == 0.4


def test_slow_zone_reduces_throttle():
    d = _arb().step(0.0, 0.5, nearest_mm=1000, scan_age_s=0.0)  # < slow_mm 1200
    assert not d.braking
    assert 0.0 < d.throttle < 0.5


def test_close_obstacle_brakes():
    d = _arb().step(0.0, 0.5, nearest_mm=400, scan_age_s=0.0)  # < brake_mm 550
    assert d.braking
    assert d.throttle == 0.0
    assert d.steer == 0.0  # управљање и даље пролази


def test_hysteresis_keeps_braking_until_release():
    arb = _arb()
    assert arb.step(0.0, 0.5, 400, 0.0).braking          # почни кочење
    assert arb.step(0.0, 0.5, 700, 0.0).braking            # 700 < release_mm 800 → и даље кочи
    assert not arb.step(0.0, 0.5, 900, 0.0).braking        # 900 > release → пусти


def test_stale_scan_brakes():
    d = _arb().step(0.0, 0.5, nearest_mm=3000, scan_age_s=1.0)
    assert d.braking
    assert "скена" in d.reason
