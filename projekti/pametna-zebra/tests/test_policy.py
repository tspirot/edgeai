from dataclasses import dataclass

from zebra.config import SafetyConfig
from zebra.safety.policy import WarningPolicy
from zebra.safety.zone import Polygon, Scene


@dataclass
class FakeTrack:
    id: int
    kind: str
    _c: tuple
    _v: tuple

    @property
    def center(self):
        return self._c

    def velocity(self, fps):
        return self._v


def _scene():
    return Scene(
        crosswalk=Polygon([(0, 0), (100, 0), (100, 100), (0, 100)]),
        roadway=Polygon([(0, 0), (100, 0), (100, 400), (0, 400)]),
    )


def _cfg(**kw):
    c = SafetyConfig()
    c.meters_per_pixel = 1.0
    c.conflict_radius_m = 5.0
    c.ttc_seconds = 3.0
    c.hold_seconds = 2.0
    for k, v in kw.items():
        setattr(c, k, v)
    return c


def test_warns_when_vehicle_closes_on_pedestrian():
    policy = WarningPolicy(_cfg())
    person = FakeTrack(1, "person", (50, 50), (0, 0))
    vehicle = FakeTrack(2, "vehicle", (50, 200), (0, -60))  # долази ка пешаку, 60 m/s
    state = policy.evaluate([person, vehicle], _scene(), now=0.0, fps=30)
    assert state.active is True
    assert state.ttc <= 3.0


def test_no_warning_for_parked_vehicle():
    policy = WarningPolicy(_cfg())
    person = FakeTrack(1, "person", (50, 50), (0, 0))
    vehicle = FakeTrack(2, "vehicle", (50, 60), (0, 0))  # мирује
    state = policy.evaluate([person, vehicle], _scene(), now=0.0, fps=30)
    assert state.active is False


def test_hysteresis_holds_warning():
    policy = WarningPolicy(_cfg(hold_seconds=2.0))
    person = FakeTrack(1, "person", (50, 50), (0, 0))
    vehicle = FakeTrack(2, "vehicle", (50, 200), (0, -60))
    assert policy.evaluate([person, vehicle], _scene(), now=0.0, fps=30).active is True
    # опасност прошла (нема возила), али упозорење се још држи
    assert policy.evaluate([person], _scene(), now=1.0, fps=30).active is True
    assert policy.evaluate([person], _scene(), now=3.5, fps=30).active is False
