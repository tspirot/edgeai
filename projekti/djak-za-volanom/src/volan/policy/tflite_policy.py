"""TFLite политика — истренирани CNN на Raspberry Pi-ју.

Покушава `tflite_runtime` (лаган), па `tensorflow.lite` као резерву.
"""

from __future__ import annotations

import logging

import numpy as np

from volan.policy.base import Policy, preprocess

log = logging.getLogger(__name__)


def _load_interpreter(path: str):
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:  # pragma: no cover
        from tensorflow.lite import Interpreter
    interp = Interpreter(model_path=path)
    interp.allocate_tensors()
    return interp


class TflitePolicy(Policy):
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._interp = _load_interpreter(cfg.path)
        self._in = self._interp.get_input_details()[0]
        self._out = [d["index"] for d in self._interp.get_output_details()]
        log.info("Учитан модел %s", cfg.path)

    def predict(self, image: np.ndarray) -> "tuple[float, float]":
        x = preprocess(image, self.cfg.input_width, self.cfg.input_height)
        if self._in["dtype"] == np.uint8:  # pragma: no cover - квантизован улаз
            scale, zero = self._in["quantization"]
            x = (x / scale + zero).astype(np.uint8) if scale else x.astype(np.uint8)
        self._interp.set_tensor(self._in["index"], x)
        self._interp.invoke()
        outs = [float(np.asarray(self._interp.get_tensor(i)).reshape(-1)[0]) for i in self._out]

        steer = outs[0]
        throttle = outs[1] if (self.cfg.predicts_throttle and len(outs) > 1) else self.cfg.cruise_throttle
        return float(np.clip(steer, -1.0, 1.0)), float(np.clip(throttle, 0.0, 1.0))
