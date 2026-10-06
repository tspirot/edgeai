from picamera2 import Picamera2
import numpy as np
import cv2

p = Picamera2()
# Test 1: BGR888
cfg_bgr = p.create_preview_configuration(main={"size": (640, 480), "format": "BGR888"})
p.configure(cfg_bgr)
p.start()
arr_bgr = p.capture_array()
p.stop()

# Test 2: RGB888
cfg_rgb = p.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
p.configure(cfg_rgb)
p.start()
arr_rgb = p.capture_array()
p.stop()

print("BGR888 sample pixel [240, 320]:", arr_bgr[240, 320].tolist())
print("RGB888 sample pixel [240, 320]:", arr_rgb[240, 320].tolist())
