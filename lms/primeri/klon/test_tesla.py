import cv2
import mediapipe as mp
import os

path = os.path.join(os.path.dirname(__file__), "tesla.jpg")
print("Reading:", path)
img = cv2.imread(path)
if img is None:
    print("Failed to read image")
    exit(1)

h, w = img.shape[:2]
s = min(h, w)
crop = img[:s, :s]
crop = cv2.resize(crop, (480, 480))

mp_fm = mp.solutions.face_mesh
fm = mp_fm.FaceMesh(static_image_mode=True, max_num_faces=1)
res = fm.process(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
if res.multi_face_landmarks:
    print("SUCCESS: Tesla face detected! Landmarks count:", len(res.multi_face_landmarks[0].landmark))
else:
    print("Face not detected on image")
