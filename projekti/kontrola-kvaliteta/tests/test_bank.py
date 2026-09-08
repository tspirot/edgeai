import numpy as np

from qc.bank import MemoryBank, _greedy_coreset


def test_known_vector_scores_near_zero():
    bank = MemoryBank(k=1).fit(np.array([[0.0, 0.0], [10.0, 10.0], [5.0, 0.0]]))
    assert bank.score_vectors(np.array([[10.0, 10.0]]))[0] < 1e-4


def test_score_grows_with_distance():
    bank = MemoryBank(k=1).fit(np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]))
    near = bank.score_vectors(np.array([[0.1, 0.1]]))[0]
    far = bank.score_vectors(np.array([[40.0, 40.0]]))[0]
    assert far > near > 0


def test_coreset_reduces_size():
    v = np.random.default_rng(0).normal(size=(200, 4))
    bank = MemoryBank().fit(v, coreset_fraction=0.25)
    assert len(bank._bank) == 50


def test_greedy_coreset_picks_spread():
    v = np.array([[0.0, 0.0], [0.01, 0.0], [10.0, 10.0]])
    sub = _greedy_coreset(v, 2)
    assert len(sub) == 2
    # мора да укључи удаљену тачку, не две скоро исте
    assert any(np.allclose(p, [10.0, 10.0]) for p in sub)


def test_save_load_roundtrip():
    v = np.random.default_rng(1).normal(size=(20, 3))
    b1 = MemoryBank(k=2).fit(v)
    b2 = MemoryBank.from_dict(b1.to_dict())
    q = np.array([[0.2, 0.1, -0.3]])
    assert np.allclose(b1.score_vectors(q), b2.score_vectors(q))
