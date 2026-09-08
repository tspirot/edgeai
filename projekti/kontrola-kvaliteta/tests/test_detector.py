import numpy as np

from qc.app import evaluate, train
from qc.config import Config
from qc.data import synthetic_defect, synthetic_ok
from qc.detect import AnomalyDetector


def _cfg():
    cfg = Config()
    cfg.features.image_size = 128
    cfg.features.grid = 8
    cfg.threshold.sigma_k = 4.0
    return cfg


def test_flags_defects_not_ok():
    cfg = _cfg()
    det = train(cfg, synthetic_ok(30, 128, seed=0), synthetic_ok(10, 128, seed=500))

    defects = [synthetic_defect(128, seed=100 + i, kind=k)
               for i, k in enumerate(["hole", "foreign", "smudge", "hole", "foreign", "smudge"])]
    clean = synthetic_ok(12, 128, seed=900)
    res = evaluate(det, clean, defects)

    assert res.true_pos >= 5          # бар 5/6 мана нађено
    assert res.false_pos <= 1         # највише 1 лажни аларм


def test_heatmap_localizes_defect():
    cfg = _cfg()
    det = train(cfg, synthetic_ok(25, 128, seed=0))
    r = det.predict(synthetic_defect(128, seed=100, kind="hole"))
    assert r.is_anomaly
    assert r.heatmap.shape == (8, 8)
    # блок са највећим резултатом је баш тамо где је мана (не по ивицама свуда)
    assert r.heatmap.max() > 3 * np.median(r.heatmap)


def test_save_load(tmp_path):
    cfg = _cfg()
    det = train(cfg, synthetic_ok(20, 128, seed=0))
    path = str(tmp_path / "m.npz")
    det.save(path)
    det2 = AnomalyDetector.load(path, cfg)

    bad = synthetic_defect(128, seed=101, kind="foreign")
    assert det.predict(bad).is_anomaly == det2.predict(bad).is_anomaly
    assert abs(det.predict(bad).score - det2.predict(bad).score) < 1e-4
