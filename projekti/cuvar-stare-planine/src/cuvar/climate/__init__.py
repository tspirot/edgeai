"""Мерење климе (температура, влажност, притисак, гас/AQI)."""

from __future__ import annotations

from cuvar.climate.base import ClimateReading, ClimateSensor

__all__ = ["ClimateReading", "ClimateSensor", "build_sensor"]


def build_sensor(cfg):
    backend = (cfg.backend or "").lower()
    if backend in ("bme688", "bme680"):
        from cuvar.climate.bme688_backend import Bme688Sensor

        return Bme688Sensor(cfg)
    if backend == "dummy":
        from cuvar.climate.dummy_backend import DummySensor

        return DummySensor(cfg)
    raise ValueError(f"Непознат climate backend: '{cfg.backend}'")
