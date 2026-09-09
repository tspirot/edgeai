import numpy as np

from mapa.icp import icp
from mapa.pose import Pose


def _cloud(seed=0, n=120):
    rng = np.random.default_rng(seed)
    # тачке дуж две зидне линије (угао просторије)
    a = np.column_stack([np.linspace(0, 3, n // 2), np.zeros(n // 2)])
    b = np.column_stack([np.zeros(n // 2), np.linspace(0, 2, n // 2)])
    return np.vstack([a, b]) + rng.normal(0, 0.002, (n, 2))


def test_recovers_pure_translation():
    tgt = _cloud()
    move = Pose(0.3, -0.15, 0.0)
    src = move.transform(tgt)                    # померен облак
    res = icp(src, tgt, max_pairs_dist=1.0, max_iter=60)
    # ICP треба да нађе (приближно) инверзно померање
    assert res.converged
    assert abs(res.pose.x + 0.3) < 0.06      # инверзно померање
    assert abs(res.pose.y - 0.15) < 0.06
    assert res.fitness > 0.9
    assert res.rmse < 0.05


def test_recovers_rotation():
    tgt = _cloud()
    move = Pose(0.1, 0.05, np.deg2rad(10))
    src = move.transform(tgt)
    res = icp(src, tgt, max_pairs_dist=1.0, max_iter=80)
    assert abs(res.pose.theta + np.deg2rad(10)) < np.deg2rad(3)


def test_degenerate_input_returns_gracefully():
    res = icp(np.zeros((2, 2)), np.zeros((2, 2)))
    assert not res.converged
    assert res.fitness == 0.0
