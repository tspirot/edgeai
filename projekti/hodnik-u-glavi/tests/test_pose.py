import numpy as np

from mapa.pose import Pose, from_matrix


def test_transform_translation():
    pts = np.array([[1.0, 0.0], [0.0, 1.0]])
    out = Pose(2.0, 3.0, 0.0).transform(pts)
    assert np.allclose(out, [[3.0, 3.0], [2.0, 4.0]])


def test_transform_rotation_90():
    out = Pose(0.0, 0.0, np.pi / 2).transform(np.array([[1.0, 0.0]]))
    assert np.allclose(out, [[0.0, 1.0]], atol=1e-9)


def test_matrix_roundtrip():
    p = Pose(1.5, -2.0, 0.7)
    assert np.allclose([*from_matrix(p.as_matrix()).__dict__.values()],
                       [p.x, p.y, p.theta])


def test_compose_is_matrix_product():
    a, b = Pose(1.0, 0.0, np.pi / 2), Pose(1.0, 0.0, 0.0)
    c = a.compose(b)                      # помери напред у оквиру a → +y глобално
    assert np.allclose([c.x, c.y], [1.0, 1.0], atol=1e-9)
