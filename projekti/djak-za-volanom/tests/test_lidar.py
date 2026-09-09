import pytest

from volan.lidar import DummyLidar, nearest_in_cone


def test_point_in_cone_is_seen():
    scan = [(0.0, 500.0), (90.0, 200.0), (180.0, 300.0)]
    assert nearest_in_cone(scan, cone_deg=60) == 500.0  # само тачка на 0° је у конусу


def test_point_outside_cone_ignored():
    scan = [(45.0, 200.0), (0.0, 900.0)]
    assert nearest_in_cone(scan, cone_deg=60) == 900.0  # 45° је ван ±30°


def test_wraparound_angles():
    scan = [(350.0, 400.0), (10.0, 600.0)]
    assert nearest_in_cone(scan, cone_deg=60) == 400.0  # 350° == −10°, у конусу


def test_forward_offset_shifts_cone():
    scan = [(90.0, 350.0), (0.0, 800.0)]
    assert nearest_in_cone(scan, cone_deg=40, forward_offset_deg=90.0) == 350.0


def test_noise_and_range_filtered():
    scan = [(0.0, 50.0), (2.0, 9000.0), (0.0, 700.0)]
    assert nearest_in_cone(scan, cone_deg=60, min_valid_mm=120, max_range_mm=4000) == 700.0


def test_empty_cone_returns_max_range():
    assert nearest_in_cone([(180.0, 500.0)], cone_deg=60, max_range_mm=4000) == 4000.0


def test_invalid_cone_raises():
    with pytest.raises(ValueError):
        nearest_in_cone([], cone_deg=0)


def test_dummy_lidar_reports_obstacle():
    lidar = DummyLidar(obstacle_mm=600.0)
    scan, ts = lidar.latest()
    assert ts > 0
    assert nearest_in_cone(scan, cone_deg=30) == 600.0
    lidar.set_obstacle(300.0)
    scan, _ = lidar.latest()
    assert nearest_in_cone(scan, cone_deg=30) == 300.0
