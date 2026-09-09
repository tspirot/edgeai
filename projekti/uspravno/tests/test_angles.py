import numpy as np

from drzanje.angles import hip_tilt, neck_angle, shoulder_tilt, trunk_angle
from drzanje.landmarks import facing_side
from drzanje.pose.synthetic import build_landmarks


def test_upright_has_small_angles():
    lm = build_landmarks(neck_deg=0.0, trunk_deg=0.0)
    assert neck_angle(lm) < 2.0
    assert trunk_angle(lm) < 2.0


def test_forward_head_increases_neck_angle():
    a0 = neck_angle(build_landmarks(neck_deg=0.0))
    a1 = neck_angle(build_landmarks(neck_deg=25.0))
    assert a1 - a0 > 15.0


def test_slouch_increases_trunk_angle():
    a0 = trunk_angle(build_landmarks(trunk_deg=0.0))
    a1 = trunk_angle(build_landmarks(trunk_deg=20.0))
    assert a1 - a0 > 12.0


def test_neck_angle_matches_input_roughly():
    lm = build_landmarks(neck_deg=18.0, trunk_deg=0.0)
    assert abs(neck_angle(lm) - 18.0) < 3.0


def test_facing_side_from_visibility():
    assert facing_side(build_landmarks(facing="left")) == "left"
    assert facing_side(build_landmarks(facing="right")) == "right"


def test_shoulder_and_hip_tilt_signed():
    level = build_landmarks(shoulder_tilt_deg=0.0, hip_tilt_deg=0.0)
    assert abs(shoulder_tilt(level)) < 1.0
    assert abs(hip_tilt(level)) < 1.0

    tilted = build_landmarks(shoulder_tilt_deg=8.0)
    assert abs(shoulder_tilt(tilted)) > 5.0
