import numpy as np

from qc.config import Config
from qc.data import synthetic_defect, synthetic_ok
from qc.features.handcrafted import HandcraftedExtractor


def _ext(size=128, grid=8):
    cfg = Config()
    cfg.features.image_size = size
    cfg.features.grid = grid
    return HandcraftedExtractor(cfg.features)


def test_output_shape():
    bf = _ext().extract(np.full((128, 128), 128, np.uint8))
    assert bf.vectors.shape == (64, 6)
    assert bf.grid == 8


def test_deterministic():
    ext = _ext()
    img = synthetic_ok(1, 128, seed=3)[0]
    assert np.array_equal(ext.extract(img).vectors, ext.extract(img).vectors)


def test_defect_block_stands_out():
    ext = _ext(size=128)
    clean = synthetic_ok(1, 128, seed=100)[0]
    bad = synthetic_defect(128, seed=100, kind="foreign")
    d = np.linalg.norm(ext.extract(bad).vectors - ext.extract(clean).vectors, axis=1)
    assert d.max() > 5 * (np.median(d) + 1e-9)
