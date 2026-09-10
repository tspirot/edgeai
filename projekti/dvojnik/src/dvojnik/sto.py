"""Окретни сто — једина ствар у пројекту која се помера, и најважнија.

Због њега систем **зна** угао сваког кадра уместо да га процењује. Тиме отпада
визуелна одометрија, корак који на једнобојном предмету и сјајној површини губи
траг и због ког већина школских покушаја 3D скенирања пропадне.

`dummy` сто ништа не окреће — само броји углове. С њим цео ланац ради на
обичном рачунару.
"""

from __future__ import annotations

import logging
import time

log = logging.getLogger(__name__)

# Полукорачни редослед за 28BYJ-48 преко ULN2003: осам стања, четири намотаја.
POLUKORAK = (
    (1, 0, 0, 0), (1, 1, 0, 0), (0, 1, 0, 0), (0, 1, 1, 0),
    (0, 0, 1, 0), (0, 0, 1, 1), (0, 0, 0, 1), (1, 0, 0, 1),
)


class Sto:
    """Заједнички облик: сто зна свој угао и уме да га промени."""

    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._ugao = 0.0

    @property
    def ugao(self) -> float:
        return self._ugao % 360.0

    def okreni_za(self, stepeni: float) -> float:
        raise NotImplementedError

    def uglovi(self, kadrova: int) -> list:
        """Равномерни углови пуног круга, онолико колико се снима кадрова."""
        if kadrova < 3:
            raise ValueError(
                f"{kadrova} кадрова је премало — испод три угла нема шта да се "
                "изрезбари. Обично иде 60–180."
            )
        return [360.0 * i / kadrova for i in range(int(kadrova))]

    def close(self) -> None:
        pass


class DummySto(Sto):
    """Ништа не окреће. Угао само броји — за рад без хардвера."""

    def okreni_za(self, stepeni: float) -> float:
        self._ugao += float(stepeni)
        return self.ugao


class KoracniSto(Sto):  # pragma: no cover — тражи GPIO
    """28BYJ-48 преко ULN2003 драјвера, на GPIO пиновима Jetson-а."""

    def __init__(self, cfg) -> None:
        super().__init__(cfg)
        try:
            import Jetson.GPIO as GPIO
        except ImportError:
            try:
                import RPi.GPIO as GPIO
            except ImportError as exc:
                raise RuntimeError(
                    "Нема ни Jetson.GPIO ни RPi.GPIO — `pip install -e \".[sto]\"`. "
                    "За рад без хардвера: --sto dummy"
                ) from exc

        self.GPIO = GPIO
        self.pinovi = list(cfg.pinovi)
        if len(self.pinovi) != 4:
            raise ValueError(f"ULN2003 тражи тачно четири пина, дато: {self.pinovi}")

        GPIO.setmode(GPIO.BCM)
        for pin in self.pinovi:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        self._stanje = 0
        log.info("Окретни сто на пиновима %s, %d корака по кругу",
                 self.pinovi, cfg.koraka_po_krugu)

    def _korak(self, napred: bool) -> None:
        self._stanje = (self._stanje + (1 if napred else -1)) % len(POLUKORAK)
        for pin, vrednost in zip(self.pinovi, POLUKORAK[self._stanje]):
            self.GPIO.output(pin, self.GPIO.HIGH if vrednost else self.GPIO.LOW)
        time.sleep(0.0015)          # брже од овога мотор прескаче кораке

    def okreni_za(self, stepeni: float) -> float:
        koraka = int(round(abs(stepeni) / 360.0 * self.cfg.koraka_po_krugu))
        napred = (stepeni >= 0) != bool(self.cfg.obrnut_smer)
        for _ in range(koraka):
            self._korak(napred)
        self._ugao += float(stepeni)
        # Намотаји се гасе да мотор не греје и не вибрира док камера снима.
        for pin in self.pinovi:
            self.GPIO.output(pin, self.GPIO.LOW)
        time.sleep(self.cfg.pauza_ms / 1000.0)
        return self.ugao

    def close(self) -> None:
        for pin in self.pinovi:
            self.GPIO.output(pin, self.GPIO.LOW)
        self.GPIO.cleanup(self.pinovi)


def build_sto(cfg) -> Sto:
    if cfg.backend == "dummy":
        return DummySto(cfg)
    if cfg.backend == "koracni":
        return KoracniSto(cfg)
    raise ValueError(f"Непознат сто: '{cfg.backend}' (има: koracni, dummy)")
