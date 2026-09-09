"""Читање гејмпада за ручну вожњу (снимање података). `evdev` се увози лениво."""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class Gamepad:
    def read(self) -> "tuple[float, float]":
        """(steer, throttle) у [−1, 1]."""
        raise NotImplementedError  # pragma: no cover

    def close(self) -> None:
        pass


class DummyGamepad(Gamepad):
    """Синусно вијуга — да `record` ради без џојстика (нпр. са DummyCamera)."""

    def __init__(self) -> None:
        self._t = 0

    def read(self):
        import math

        self._t += 1
        return 0.25 * math.sin(self._t / 25.0), 0.3


class EvdevGamepad(Gamepad):  # pragma: no cover - тражи хардвер
    def __init__(self, steer_axis: str = "ABS_X", throttle_axis: str = "ABS_RZ") -> None:
        from evdev import InputDevice, ecodes, list_devices

        self._ec = ecodes
        dev = None
        for path in list_devices():
            d = InputDevice(path)
            if ecodes.EV_ABS in d.capabilities():
                dev = d
                break
        if dev is None:
            raise RuntimeError("Гејмпад није пронађен")
        self._dev = dev
        self._steer_code = getattr(ecodes, steer_axis)
        self._throttle_code = getattr(ecodes, throttle_axis)
        self._steer = 0.0
        self._throttle = 0.0

    def read(self):
        try:
            for ev in self._dev.read():
                if ev.type != self._ec.EV_ABS:
                    continue
                info = self._dev.absinfo(ev.code)
                span = (info.max - info.min) / 2.0 or 1.0
                norm = (ev.value - info.min) / span - 1.0
                if ev.code == self._steer_code:
                    self._steer = norm
                elif ev.code == self._throttle_code:
                    self._throttle = max(0.0, norm)
        except BlockingIOError:
            pass
        return self._steer, self._throttle


def build_gamepad(backend: str = "auto") -> Gamepad:
    backend = (backend or "auto").lower()
    if backend == "dummy":
        return DummyGamepad()
    if backend in ("auto", "evdev"):
        try:
            return EvdevGamepad()
        except Exception as exc:  # pragma: no cover
            if backend == "evdev":
                raise
            log.warning("Гејмпад недоступан (%s) — DummyGamepad", exc)
            return DummyGamepad()
    raise ValueError(f"Непознат gamepad backend: '{backend}'")
