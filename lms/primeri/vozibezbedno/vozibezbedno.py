import os
import time
import math
from collections import deque
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

# Inicijalizacija MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Inicijalizacija kamere (Picamera2 za RPi 5 sa fallback-om)
use_picam2 = False
picam2 = None
cap = None

try:
    from picamera2 import Picamera2
    print("[INFO] Pokrecem kameru preko Picamera2 (IMX708)...")
    picam2 = Picamera2()
    # RGB888 konfiguracija u Picamera2 daje tačan BGR raspored u OpenCV memoriji
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    use_picam2 = True
    print("[INFO] Picamera2 uspešno pokrenuta sa prirodnim bojama!")
except Exception as e:
    print(f"[INFO] Picamera2 nije ucitana ({e}), pokusavam OpenCV VideoCapture...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not use_picam2 and (cap is None or not cap.isOpened()):
    print("[GRESKA] Kamera nije pronadjena! Pokreni skriptu sa: libcamerify python lice.py")
    exit(1)

# Indeksi tacaka na licu (MediaPipe Face Mesh 468 landmarks)
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]
LIPS_CONTOUR = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 78]

# 3D model lica za odredjivanje orijentacije glave (Head Pose)
MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),          # Vrh nosa (1)
    (0.0, -330.0, -65.0),     # Brada (152)
    (-225.0, 170.0, -135.0),  # Levi ugao levog oka (263)
    (225.0, 170.0, -135.0),   # Desni ugao desnog oka (33)
    (-150.0, -150.0, -125.0), # Levi ugao usta (291)
    (150.0, -150.0, -125.0)   # Desni ugao usta (61)
], dtype=np.float64)

# Pragovi za detekciju umora
EAR_THRESHOLD = 0.22        # Ispod ovoga se smatra da su oci zatvorene
MAR_THRESHOLD = 0.55        # Iznad ovoga se smatra da vozac zeva
EYES_CLOSED_ALERT_SEC = 1.3 # Vreme zazmurenih ociju pre alarma

# Istorija podataka za talasni grafikon (Waveform)
HISTORY_LEN = 90
ear_history = deque([0.3] * HISTORY_LEN, maxlen=HISTORY_LEN)
mar_history = deque([0.1] * HISTORY_LEN, maxlen=HISTORY_LEN)
perclos_window = deque([0] * 150, maxlen=150)

eyes_closed_start_time = None
closed_duration = 0.0
prev_time = 0

def calc_ear(landmarks, eye_indices, w, h):
    """Racuna Eye Aspect Ratio (EAR) - stepen otvorenosti oka"""
    pts = [np.array([landmarks[i].x * w, landmarks[i].y * h]) for i in eye_indices]
    d_v1 = np.linalg.norm(pts[1] - pts[5])
    d_v2 = np.linalg.norm(pts[2] - pts[4])
    d_h = np.linalg.norm(pts[0] - pts[3])
    if d_h < 1e-5:
        return 0.3
    return (d_v1 + d_v2) / (2.0 * d_h)

def calc_mar(landmarks, w, h):
    """Racuna Mouth Aspect Ratio (MAR) - detekcija zevanja"""
    p_left = np.array([landmarks[61].x * w, landmarks[61].y * h])
    p_right = np.array([landmarks[291].x * w, landmarks[291].y * h])
    p_top = np.array([landmarks[13].x * w, landmarks[13].y * h])
    p_bottom = np.array([landmarks[14].x * w, landmarks[14].y * h])
    
    d_v = np.linalg.norm(p_top - p_bottom)
    d_h = np.linalg.norm(p_left - p_right)
    if d_h < 1e-5:
        return 0.1
    return d_v / d_h

