import math

from cuvar.power import average_power_w, estimated_runtime_h


def test_all_sleep():
    assert average_power_w(active_w=2.5, sleep_w=0.3, triggers_per_hour=0, seconds_per_trigger=6) == 0.3


def test_mixed_duty_cycle():
    # 10 догађаја/h × 6 s = 60 s активно, 3540 s спава
    avg = average_power_w(2.4, 0.3, triggers_per_hour=10, seconds_per_trigger=6)
    expected = (2.4 * 60 + 0.3 * 3540) / 3600
    assert math.isclose(avg, expected, rel_tol=1e-9)


def test_runtime_days():
    hours = estimated_runtime_h(battery_wh=77, active_w=2.4, sleep_w=0.35,
                                triggers_per_hour=4, seconds_per_trigger=6)
    assert hours > 24 * 5   # бар неколико дана
    assert hours < 24 * 30


def test_zero_power_is_infinite():
    assert estimated_runtime_h(77, 0, 0, 0) == math.inf
