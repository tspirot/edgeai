"""Светлосно упозорење преко GPIO (gpiozero). Без хардвера — тихо не ради ништа."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class WarningLight:
    def __init__(self, cfg) -> None:
        self._led = None
        self._state = False
        if not cfg.gpio:
            return
        try:
            from gpiozero import LED

            self._led = LED(cfg.led_pin)
            log.info("Упозорење: LED на GPIO %s.", cfg.led_pin)
        except Exception as exc:  # noqa: BLE001
            log.warning("GPIO недоступан (%s) — упозорење само на екрану/у логу.", exc)

    def set(self, on: bool) -> None:
        if on == self._state:
            return
        self._state = on
        if self._led is not None:
            (self._led.on if on else self._led.off)()

    @property
    def state(self) -> bool:
        return self._state

    def close(self) -> None:
        self.set(False)
        if self._led is not None:
            self._led.close()
