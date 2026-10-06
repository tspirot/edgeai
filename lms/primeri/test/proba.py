import os
import time
import cv2
import numpy as np

# Postavljanje prikaza na lokalni HDMI ekran (TV) kada se pokrece preko SSH
os.environ["DISPLAY"] = ":0"
os.environ["WAYLAND_DISPLAY"] = "wayland-0"

# Provera MediaPipe biblioteke
try:
    import mediapipe as mp
except ImportError:
    print("\n[GRESKA] 'mediapipe' nije instaliran!")
    print("Pokreni: pip install mediapipe==0.10.14\n")
    exit(1)

# Inicijalizacija MediaPipe Hands modula
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Inicijalizacija Raspberry Pi Camera Module 3 (IMX708 NoIR) preko Picamera2
use_picam2 = False
picam2 = None
cap = None

try:
    from picamera2 import Picamera2
    print("[INFO] Pokrecem kameru preko nativnog Picamera2 drajvera (IMX708)...")
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    use_picam2 = True
    print("[INFO] Camera Module 3 je uspesno aktiviran (prirodne boje)!")
except Exception as e:
    print(f"[INFO] Picamera2 nije ucitana ({e}), pokusavam OpenCV VideoCapture...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not use_picam2 and (cap is None or not cap.isOpened()):
    print("\n[GRESKA] Kamera nije pronadjena! Pokreni skriptu sa: libcamerify python proba.py")
    exit(1)

finger_tips = [4, 8, 12, 16, 20]
prev_time = 0

noir_correction = False    # Moze se ukljuciti na 'n' po potrebi
saturation_boost = 1.0     # Zasicenost (moze se menjati na '+' i '-')

print("=" * 60)
print("Aplikacija pokrenuta sa podesenim tacnim prirodnim bojama!")
print("Kontrole: [n] NoIR filter | [+/-] Zasicenost | [q] Izlaz")
print("=" * 60)

def apply_noir_balance(img):
    img_float = img.astype(np.float32)
    img_float[:, :, 2] = img_float[:, :, 2] * 0.82
    img_float[:, :, 0] = img_float[:, :, 0] * 0.90
    img_float[:, :, 1] = np.clip(img_float[:, :, 1] * 1.08, 0, 255)
    return np.clip(img_float, 0, 255).astype(np.uint8)

def adjust_saturation(img, scale):
    if scale == 1.0:
        return img
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * scale, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

while True:
    if use_picam2:
        raw_frame = picam2.capture_array()
        frame = cv2.flip(raw_frame, 1)
    else:
        success, raw_frame = cap.read()
        if not success:
            print("[UPOZORENJE] Nije moguce ocitati sliku sa kamere.")
            break
        frame = cv2.flip(raw_frame, 1)

    if noir_correction:
        frame = apply_noir_balance(frame)

    if saturation_boost != 1.0:
        frame = adjust_saturation(frame, saturation_boost)

    h, w, c = frame.shape
    # Za MediaPipe uvek obezbedjujemo RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    total_fingers = 0
    hands_keypoints = []

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

            lm_list = hand_landmarks.landmark
            thumb_pt = (int(lm_list[4].x * w), int(lm_list[4].y * h))
            index_pt = (int(lm_list[8].x * w), int(lm_list[8].y * h))
            hands_keypoints.append((thumb_pt, index_pt))

            cv2.circle(frame, thumb_pt, 7, (0, 165, 255), -1)
            cv2.circle(frame, index_pt, 7, (255, 0, 255), -1)
            cv2.line(frame, thumb_pt, index_pt, (255, 255, 255), 2)

            handedness = "Hand"
            if results.multi_handedness and idx < len(results.multi_handedness):
                handedness = results.multi_handedness[idx].classification[0].label

            fingers_up = []
            if handedness == "Right":
                fingers_up.append(1 if lm_list[4].x < lm_list[3].x else 0)
            else:
                fingers_up.append(1 if lm_list[4].x > lm_list[3].x else 0)

            for tip in finger_tips[1:]:
                fingers_up.append(1 if lm_list[tip].y < lm_list[tip - 2].y else 0)

            hand_finger_count = sum(fingers_up)
            total_fingers += hand_finger_count

            wrist_x = int(lm_list[0].x * w)
            wrist_y = int(lm_list[0].y * h)
            cv2.putText(
                frame,
                f"{handedness}: {hand_finger_count}",
                (wrist_x - 40, wrist_y - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

        # Crtanje pravougaonika izmedju dve ruke
        if len(hands_keypoints) >= 2:
            h1_thumb, h1_index = hands_keypoints[0]
            h2_thumb, h2_index = hands_keypoints[1]

            all_x = [h1_thumb[0], h1_index[0], h2_thumb[0], h2_index[0]]
            all_y = [h1_thumb[1], h1_index[1], h2_thumb[1], h2_index[1]]

            x_min, x_max = min(all_x), max(all_x)
            y_min, y_max = min(all_y), max(all_y)

            overlay = frame.copy()
            cv2.rectangle(overlay, (x_min, y_min), (x_max, y_max), (0, 255, 255), -1)
            cv2.addWeighted(overlay, 0.22, frame, 0.78, 0, frame)

            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 255), 3)

            line_len = min(25, (x_max - x_min) // 4, (y_max - y_min) // 4)
            if line_len > 5:
                cv2.line(frame, (x_min, y_min), (x_min + line_len, y_min), (0, 255, 0), 4)
                cv2.line(frame, (x_min, y_min), (x_min, y_min + line_len), (0, 255, 0), 4)
                cv2.line(frame, (x_max, y_min), (x_max - line_len, y_min), (0, 255, 0), 4)
                cv2.line(frame, (x_max, y_min), (x_max, y_min + line_len), (0, 255, 0), 4)
                cv2.line(frame, (x_min, y_max), (x_min + line_len, y_max), (0, 255, 0), 4)
                cv2.line(frame, (x_min, y_max), (x_min, y_max - line_len), (0, 255, 0), 4)
                cv2.line(frame, (x_max, y_max), (x_max - line_len, y_max), (0, 255, 0), 4)
                cv2.line(frame, (x_max, y_max), (x_max, y_max - line_len), (0, 255, 0), 4)

            rect_w = x_max - x_min
            rect_h = y_max - y_min
            cv2.putText(
                frame,
                f"Pravougaonik: {rect_w}x{rect_h} px",
                (x_min, max(30, y_min - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, f"Prstiju: {total_fingers}", (10, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Prepoznavanje Ruku i Pravougaonik - RPi 5", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == ord('n'):
        noir_correction = not noir_correction
    elif key == ord('+') or key == ord('='):
        saturation_boost = min(2.5, saturation_boost + 0.1)
    elif key == ord('-'):
        saturation_boost = max(0.5, saturation_boost - 0.1)

if use_picam2:
    picam2.stop()
else:
    cap.release()

cv2.destroyAllWindows()
