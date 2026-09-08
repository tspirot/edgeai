"""Лажни сензор климе — детерминистичке вредности са благим дневним колебањем."""

from __future__ import annotations

import math

from cuvar.climate.base import ClimateReading, ClimateSensor


class DummySensor(ClimateSensor):
    def __init__(self, cfg=None) -> None:
        self._t = 0.0

    def read(self) -> ClimateReading:
        self._t += 1.0
        phase = self._t / 50.0
        temp = 12.0 + 6.0 * math.sin(phase)
        humidity = 55.0 + 15.0 * math.cos(phase / 2)
        pressure = 1013.0 + 3.0 * math.sin(phase / 3)
        gas = 120_000.0 - 20_000.0 * math.sin(phase)
        aqi = max(0.0, min(100.0, 30.0 + 20.0 * math.sin(phase)))
        return ClimateReading(temp, humidity, pressure, gas, aqi)
