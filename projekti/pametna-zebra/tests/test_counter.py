import csv
from dataclasses import dataclass

from zebra.io.counter import Counter
from zebra.safety.zone import Polygon, Scene


@dataclass
class T:
    id: int
    kind: str
    _c: tuple = (5, 5)

    @property
    def center(self):
        return self._c


def _scene():
    return Scene(crosswalk=Polygon([(0, 0), (10, 0), (10, 10), (0, 10)]))


def test_unique_counting():
    c = Counter(interval_s=1000)
    scene = _scene()
    c.update([T(1, "person"), T(2, "vehicle")], scene, now=0.0)
    c.update([T(1, "person"), T(2, "vehicle")], scene, now=0.5)  # исти трагови
    c.update([T(3, "person")], scene, now=0.9)
    assert c.total == {"person": 2, "vehicle": 1}
    assert c.zones["crosswalk"] == {1, 2, 3}


def test_interval_flush_writes_csv(tmp_path):
    path = tmp_path / "brojac.csv"
    c = Counter(log_file=path, interval_s=1.0)
    scene = _scene()
    c.update([T(1, "person")], scene, now=0.0)
    c.update([T(2, "person")], scene, now=1.0)   # окида flush за прозор [0,1)
    c.update([T(3, "vehicle")], scene, now=2.0)  # окида flush за [1,2)
    assert len(c.rows) == 2
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows[0]["pesaci"] == "1"
    assert rows[1]["pesaci"] == "1"


def test_close_flushes_remainder():
    c = Counter(interval_s=100)
    c.update([T(1, "person")], _scene(), now=0.0)
    c.close(now=5.0)
    assert len(c.rows) == 1
    assert c.rows[0]["pesaci"] == 1
