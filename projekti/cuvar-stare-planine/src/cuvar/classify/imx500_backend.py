"""Класификација на самом IMX500 сензору (модел се извршава на чипу камере).

Захтева `imx500-all` и `.rpk` модел (види упутство „Raspberry Pi AI Camera").
Ако окружење није доступно, пада на ONNX на процесору ако постоји модел,
иначе на dummy — да радионица не стане.
"""

from __future__ import annotations

import logging

from cuvar.classify.base import Classifier, Prediction

log = logging.getLogger(__name__)


class IMX500Classifier(Classifier):
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        try:  # pragma: no cover - хардвер
            from picamera2.devices import IMX500  # noqa: F401

            raise NotImplementedError(
                "Попуни IMX500Classifier: учитавање .rpk модела и читање излаза "
                "класификатора са сензора (picamera2.devices.IMX500)."
            )
        except Exception as exc:  # noqa: BLE001
            log.warning("IMX500 није доступан (%s) — пробам ONNX/dummy.", exc)
            self._fallback = _fallback(cfg)

    def classify(self, frame) -> "Prediction | None":
        return self._fallback.classify(frame)

    def close(self) -> None:
        self._fallback.close()


def _fallback(cfg) -> Classifier:
    import os

    if getattr(cfg, "model", "").endswith(".onnx") and os.path.exists(cfg.model):
        from cuvar.classify.onnx_backend import OnnxClassifier

        return OnnxClassifier(cfg)
    from cuvar.classify.dummy_backend import DummyClassifier

    return DummyClassifier(cfg)
