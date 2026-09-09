from drzanje.logbook import log_screening, read_csv
from drzanje.screening import summarize


def test_empty_rows():
    r = summarize([], flag_deg=3.0)
    assert r["n"] == 0
    assert r["flagged"] is False


def test_symmetric_not_flagged():
    rows = [{"date": f"2026-05-{d:02d}", "shoulder_tilt": s, "hip_tilt": h}
            for d, (s, h) in enumerate([(0.5, -0.3), (-0.4, 0.6), (0.2, 0.1), (-0.1, -0.2)], 1)]
    r = summarize(rows, flag_deg=3.0)
    assert not r["flagged"]
    assert "није дијагноза" in r["note"]


def test_consistent_asymmetry_flagged():
    rows = [{"date": f"2026-05-{d:02d}", "shoulder_tilt": 5.0 + d * 0.1, "hip_tilt": 0.2}
            for d in range(1, 9)]
    r = summarize(rows, flag_deg=3.0)
    assert r["flagged"]
    assert r["shoulder"]["n_over"] >= 6
    assert "лекару" in r["note"]


def test_roundtrip_csv(tmp_path):
    p = tmp_path / "skrining.csv"
    log_screening(p, 4.1, -0.5)
    log_screening(p, 3.9, 0.2)
    rows = read_csv(p)
    assert len(rows) == 2
    assert rows[0]["shoulder_tilt"] == "4.1"
    r = summarize(rows, flag_deg=3.0)
    assert r["n"] == 2
