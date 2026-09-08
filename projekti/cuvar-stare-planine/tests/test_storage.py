import json

from cuvar.storage import EventStore


def test_records_event_and_sidecar(tmp_path):
    store = EventStore(tmp_path, save_images=False)
    ev = store.record("srna", 0.82, {"temp_c": 11.2, "aqi": 30.0})
    assert ev.species == "srna"
    assert store.species_counts == {"srna": 1}

    sidecars = list(tmp_path.glob("*.json"))
    assert len(sidecars) == 1
    data = json.loads(sidecars[0].read_text(encoding="utf-8"))
    assert data["species"] == "srna"
    assert data["climate"]["temp_c"] == 11.2


def test_species_counts_accumulate(tmp_path):
    store = EventStore(tmp_path, save_images=False)
    for sp in ["srna", "lisica", "srna", "zec", "srna"]:
        store.record(sp, 0.7, {})
    assert store.species_counts == {"srna": 3, "lisica": 1, "zec": 1}
    assert len(store.events) == 5


def test_rotation_keeps_only_recent(tmp_path):
    store = EventStore(tmp_path, keep_last=3, save_images=False)
    for i in range(8):
        store.record(f"vrsta{i}", 0.7, {})
    remaining = list(tmp_path.glob("*.json"))
    assert len(remaining) <= 3
