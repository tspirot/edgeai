"""Подсетник: LED/зујалица на GPIO, или испис у терминал."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class Feedback:
    def remind(self) -> None:
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        pass


class NullFeedback(Feedback):
    def remind(self) -> None:
        pass


class ConsoleFeedback(Feedback):
    def __init__(self, cfg=None) -> None:
        self.count = 0

    def remind(self) -> None:
        self.count += 1
        print("🔔 Исправи се — седиш погрбљено дуже време.")


class GpioFeedback(Feedback):  # pragma: no cover - тражи хардвер
    def __init__(self, cfg) -> None:
        from gpiozero import LED, Buzzer

        self.cfg = cfg
        self._led = LED(cfg.led_pin)
        self._buzzer = Buzzer(cfg.buzzer_pin) if cfg.buzzer else None

    def remind(self) -> None:
        self._led.blink(on_time=0.4, off_time=0.4, n=int(self.cfg.blink_s / 0.8), background=True)
        if self._buzzer is not None:
            self._buzzer.beep(on_time=0.1, off_time=0.1, n=2, background=True)

    def close(self) -> None:
        self._led.off()


def build_feedback(cfg) -> Feedback:
    backend = (cfg.backend or "auto").lower()
    if backend == "none":
        return NullFeedback()
    if backend == "console":
        return ConsoleFeedback(cfg)
    if backend in ("auto", "gpio"):
        try:
            return GpioFeedback(cfg)
        except Exception as exc:  # pragma: no cover
            if backend == "gpio":
                raise
            log.warning("GPIO недоступан (%s) — подсетник у терминалу", exc)
            return ConsoleFeedback(cfg)
    raise ValueError(f"Непознат feedback backend: '{cfg.backend}'")
