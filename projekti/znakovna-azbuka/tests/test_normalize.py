import numpy as np

from znak.normalize import normalize_landmarks
from znak.poses import POSES


def test_output_shape():
    v = normalize_landmarks(POSES["V"])
    assert v.shape == (42,)


def test_invariant_to_translate_scale_rotate():
    base = POSES["D"]
    v0 = normalize_landmarks(base)
    rng = np.random.default_rng(0)
    for _ in range(6):
        ang = rng.uniform(-1.2, 1.2)
        c, s = np.cos(ang), np.sin(ang)
        pts = base @ np.array([[c, -s], [s, c]])
        pts = pts * rng.uniform(0.4, 2.5)
        pts = pts + rng.uniform(-8, 8, 2)
        assert np.allclose(normalize_landmarks(pts), v0, atol=1e-3)


def test_different_letters_differ():
    a = normalize_landmarks(POSES["A"])
    b = normalize_landmarks(POSES["B"])
    assert np.linalg.norm(a - b) > 0.3
