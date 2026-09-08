"""YOLOv8n преко Ultralytics-а — ради на процесору (fallback) или GPU/Hailo export-у.

На Raspberry Pi 5 без акцелератора је спорије али употребљиво за учење. На
радионици се пореди са Hailo backend-ом (`--backend hailo`).
"""

from __future__ import annotations

import logging

from zebra.detect.base import Detection, Detector

log = logging.getLogger(__name__)


class YoloDetector(Detector):
    def __init__(self, cfg) -> None:
        from ultralytics import YOLO

        self.cfg = cfg
        self.person = set(cfg.person_labels)
        self.vehicle = set(cfg.vehicle_labels)
        log.info("Учитавам YOLO модел '%s'…", cfg.model)
        self.model = YOLO(cfg.model)

    def detect(self, frame) -> list[Detection]:
        results = self.model.predict(frame, conf=self.cfg.conf_low, verbose=False)
        out: list[Detection] = []
        for res in results:
            names = res.names
            for box in res.boxes:
                label = names[int(box.cls)]
                if label in self.person:
                    kind = "person"
                elif label in self.vehicle:
                    kind = "vehicle"
                else:
                    continue
                x1, y1, x2, y2 = (float(v) for v in box.xyxy[0])
                out.append(Detection(x1, y1, x2, y2, float(box.conf), kind))
        return out
