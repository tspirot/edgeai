import numpy as np

from volan.recorder import TubWriter, read_tub


def test_write_then_read_roundtrip(tmp_path):
    w = TubWriter(tmp_path, jpg_quality=95, session="s1")
    for i in range(5):
        img = np.full((120, 160, 3), i * 40, dtype=np.uint8)
        w.add(img, steer=i / 10.0, throttle=0.3)
    assert w.count == 5

    X, y = read_tub(tmp_path)
    assert X.shape == (5, 120, 160, 3)
    assert y.shape == (5, 2)
    assert np.allclose(y[:, 0], [0.0, 0.1, 0.2, 0.3, 0.4], atol=1e-4)
    assert np.allclose(y[:, 1], 0.3)


def test_read_missing_tub_raises(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        read_tub(tmp_path / "prazno")
