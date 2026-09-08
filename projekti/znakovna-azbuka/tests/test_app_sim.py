import numpy as np

from znak.app import App
from znak.camera import SimSource
from znak.classifier import KnnClassifier
from znak.config import Config
from znak.hands.dummy_backend import DummyHands
from znak.normalize import normalize_landmarks
from znak.poses import POSES, sample


def _classifier(k=5, per=30, seed=0):
    rng = np.random.default_rng(seed)
    letters = list(POSES)
    X = [normalize_landmarks(sample(l, rng)) for l in letters for _ in range(per)]
    y = [l for l in letters for _ in range(per)]
    return KnnClassifier(k=k).fit(X, y)


def test_sim_recognizes_sequence():
    cfg = Config()
    cfg.camera.source = "sim"
    cfg.vote.window = 8
    cfg.vote.min_count = 4
    cfg.vote.min_confidence = 0.4
    cfg.classifier.min_confidence = 0.4

    seq = ["B", "A", "D", "O", "L"]
    hold = 14
    app = App(
        cfg,
        _classifier(),
        source=SimSource(frames=len(seq) * hold),
        detector=DummyHands(sequence=seq, hold=hold, seed=3),
    )
    stats = app.run()

    assert stats.hands_seen > 0
    hits = sum(1 for a, b in zip(stats.recognized, seq) if a == b)
    assert hits >= len(seq) - 1        # бар 4/5 тачно и редом
