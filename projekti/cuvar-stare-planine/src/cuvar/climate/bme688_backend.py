"""BME688 преко I²C (библиотека `bme680` ради и за BME688 основна мерења).

Гас у ому → упрошћен AQI: чист ваздух има високу отпорност, загађен ниску.
Калибрација базне линије на радионици (`baseline_ohm`).
"""

from __future__ import annotations

import logging

from cuvar.climate.base import ClimateReading, ClimateSensor

log = logging.getLogger(__name__)


class Bme688Sensor(ClimateSensor):
    def __init__(self, cfg, baseline_ohm: float = 120_000.0) -> None:
        import bme680  # noqa: F401  (подиже ImportError ако нема библиотеке/сензора)

        self._bme680 = bme680
        self.sensor = bme680.BME680(cfg.i2c_address)
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
        self.sensor.set_gas_heater_temperature(320)
        self.sensor.set_gas_heater_duration(150)
        self.sensor.select_gas_heater_profile(0)
        self.baseline_ohm = baseline_ohm

    def read(self) -> ClimateReading:
        if not self.sensor.get_sensor_data():
            raise RuntimeError("BME688: подаци нису спремни")
        d = self.sensor.data
        gas = float(getattr(d, "gas_resistance", 0.0) or 0.0)
        aqi = _aqi(gas, self.baseline_ohm)
        return ClimateReading(
            temp_c=float(d.temperature),
            humidity=float(d.humidity),
            pressure_hpa=float(d.pressure),
            gas_ohm=gas,
            aqi=aqi,
        )


def _aqi(gas_ohm: float, baseline_ohm: float) -> float:
    if gas_ohm <= 0:
        return 50.0
    ratio = gas_ohm / baseline_ohm
    return float(max(0.0, min(100.0, 100.0 * (1.0 - min(1.0, ratio)))))
