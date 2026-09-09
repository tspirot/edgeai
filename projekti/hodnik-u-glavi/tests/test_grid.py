import numpy as np

from mapa.config import GridConfig
from mapa.grid import OccupancyGrid, _bresenham


def test_bresenham_endpoints_and_straight_line():
    cells = _bresenham(0, 0, 3, 0)
    assert cells[0] == (0, 0) and cells[-1] == (3, 0)
    assert len(cells) == 4


def test_bresenham_diagonal():
    cells = _bresenham(0, 0, 2, 2)
    assert cells == [(0, 0), (1, 1), (2, 2)]


def test_world_cell_roundtrip():
    g = OccupancyGrid(GridConfig(res_m=0.1, size_m=4.0))
    cx, cy = g.world_to_cell([0.0, 0.0])
    assert (cx, cy) == (20, 20)                 # центар мапе
    cx, cy = g.world_to_cell([1.05, -0.95])
    assert (cx, cy) == (30, 10)


def test_integrate_marks_free_and_occupied():
    g = OccupancyGrid(GridConfig(res_m=0.1, size_m=6.0))
    sensor = np.array([0.0, 0.0])
    hit = np.array([[1.0, 0.0]])               # препрека 1 m испред
    g.integrate(sensor, hit)

    # ћелија на препреци је заузета
    hx, hy = g.world_to_cell(hit[0])
    assert g.logodds[hy, hx] > 0
    # ћелија на пола пута је слободна
    mx, my = g.world_to_cell([0.5, 0.0])
    assert g.logodds[my, mx] < 0


def test_repeated_hits_saturate_but_clamp():
    g = OccupancyGrid(GridConfig(res_m=0.1, size_m=6.0, clamp=3.0))
    for _ in range(50):
        g.integrate(np.array([0.0, 0.0]), np.array([[0.8, 0.0]]))
    assert g.logodds.max() <= 3.0
    assert g.occupied_mask().any()


def test_to_image_values():
    g = OccupancyGrid(GridConfig(res_m=0.1, size_m=4.0))
    g.integrate(np.array([0.0, 0.0]), np.array([[1.0, 0.0]]))
    img = g.to_image()
    vals = set(np.unique(img)) - {127}
    assert vals <= {0, 255}
    assert 0 in vals and 255 in vals
