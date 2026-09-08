import numpy as np

from znak.classifier import KnnClassifier
from znak.normalize import normalize_landmarks
from znak.poses import POSES, sample


def _trained(k=5, per=30, seed=0):
    rng = np.random.default_rng(seed)
    letters = list(POSES)
    X = [normalize_landmarks(sample(l, rng)) for l in letters for _ in range(per)]
    y = [l for l in letters for _ in range(per)]
    return KnnClassifier(k=k).fit(X, y)


def test_recognizes_held_out_samples():
    clf = _trained()
    rng = np.random.default_rng(12345)
    letters = list(POSES)
    correct = 0
    for letter in letters:
        for _ in range(12):
            label, conf = clf.predict(normalize_landmarks(sample(letter, rng)))
            correct += label == letter
    assert correct >= int(0.8 * len(letters) * 12)


def test_confidence_in_unit_range():
    clf = _trained()
    _, conf = clf.predict(normalize_landmarks(POSES["O"]))
    assert 0.0 <= conf <= 1.0


def test_save_load(tmp_path):
    clf = _trained()
    p = str(tmp_path / "m.npz")
    clf.save(p)
    clf2 = KnnClassifier.load(p)
    q = normalize_landmarks(POSES["L"])
    assert clf.predict(q) == clf2.predict(q)
    assert clf2.labels == sorted(POSES)


def test_fit_length_mismatch():
    import pytest

    with pytest.raises(ValueError):
        KnnClassifier().fit(np.zeros((3, 42)), ["A", "B"])
