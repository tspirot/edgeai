"""Обука малог CNN-а из снимака и извоз у TensorFlow Lite.

Тражи `pip install -e ".[train]"` (TensorFlow). Покреће се на рачунару, не на
Pi-ју. Резултат `pilot.tflite` иде у `models/` на аутомобилу.
"""

from __future__ import annotations

import logging

import numpy as np

from volan.recorder import read_tub

log = logging.getLogger(__name__)


def build_model(width: int, height: int, outputs: int = 1):
    from tensorflow import keras
    from tensorflow.keras import layers

    return keras.Sequential([
        layers.Input((height, width, 3)),
        layers.Conv2D(24, 5, strides=2, activation="relu"),
        layers.Conv2D(32, 5, strides=2, activation="relu"),
        layers.Conv2D(48, 3, strides=2, activation="relu"),
        layers.Conv2D(64, 3, activation="relu"),
        layers.Flatten(),
        layers.Dropout(0.2),
        layers.Dense(64, activation="relu"),
        layers.Dense(outputs),
    ])


def _resize(images: np.ndarray, width: int, height: int) -> np.ndarray:
    n, h, w = images.shape[:3]
    if (w, h) == (width, height):
        out = images
    else:
        yi = np.linspace(0, h - 1, height).astype(np.int64)
        xi = np.linspace(0, w - 1, width).astype(np.int64)
        out = images[:, yi][:, :, xi]
    return out.astype(np.float32) / 255.0


def train(data_dir: str, out_path: str, width: int, height: int,
          predicts_throttle: bool = False, epochs: int = 20) -> str:
    import tensorflow as tf

    X, y = read_tub(data_dir)
    log.info("Учитано %d кадрова из %s", len(X), data_dir)
    X = _resize(X, width, height)
    y = y if predicts_throttle else y[:, :1]

    model = build_model(width, height, outputs=y.shape[1])
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    model.fit(X, y, validation_split=0.15, epochs=epochs, batch_size=64, verbose=2)

    conv = tf.lite.TFLiteConverter.from_keras_model(model)
    conv.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite = conv.convert()

    from pathlib import Path

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_bytes(tflite)
    log.info("Сачувано %s (%d kB)", out_path, len(tflite) // 1024)
    return out_path
