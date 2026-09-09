import numpy as np
import pytest

from drzanje.landmarks import Landmarks, N_POINTS
from drzanje.pose.synthetic import build_landmarks


def test_wrong_shape_raises():
    with pytest.raises(ValueError):
        Landmarks(np.zeros((10, 3)))


def test_named_access_and_midpoint():
    lm = build_landmarks()
    ls = lm.xy("left_shoulder")
    rs = lm.xy("right_shoulder")
    mid = lm.midpoint("left_shoulder", "right_shoulder")
    assert np.allclose(mid, (ls + rs) / 2)
    assert lm.points.shape == (N_POINTS, 3)


def test_visibility_gate():
    lm = build_landmarks(facing="left")
    assert lm.visible("left_ear", 0.5)          # видљива страна
    assert not lm.visible("right_ear", 0.5)     # друга страна у профилу


def test_ema_smoothing_moves_partway():
    a = build_landmarks(neck_deg=0.0)
    b = build_landmarks(neck_deg=30.0)
    mid = a.lerp(b, 0.5)
    assert np.allclose(mid.points, (a.points + b.points) / 2)
