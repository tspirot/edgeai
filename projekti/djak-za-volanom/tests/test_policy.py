import numpy as np

from volan.config import ModelConfig
from volan.policy import build_policy, preprocess
from volan.policy.heuristic_policy import HeuristicPolicy


def test_preprocess_shape_and_range():
    img = np.full((120, 160, 3), 255, dtype=np.uint8)
    x = preprocess(img, 160, 120)
    assert x.shape == (1, 120, 160, 3)
    assert x.dtype == np.float32
    assert 0.0 <= x.min() and x.max() <= 1.0


def test_preprocess_resizes():
    img = np.zeros((240, 320, 3), dtype=np.uint8)
    assert preprocess(img, 160, 120).shape == (1, 120, 160, 3)


def test_heuristic_follows_bright_lane():
    h, w = 120, 160
    img = np.full((h, w, 3), 20, dtype=np.uint8)
    img[80:, 130:150, :] = 240          # светла трака десно
    steer, throttle = HeuristicPolicy(cruise_throttle=0.4).predict(img)
    assert steer > 0.2                    # скреће десно
    assert throttle == 0.4


def test_heuristic_centered_lane_goes_straight():
    h, w = 120, 160
    img = np.full((h, w, 3), 20, dtype=np.uint8)
    img[80:, 74:86, :] = 240
    steer, _ = HeuristicPolicy().predict(img)
    assert abs(steer) < 0.1


def test_build_policy_dummy_and_heuristic():
    d = build_policy(ModelConfig(backend="dummy", cruise_throttle=0.25))
    assert d.predict(np.zeros((120, 160, 3), np.uint8)) == (0.0, 0.25)
    assert isinstance(build_policy(ModelConfig(backend="heuristic")), HeuristicPolicy)


def test_build_policy_unknown_raises():
    import pytest

    with pytest.raises(ValueError):
        build_policy(ModelConfig(backend="нешто"))
