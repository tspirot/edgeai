"""PWM управљање за право возило (дели се са пројектом „Ђак за воланом“)."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class DummyActuator:
    def __init__(self) -> None:
        self.commands: list = []

    def drive(self, steer: float, speed: float) -> None:
        self.commands.append((round(steer, 3), round(speed, 3)))


class Pca9685Actuator:  # pragma: no cover - тражи хардвер
    def __init__(self, cfg=None, steer_channel=0, throttle_channel=1) -> None:
        import board
        import busio
        from adafruit_pca9685 import PCA9685

        self._pca = PCA9685(busio.I2C(board.SCL, board.SDA))
        self._pca.frequency = 60
        self._sc = steer_channel
        self._tc = throttle_channel

    def _us(self, channel, us):
        duty = int(us / (1_000_000 / self._pca.frequency) * 0xFFFF)
        self._pca.channels[channel].duty_cycle = max(0, min(0xFFFF, duty))

    def drive(self, steer: float, speed: float) -> None:
        self._us(self._sc, 1500 + 500 * max(-1.0, min(1.0, steer / 0.5)))
        self._us(self._tc, 1500 + 400 * max(0.0, min(1.0, speed)))


def build_actuator(backend: str = "auto"):
    backend = (backend or "auto").lower()
    if backend == "dummy":
        return DummyActuator()
    try:  # pragma: no cover
        return Pca9685Actuator()
    except Exception as exc:  # pragma: no cover
        if backend == "pca9685":
            raise
        log.warning("PCA9685 недоступан (%s) — DummyActuator", exc)
        return DummyActuator()
