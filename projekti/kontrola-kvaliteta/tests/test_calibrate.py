import numpy as np
import pytest

from qc.calibrate import threshold_from_ok


def test_sigma_no_variance():
    assert threshold_from_ok([1.0, 1.0, 1.0], "sigma", sigma_k=4) == 1.0


def test_sigma_with_variance():
    assert threshold_from_ok([0.0, 2.0], "sigma", sigma_k=3) == 4.0  # mean 1 + 3·1


def test_percentile():
    assert threshold_from_ok(list(np.arange(101)), "percentile", percentile=99) == 99.0


def test_empty_raises():
    with pytest.raises(ValueError):
        threshold_from_ok([])


def test_unknown_method():
    with pytest.raises(ValueError):
        threshold_from_ok([1.0], method="magic")
