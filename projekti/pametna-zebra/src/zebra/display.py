"""Опциони преглед (OpenCV): зоне, оквири са ID-јем, банер упозорења, бројачи.

За Demo Day. За рад „на слепо" (без екрана) се не користи.
"""

from __future__ import annotations


class Display:
    def __init__(self, cfg) -> None:
        import cv2

        self.cv2 = cv2
        self.w = cfg.video.width
        self.h = cfg.video.height
        self.window = "Паметна зебра"
        cv2.namedWindow(self.window, cv2.WINDOW_NORMAL)

    def render(self, frame, tracks, state, counter, scene) -> bool:
        cv2 = self.cv2
        if frame is None:
            import numpy as np

            frame = np.full((self.h, self.w, 3), 18, dtype="uint8")
        else:
            frame = frame.copy()

        for poly, color in ((scene.crosswalk, (90, 200, 120)), (scene.roadway, (200, 170, 60))):
            if poly and len(poly.points) >= 3:
                import numpy as np

                pts = np.array(poly.points, dtype="int32").reshape(-1, 1, 2)
                cv2.polylines(frame, [pts], True, color, 2)

        for tr in tracks:
            x1, y1, x2, y2 = (int(v) for v in tr.bbox)
            color = (80, 160, 255) if tr.kind == "person" else (60, 200, 200)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{tr.kind[:1].upper()}{tr.id}", (x1, max(14, y1 - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        label = f"pesaci {counter.total.get('person', 0)}   vozila {counter.total.get('vehicle', 0)}"
        cv2.putText(frame, label, (16, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (240, 240, 240), 2, cv2.LINE_AA)

        if state.active:
            cv2.rectangle(frame, (0, 0), (frame.shape[1], 8), (0, 0, 230), -1)
            cv2.putText(frame, "! UPOZORENJE", (16, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 230), 3, cv2.LINE_AA)

        cv2.imshow(self.window, frame)
        key = cv2.waitKey(1) & 0xFF
        return key not in (ord("q"), 27)

    def close(self) -> None:
        self.cv2.destroyAllWindows()
