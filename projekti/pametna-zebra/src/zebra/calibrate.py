"""Калибрација зона: кликом означи темена пешачког прелаза па коловоза, сними у zones.json."""

from __future__ import annotations

import logging

from zebra.safety.zone import Polygon, Scene

log = logging.getLogger(__name__)


def calibrate(cfg, out_path: str) -> None:
    import cv2

    from zebra.video.source import open_source

    source = open_source(cfg)
    frame = None
    for f, _ in source:
        frame = f
        break
    if hasattr(source, "close"):
        source.close()
    if frame is None:
        # sim извор нема слику — направи празну подлогу
        import numpy as np

        frame = np.full((cfg.video.height, cfg.video.width, 3), 18, dtype="uint8")

    stages = ["пешачки прелаз", "коловоз"]
    collected: list[list[tuple[int, int]]] = [[], []]
    idx = 0
    window = "Калибрација — леви клик тачка, ENTER следеће, ESC крај"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    def on_mouse(event, x, y, _flags, _param):
        if event == cv2.EVENT_LBUTTONDOWN:
            collected[idx].append((x, y))

    cv2.setMouseCallback(window, on_mouse)

    while True:
        canvas = frame.copy()
        cv2.putText(canvas, f"Означи: {stages[idx]}", (16, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 230, 120), 2)
        for i, pts in enumerate(collected):
            for p in pts:
                cv2.circle(canvas, p, 4, (0, 230, 120) if i == idx else (150, 150, 150), -1)
            if len(pts) >= 2:
                import numpy as np

                cv2.polylines(canvas, [np.array(pts, "int32")], i < idx,
                              (0, 230, 120) if i == idx else (150, 150, 150), 2)
        cv2.imshow(window, canvas)
        key = cv2.waitKey(20) & 0xFF
        if key in (13, 10):  # ENTER
            if idx == 0:
                idx = 1
            else:
                break
        elif key == 27:  # ESC
            break
        elif key == ord("z") and collected[idx]:
            collected[idx].pop()

    cv2.destroyAllWindows()

    scene = Scene(
        crosswalk=Polygon([tuple(p) for p in collected[0]]) if len(collected[0]) >= 3 else None,
        roadway=Polygon([tuple(p) for p in collected[1]]) if len(collected[1]) >= 3 else None,
    )
    scene.to_file(out_path)
    log.info("Зоне сачуване у %s", out_path)
