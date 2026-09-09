"""Управљање серво воланом и ESC-ом преко PCA9685. Лажни драјвер бележи команде."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class Actuator:
    def drive(self, steer: float, throttle: float) -> None:
        """steer ∈ [−1, 1], throttle ∈ [−1, 1] (негативно = рикверц/кочница)."""
        raise NotImplementedError  # pragma: no cover

    def stop(self) -> None:
        self.drive(0.0, 0.0)

    def close(self) -> None:
        self.stop()


class DummyActuator(Actuator):
    def __init__(self, cfg=None) -> None:
        self.commands: list = []

    def drive(self, steer: float, throttle: float) -> None:
        self.commands.append((round(steer, 3), round(throttle, 3)))


class Pca9685Actuator(Actuator):  # pragma: no cover - тражи хардвер
    def __init__(self, cfg) -> None:
        import board
        import busio
        from adafruit_pca9685 import PCA9685

        self.cfg = cfg
        self._pca = PCA9685(busio.I2C(board.SCL, board.SDA))
        self._pca.frequency = 60

    def _set_us(self, channel: int, us: float) -> None:
        duty = int(us / (1_000_000 / self._pca.frequency) * 0xFFFF)
        self._pca.channels[channel].duty_cycle = max(0, min(0xFFFF, duty))

    def drive(self, steer: float, throttle: float) -> None:
        c = self.cfg
        steer = max(-1.0, min(1.0, steer))
        if steer <= 0:
            us = _lerp(c.steer_center_us, c.steer_left_us, -steer)
        else:
            us = _lerp(c.steer_center_us, c.steer_right_us, steer)
        self._set_us(c.steer_channel, us)

        throttle = max(-1.0, min(1.0, throttle))
        if throttle >= 0:
            tu = _lerp(c.throttle_stop_us, c.throttle_full_us, throttle)
        else:
            tu = _lerp(c.throttle_stop_us, c.throttle_reverse_us, -throttle)
        self._set_us(c.throttle_channel, tu)


def build_actuator(cfg) -> Actuator:
    backend = (cfg.backend or "auto").lower()
    if backend == "dummy":
        return DummyActuator(cfg)
    if backend in ("auto", "pca9685"):
        try:
            return Pca9685Actuator(cfg)
        except Exception as exc:  # pragma: no cover
            if backend == "pca9685":
                raise
            log.warning("PCA9685 недоступан (%s) — DummyActuator", exc)
            return DummyActuator(cfg)
    raise ValueError(f"Непознат actuator backend: '{cfg.backend}'")
