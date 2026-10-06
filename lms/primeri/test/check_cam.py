from picamera2 import Picamera2
import cv2

p = Picamera2()
config = p.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
p.configure(config)
p.start()
arr = p.capture_array()
print("Captured frame shape:", arr.shape)
print("Channel means (0, 1, 2):", arr[:, :, 0].mean(), arr[:, :, 1].mean(), arr[:, :, 2].mean())
p.stop()
