from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class ClimateReading:
    temp_c: float
    humidity: float
    pressure_hpa: float
    gas_ohm: float
    aqi: float  # 0–100, веће = гори ваздух (упрошћено)

    def as_dict(self) -> dict:
        return {k: round(v, 2) for k, v in asdict(self).items()}


class ClimateSensor:
    def read(self) -> ClimateReading:  # pragma: no cover - интерфејс
        raise NotImplementedError

    def close(self) -> None:
        pass
