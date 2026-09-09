import numpy as np

from mapa.planner import a_star, inflate


def test_astar_straight_line_when_clear():
    blocked = np.zeros((10, 10), dtype=bool)
    path = a_star(blocked, (0, 0), (9, 0), allow_diagonal=False)
    assert path[0] == (0, 0) and path[-1] == (9, 0)
    assert len(path) == 10


def test_astar_routes_around_wall():
    blocked = np.zeros((10, 10), dtype=bool)
    blocked[0:8, 5] = True                      # вертикални зид, пролаз на дну (редови 8–9)
    path = a_star(blocked, (2, 4), (8, 4), allow_diagonal=True)
    assert path
    assert path[0] == (2, 4) and path[-1] == (8, 4)
    assert all(not blocked[y, x] for x, y in path)
    assert any(y >= 8 for _, y in path)         # мора да прође кроз доњи пролаз


def test_astar_no_path_returns_empty():
    blocked = np.zeros((10, 10), dtype=bool)
    blocked[:, 5] = True                        # потпун зид
    assert a_star(blocked, (0, 0), (9, 9)) == []


def test_astar_blocked_start_or_goal():
    blocked = np.zeros((5, 5), dtype=bool)
    blocked[0, 0] = True
    assert a_star(blocked, (0, 0), (4, 4)) == []


def test_inflate_grows_obstacle():
    occ = np.zeros((7, 7), dtype=bool)
    occ[3, 3] = True
    out = inflate(occ, 1)
    assert out[2:5, 2:5].all()
    assert not out[0, 0]
