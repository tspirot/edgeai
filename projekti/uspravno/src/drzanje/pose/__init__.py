"""Избор детектора позе према конфигурацији."""

from __future__ import annotations

import logging

from drzanje.pose.base import PoseBackend

log = logging.getLogger(__name__)

__all__ = ["PoseBackend", "build_pose"]


def build_pose(pose_cfg, fps: int = 15) -> PoseBackend:
    backend = (pose_cfg.backend or "auto").lower()

    if backend == "dummy":
        from drzanje.pose.synthetic import SyntheticPose

        return SyntheticPose(pose_cfg, fps=fps)

    if backend in ("auto", "mediapipe"):
        try:
            from drzanje.pose.mediapipe_backend import MediaPipePose

            return MediaPipePose(pose_cfg)
        except Exception as exc:  # pragma: no cover
            if backend == "mediapipe":
                raise
            log.warning("MediaPipe недоступан (%s) — синтетичка поза", exc)
            from drzanje.pose.synthetic import SyntheticPose

            return SyntheticPose(pose_cfg, fps=fps)

    raise ValueError(f"Непознат pose backend: '{pose_cfg.backend}'")
