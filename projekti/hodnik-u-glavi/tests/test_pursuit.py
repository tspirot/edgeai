import numpy as np

from mapa.config import PursuitConfig
from mapa.pose import Pose
from mapa.pursuit import pure_pursuit


def test_straight_path_goes_straight():
    path = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)]
    cmd = pure_pursuit(Pose(0.0, 0.0, 0.0), path, PursuitConfig(lookahead_m=0.8))
    assert abs(cmd.steer) < 1e-6
    assert cmd.speed > 0
    assert not cmd.done


def test_target_to_the_left_steers_left():
    path = [(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    cmd = pure_pursuit(Pose(0.0, 0.0, 0.0), path, PursuitConfig(lookahead_m=0.5))
    assert cmd.steer > 0                         # позитивно = лево (CCW)


def test_reaches_goal_within_tolerance():
    path = [(0.0, 0.0), (1.0, 0.0)]
    cmd = pure_pursuit(Pose(0.95, 0.0, 0.0), path, PursuitConfig(goal_tol_m=0.2))
    assert cmd.done
    assert cmd.speed == 0.0


def test_empty_path_is_done():
    cmd = pure_pursuit(Pose(), [], PursuitConfig())
    assert cmd.done and cmd.speed == 0.0


def test_steer_clamped():
    path = [(0.0, 0.0), (0.1, 2.0)]              # оштар угао
    cmd = pure_pursuit(Pose(0.0, 0.0, 0.0), path, PursuitConfig(max_steer_rad=0.4, lookahead_m=0.3))
    assert abs(cmd.steer) <= 0.4 + 1e-9
