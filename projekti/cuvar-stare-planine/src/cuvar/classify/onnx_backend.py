"""Класификатор преко ONNX Runtime-а (CPU) — за развој и радионицу без сензора.

Очекује стандардни класификациони модел (нпр. MobileNet fine-tune на врстама):
улаз NCHW float32 224×224, излаз логити по класама из `cfg.labels`.
"""

from __future__ import annotations

import numpy as np

from cuvar.classify.base import Classifier, Prediction


class OnnxClassifier(Classifier):
    def __init__(self, cfg) -> None:
        import onnxruntime as ort

        self.cfg = cfg
        self.labels = list(cfg.labels)
        self.session = ort.InferenceSession(cfg.model, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name

    def classify(self, frame) -> "Prediction | None":
        x = self._preprocess(frame)
        logits = self.session.run(None, {self.input_name: x})[0][0]
        probs = _softmax(logits)
        idx = int(np.argmax(probs))
        score = float(probs[idx])
        if idx >= len(self.labels) or score < self.cfg.min_score:
            return None
        return Prediction(self.labels[idx], score)

    @staticmethod
    def _preprocess(frame) -> np.ndarray:
        import cv2

        img = cv2.resize(np.asarray(frame), (224, 224)).astype(np.float32) / 255.0
        img = (img - 0.5) / 0.5
        return img.transpose(2, 0, 1)[None, ...]


def _softmax(v: np.ndarray) -> np.ndarray:
    e = np.exp(v - np.max(v))
    return e / e.sum()
