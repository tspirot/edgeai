import math

from zebra.safety.geometry import closest_approach, speed, time_to_conflict


def test_head_on_approach():
    # A у (0,0) иде десно 1 m/s, B у (10,0) иде лево 1 m/s, судар кад су ближе од 2 m
    ttc = time_to_conflict((0, 0), (1, 0), (10, 0), (-1, 0), radius=2.0)
    assert math.isclose(ttc, 4.0, rel_tol=1e-6)  # затвори 8 m релативном брзином 2 m/s


def test_already_in_conflict():
    assert time_to_conflict((0, 0), (0, 0), (1, 0), (0, 0), radius=2.0) == 0.0


def test_moving_apart_is_infinite():
    assert time_to_conflict((0, 0), (-1, 0), (10, 0), (1, 0), radius=2.0) == math.inf


def test_parallel_never_meets():
    assert time_to_conflict((0, 0), (1, 0), (0, 10), (1, 0), radius=2.0) == math.inf


def test_closest_approach():
    t, d = closest_approach((0, 0), (1, 0), (5, 3), (-1, 0))
    assert math.isclose(t, 2.5, rel_tol=1e-6)
    assert math.isclose(d, 3.0, rel_tol=1e-6)


def test_speed_conversion():
    assert math.isclose(speed((3, 4), meters_per_pixel=1.0), 5.0)
    assert math.isclose(speed((3, 4), meters_per_pixel=0.5), 2.5)
