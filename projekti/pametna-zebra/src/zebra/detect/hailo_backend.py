"""Детекција на Hailo-8L акцелератору (AI HAT+).

Захтева `hailo-all` пакет и HEF модел (YOLOv8n) — види
`edgeai/web` упутство „AI HAT+ (Hailo-8L)". Ако Hailo окружење није доступно,
намерно пада на YOLO backend да радионица не стане.
"""

from __future__ import annotations

import logging

from zebra.detect.base import Detection, Detector

log = logging.getLogger(__name__)


class HailoDetector(Detector):
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        try:
            self._impl = _RealHailo(cfg)
            self._fallback = None
            log.info("Hailo-8L детектор спреман.")
        except Exception as exc:  # noqa: BLE001
            log.warning("Hailo није доступан (%s) — падам на YOLO backend.", exc)
            from zebra.detect.yolo_backend import YoloDetector

            self._impl = None
            self._fallback = YoloDetector(cfg)

    def detect(self, frame) -> list[Detection]:
        if self._impl is not None:
            return self._impl.detect(frame)
        return self._fallback.detect(frame)

    def close(self) -> None:
        if self._impl is not None:
            self._impl.close()
        elif self._fallback is not None:
            self._fallback.close()


class _RealHailo:
    """Танак омотач око hailo_platform / DeGirum рантајма.

    Оставено као место за попуну на радионици: учитати HEF, покренути инференцу,
    декодовати YOLOv8 излаз у листу `Detection`. Док није попуњено, конструктор
    подиже изузетак па `HailoDetector` користи YOLO.
    """

    def __init__(self, cfg) -> None:  # pragma: no cover - хардвер
        import hailo_platform  # noqa: F401  (подиже ImportError ако нема SDK)

        raise NotImplementedError(
            "Попуни _RealHailo: учитавање HEF модела и декодовање излаза. "
            "Видети примере у /usr/share/rpi-camera-assets и hailo-apps."
        )

    def detect(self, frame):  # pragma: no cover - хардвер
        raise NotImplementedError

    def close(self):  # pragma: no cover
        pass
