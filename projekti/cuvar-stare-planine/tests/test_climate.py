from cuvar.climate.base import ClimateReading
from cuvar.climate.bme688_backend import _aqi
from cuvar.climate.dummy_backend import DummySensor


def test_dummy_sensor_in_plausible_range():
    s = DummySensor()
    for _ in range(20):
        r = s.read()
        assert isinstance(r, ClimateReading)
        assert 0 <= r.temp_c <= 40
        assert 0 <= r.humidity <= 100
        assert 900 <= r.pressure_hpa <= 1100
        assert 0 <= r.aqi <= 100


def test_reading_as_dict_rounds():
    r = ClimateReading(11.23456, 55.5, 1013.0, 120000.0, 30.0)
    d = r.as_dict()
    assert d["temp_c"] == 11.23


def test_aqi_clean_vs_polluted():
    assert _aqi(gas_ohm=120_000, baseline_ohm=120_000) < 5      # чист
    assert _aqi(gas_ohm=20_000, baseline_ohm=120_000) > 70      # загађен