def estimate_head_pose(landmarks, w, h):
    """Procena nagiba i rotacije glave (Pitch, Yaw, Roll) i crtanje 3D osa"""
    image_points = np.array([
        (landmarks[1].x * w, landmarks[1].y * h),     # Vrh nosa
        (landmarks[152].x * w, landmarks[152].y * h), # Brada
        (landmarks[263].x * w, landmarks[263].y * h), # Levo oko
        (landmarks[33].x * w, landmarks[33].y * h),   # Desno oko
        (landmarks[291].x * w, landmarks[291].y * h), # Leva strana usta
        (landmarks[61].x * w, landmarks[61].y * h)    # Desna strana usta
    ], dtype=np.float64)

    focal_length = w
    center = (w / 2, h / 2)
    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float64)
    dist_coeffs = np.zeros((4, 1))

    success, rvec, tvec = cv2.solvePnP(
        MODEL_POINTS, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not success:
        return 0, 0, 0, None, None

    rmat, _ = cv2.Rodrigues(rvec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
    pitch, yaw, roll = angles[0], angles[1], angles[2]

    axis_len = 50.0
    axis_pts = np.array([
        (axis_len, 0, 0),     # X (Crvena)
        (0, -axis_len, 0),    # Y (Zelena)
        (0, 0, -axis_len)     # Z (Plava)
    ], dtype=np.float64)

    img_axis_pts, _ = cv2.projectPoints(axis_pts, rvec, tvec, camera_matrix, dist_coeffs)
    nose_pt = (int(image_points[0][0]), int(image_points[0][1]))
    
    return pitch, yaw, roll, nose_pt, img_axis_pts

print("=" * 65)
print("AI SISTEM ZA MONITORING VOZACA (DMS) POKRENUT!")
print("Detektuje: Treptanje, Sklapanje ociju, Zevanje, Nagib glave")
print("Kontrole: [c] Obrni R/B boje | [n] NoIR filter | [q] Izlaz")
print("=" * 65)

swap_rb = False
noir_filter = False

def apply_noir_balance(img):
    img_float = img.astype(np.float32)
    img_float[:, :, 2] = img_float[:, :, 2] * 0.85
    img_float[:, :, 0] = img_float[:, :, 0] * 0.90
    img_float[:, :, 1] = np.clip(img_float[:, :, 1] * 1.06, 0, 255)
    return np.clip(img_float, 0, 255).astype(np.uint8)

while True:
    if use_picam2:
        raw_frame = picam2.capture_array()
        raw_frame = cv2.flip(raw_frame, 1)
        frame = raw_frame
    else:
        success, raw_frame = cap.read()
        if not success:
            break
        frame = cv2.flip(raw_frame, 1)

    if swap_rb:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if noir_filter:
        frame = apply_noir_balance(frame)

    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    ear = 0.30
    mar = 0.08
    pitch, yaw, roll = 0.0, 0.0, 0.0
    face_detected = False
    status_text = "SISTEM AKTIVAN - VOZAC BUDAN"
    status_color = (0, 180, 0) # Zelena

    if results.multi_face_landmarks:
        face_detected = True
        landmarks = results.multi_face_landmarks[0].landmark

        # Racunanje EAR (otvorenost ociju)
        ear_left = calc_ear(landmarks, LEFT_EYE, w, h)
        ear_right = calc_ear(landmarks, RIGHT_EYE, w, h)
        ear = (ear_left + ear_right) / 2.0

        # Racunanje MAR (otvorenost usta)
        mar = calc_mar(landmarks, w, h)

        # 1. Konture ociju (Zuta boja)
        left_eye_pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in LEFT_EYE], dtype=np.int32)
        right_eye_pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in RIGHT_EYE], dtype=np.int32)
        cv2.polylines(frame, [left_eye_pts], True, (0, 255, 255), 2)
        cv2.polylines(frame, [right_eye_pts], True, (0, 255, 255), 2)

        # 2. Konture usta (Cijan / Svetlo plava boja)
        mouth_pts = np.array([[int(landmarks[i].x * w), int(landmarks[i].y * h)] for i in LIPS_CONTOUR], dtype=np.int32)
        cv2.polylines(frame, [mouth_pts], True, (255, 200, 0), 2)

        # 3. 3D Ose glave iz nosa
        pitch, yaw, roll, nose_pt, img_axis = estimate_head_pose(landmarks, w, h)
        if nose_pt and img_axis is not None:
            p_x = (int(img_axis[0][0][0]), int(img_axis[0][0][1]))
            p_y = (int(img_axis[1][0][0]), int(img_axis[1][0][1]))
            p_z = (int(img_axis[2][0][0]), int(img_axis[2][0][1]))
            cv2.line(frame, nose_pt, p_x, (0, 0, 255), 3) # X - Crvena
            cv2.line(frame, nose_pt, p_y, (0, 255, 0), 3) # Y - Zelena
            cv2.line(frame, nose_pt, p_z, (255, 0, 0), 3) # Z - Plava

        # Merenje trajanja zazmurenih ociju
        if ear < EAR_THRESHOLD:
            if eyes_closed_start_time is None:
                eyes_closed_start_time = time.time()
            closed_duration = time.time() - eyes_closed_start_time
            perclos_window.append(1)
        else:
            eyes_closed_start_time = None
            closed_duration = 0.0
            perclos_window.append(0)

        # Upozorenja i alarmi na srpskom jeziku
        if closed_duration >= EYES_CLOSED_ALERT_SEC:
            status_text = "ALARM ZA POSPANOST - PROBUDI SE!"
            status_color = (0, 0, 255) # Crvena
        elif mar > MAR_THRESHOLD:
            status_text = "UPOZORENJE NA UMOR (ZEVANJE)"
            status_color = (0, 200, 255) # Zuta/Narandzasta
        elif abs(yaw) > 30 or pitch < -25:
            status_text = "UPOZORENJE: SKRENUT POGLED (GLEDAJ PUT)"
            status_color = (0, 140, 255) # Narandzasta
        elif closed_duration > 0.4:
            status_text = "UPOZORENJE: SKLAPANJE OCIJU"
            status_color = (0, 215, 255)
    else:
        eyes_closed_start_time = None
        closed_duration = 0.0
        status_text = "VOZAC NIJE DETEKTOVAN"
        status_color = (80, 80, 80)

    # Azuriranje istorije za talasni grafikon
    ear_history.append(ear)
    mar_history.append(mar)
    perclos_val = (sum(perclos_window) / len(perclos_window)) * 100.0 if perclos_window else 0.0

    # ================= HUD ELEMETI NA SRPSKOM =================
    
    # 1. Gornji Header
    cv2.putText(frame, "AI SISTEM ZA MONITORING VOZACA", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
    
    # FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time
    cv2.putText(frame, f"FPS: {int(fps)} | Status: AKTIVAN", (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1)

    # 2. Centralni Banner upozorenja
    banner_w, banner_h = 420, 32
    bx1 = (w - banner_w) // 2
    by1 = 55
    cv2.rectangle(frame, (bx1, by1), (bx1 + banner_w, by1 + banner_h), status_color, -1)
    
    text_size = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 2)[0]
    tx = bx1 + (banner_w - text_size[0]) // 2
    ty = by1 + (banner_h + text_size[1]) // 2
    cv2.putText(frame, status_text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 255, 255), 2)

    # 3. DONJI LEVI PANEL: BIOMETRIJSKA TELEMETRIJA
    pan_w, pan_h = 320, 125
    px1, py1 = 10, h - pan_h - 10
    
    overlay = frame.copy()
    cv2.rectangle(overlay, (px1, py1), (px1 + pan_w, py1 + pan_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)
    cv2.rectangle(frame, (px1, py1), (px1 + pan_w, py1 + pan_h), (80, 80, 80), 1)

    cv2.putText(frame, "BIOMETRIJSKA TELEMETRIJA", (px1 + 10, py1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 215, 255), 2)

    # EAR red (otvorenost ociju)
    cv2.putText(frame, f"EAR (Oci): {ear:.3f}", (px1 + 10, py1 + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (230, 230, 230), 1)
    bar_w = int(np.clip(ear / 0.45 * 80, 0, 80))
    bar_col = (0, 255, 0) if ear >= EAR_THRESHOLD else (0, 0, 255)
    cv2.rectangle(frame, (px1 + 210, py1 + 32), (px1 + 210 + bar_w, py1 + 44), bar_col, -1)
    cv2.rectangle(frame, (px1 + 210, py1 + 32), (px1 + 290, py1 + 44), (100, 100, 100), 1)

    # MAR red (otvorenost usta / zevanje)
    cv2.putText(frame, f"MAR (Usta): {mar:.3f}", (px1 + 10, py1 + 62), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (230, 230, 230), 1)
    mar_bar_w = int(np.clip(mar / 0.80 * 80, 0, 80))
    mar_col = (0, 165, 255) if mar >= MAR_THRESHOLD else (180, 180, 180)
    cv2.rectangle(frame, (px1 + 210, py1 + 52), (px1 + 210 + mar_bar_w, py1 + 64), mar_col, -1)
    cv2.rectangle(frame, (px1 + 210, py1 + 52), (px1 + 290, py1 + 64), (100, 100, 100), 1)

    # PERCLOS i Nagib glave
    cv2.putText(frame, f"PERCLOS indeks: {perclos_val:.1f}%", (px1 + 10, py1 + 82), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (220, 220, 220), 1)
    cv2.putText(frame, f"Nagib glave: {pitch:+.1f} | Smer: {yaw:+.1f}", (px1 + 10, py1 + 101), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (190, 190, 190), 1)
    cv2.putText(frame, f"Zazmureno: {closed_duration:.2f}s", (px1 + 10, py1 + 118), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 0, 255) if closed_duration > 0.8 else (190, 190, 190), 1)

    # 4. DONJI DESNI PANEL: TALASNI GRAFIKON
    graph_w, graph_h = 240, 125
    gx1, gy1 = w - graph_w - 10, h - graph_h - 10
    
    overlay_g = frame.copy()
    cv2.rectangle(overlay_g, (gx1, gy1), (gx1 + graph_w, gy1 + graph_h), (20, 20, 20), -1)
    cv2.addWeighted(overlay_g, 0.72, frame, 0.28, 0, frame)
    cv2.rectangle(frame, (gx1, gy1), (gx1 + graph_w, gy1 + graph_h), (80, 80, 80), 1)

    cv2.putText(frame, "GRAFIKON (OCI / USTA)", (gx1 + 10, gy1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1)

    # Crvena referentna linija praga
    thresh_y = int(gy1 + graph_h - 15 - (EAR_THRESHOLD / 0.50) * 70)
    cv2.line(frame, (gx1 + 10, thresh_y), (gx1 + graph_w - 10, thresh_y), (0, 0, 180), 1)

    # Crtanje EAR (Cijan) i MAR (Magenta) krive
    pts_ear = []
    pts_mar = []
    for i in range(len(ear_history)):
        x_pt = int(gx1 + 10 + i * ((graph_w - 20) / (HISTORY_LEN - 1)))
        
        y_ear = int(gy1 + graph_h - 15 - np.clip(ear_history[i] / 0.50, 0, 1) * 70)
        pts_ear.append((x_pt, y_ear))

        y_mar = int(gy1 + graph_h - 15 - np.clip(mar_history[i] / 0.80, 0, 1) * 70)
        pts_mar.append((x_pt, y_mar))

    if len(pts_ear) > 1:
        cv2.polylines(frame, [np.array(pts_ear)], False, (255, 200, 0), 2)  # Cijan za oci
    if len(pts_mar) > 1:
        cv2.polylines(frame, [np.array(pts_mar)], False, (255, 0, 255), 2)  # Magenta za usta

    # Prikaz na ekranu / TV-u
    cv2.imshow("AI Nadzor Vozaca - RPi 5", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == ord('c'):
        swap_rb = not swap_rb
        print(f"[BOJE] Obrtanje Crvena/Plava: {'UKLJUCENO' if swap_rb else 'ISKLJUCENO'}")
    elif key == ord('n'):
        noir_filter = not noir_filter
        print(f"[FILTER] NoIR balans: {'UKLJUCEN' if noir_filter else 'ISKLJUCEN'}")

if use_picam2:
    picam2.stop()
else:
    cap.release()

cv2.destroyAllWindows()
