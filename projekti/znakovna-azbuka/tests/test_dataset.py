import numpy as np

from znak.dataset import append_sample, counts, load_dataset
from znak.normalize import normalize_landmarks
from znak.poses import POSES


def test_append_and_load(tmp_path):
    p = tmp_path / "d.csv"
    append_sample(p, "A", POSES["A"])
    append_sample(p, "B", POSES["B"])
    append_sample(p, "A", POSES["A"])

    X, y = load_dataset(p)
    assert y == ["A", "B", "A"]
    assert X.shape == (3, 42)
    assert np.allclose(X[0], normalize_landmarks(POSES["A"]), atol=1e-3)


def test_counts(tmp_path):
    p = tmp_path / "d.csv"
    for label in ["A", "A", "B", "V", "A"]:
        append_sample(p, label, POSES[label])
    assert counts(p) == {"A": 3, "B": 1, "V": 1}


def test_empty_file(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    X, y = load_dataset(p)
    assert y == [] and X.shape == (0, 42)
