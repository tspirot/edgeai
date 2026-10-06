import os
import time
import math
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

# Inicijalizacija MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# Inicijalizacija kamere (Picamera2 za RPi 5 sa fallback-om na OpenCV)
use_picam2 = False
picam2 = None
cap = None

try:
    from picamera2 import Picamera2
    print("[INFO] Pokrecem kameru preko nativnog Picamera2 drajvera (IMX708)...")
    picam2 = Picamera2()
    # RGB888 konfiguracija daje tačan BGR raspored u OpenCV memoriji
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
    print("[GRESKA] Kamera nije pronadjena! Pokreni skriptu sa: libcamerify python mesec.py")
    exit(1)

# Generisanje radijalne mape osvetljenja (Radial Light Kernel za realno svetlo)
KERNEL_RADIUS = 240
ky, kx = np.ogrid[-KERNEL_RADIUS:KERNEL_RADIUS, -KERNEL_RADIUS:KERNEL_RADIUS]
kdist = np.sqrt(kx*kx + ky*ky)
# Pad jacine svetlosti po fizickom modelu (Inverse square falloff)
light_kernel = np.clip(1.0 / (1.0 + (kdist / 60.0)**2), 0, 1).astype(np.float32)

# Teme boja meseca i svetlosti
COLOR_MODES = [
    {"name": "Srebrni Mesec", "core": (255, 255, 255), "glow": (255, 240, 210), "light": (180, 160, 120)},
    {"name": "Zlatni Mesec", "core": (255, 255, 230), "glow": (100, 210, 255), "light": (60, 150, 210)},
    {"name": "Plavi Misticni Mesec", "core": (255, 255, 255), "glow": (255, 200, 80), "light": (200, 140, 40)},
    {"name": "Neon Etericni Mesec", "core": (240, 255, 240), "glow": (120, 255, 140), "light": (60, 180, 90)}
]
current_mode_idx = 0

def draw_realistic_moon(frame, cx, cy, radius, theme):
    """Crta mesec sa dinamicnim osvetljenjem prostora i slojevitim sjajem (bloom)"""
    h, w, _ = frame.shape
    
    # 1. AMBIJENTALNO OSVETLJENJE (Svetlost koja realno osvetljava ruku, lice i scenu)
    x1 = max(0, cx - KERNEL_RADIUS)
    x2 = min(w, cx + KERNEL_RADIUS)
    y1 = max(0, cy - KERNEL_RADIUS)
    y2 = min(h, cy + KERNEL_RADIUS)
    
    kx1 = x1 - (cx - KERNEL_RADIUS)
    kx2 = kx1 + (x2 - x1)
    ky1 = y1 - (cy - KERNEL_RADIUS)
    ky2 = ky1 + (y2 - y1)
    
    if x2 > x1 and y2 > y1:
        patch = frame[y1:y2, x1:x2].astype(np.float32)
        k_patch = light_kernel[ky1:ky2, kx1:kx2, np.newaxis]
        l_col = np.array(theme["light"], dtype=np.float32)
        # Dodavanje svetla na scenu
        illuminated = patch + k_patch * l_col * 0.70
        frame[y1:y2, x1:x2] = np.clip(illuminated, 0, 255).astype(np.uint8)

    # 2. SLOJEVITI SJAJ OKO MESECA (Multi-layer Bloom Aura)
    overlay = frame.copy()
    glow_col = theme["glow"]
    
    # Veliki meki oreol
    cv2.circle(overlay, (cx, cy), int(radius * 2.8), glow_col, -1)
    cv2.circle(overlay, (cx, cy), int(radius * 1.9), (255, 255, 255), -1)
    cv2.addWeighted(overlay, 0.35, frame, 0.65, 0, frame)
    
    # Unutrasnji jaci sjaj
    overlay2 = frame.copy()
    cv2.circle(overlay2, (cx, cy), int(radius * 1.4), glow_col, -1)
    cv2.addWeighted(overlay2, 0.45, frame, 0.55, 0, frame)
    
    # 3. GLAVNA KUGLA MESECA (Mesec sa kraterima)
    core_col = theme["core"]
    cv2.circle(frame, (cx, cy), radius, core_col, -1)
    
    # Krateri
    crater_col = (max(0, core_col[0] - 40), max(0, core_col[1] - 40), max(0, core_col[2] - 40))
    if radius > 15:
        cv2.circle(frame, (cx - int(radius * 0.3), cy - int(radius * 0.2)), int(radius * 0.22), crater_col, -1)
        cv2.circle(frame, (cx + int(radius * 0.25), cy + int(radius * 0.3)), int(radius * 0.18), crater_col, -1)
        cv2.circle(frame, (cx + int(radius * 0.35), cy - int(radius * 0.25)), int(radius * 0.14), crater_col, -1)
        cv2.circle(frame, (cx - int(radius * 0.2), cy + int(radius * 0.35)), int(radius * 0.12), crater_col, -1)

    # 4. SJAJNO USIJANJE U CENTRU (Hot white core)
    cv2.circle(frame, (cx - int(radius * 0.12), cy - int(radius * 0.12)), int(radius * 0.42), (255, 255, 255), -1)

print("=" * 60)
print("Aplikacija 'MESEC' pokrenuta!")
print("Kontrole:")
print("  [m] - Promeni temu/boju meseca (Srebrni, Zlatni, Plavi...)")
print("  [+] / [-] - Povecaj / smanji osnovnu velicinu meseca")
print("  [q] - Izlaz")
print("=" * 60)

# Glatko kretanje (Damping filter za uklanjanje podrhtavanja)
smooth_x, smooth_y = None, None
smooth_r = 38
base_radius = 38
prev_time = 0

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

    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    hand_detected = False
    target_x, target_y = 0, 0
    target_r = base_radius

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        lm = hand_landmarks.landmark

        thumb_x, thumb_y = int(lm[4].x * w), int(lm[4].y * h)
        index_x, index_y = int(lm[8].x * w), int(lm[8].y * h)
        palm_x, palm_y = int(lm[9].x * w), int(lm[9].y * h)

        # Rastojanje izmedju palca i kaziprsta
        pinch_dist = math.hypot(thumb_x - index_x, thumb_y - index_y)

        # Pozicija meseca: Prirodno u ruci izmedju palca, kaziprsta i dlana
        target_x = int(thumb_x * 0.35 + index_x * 0.35 + palm_x * 0.3)
        target_y = int(thumb_y * 0.35 + index_y * 0.35 + palm_y * 0.3)

        # Velicina meseca dinamicki reaguje na otvaranje/zatvaranje sake
        target_r = int(np.clip(base_radius * (pinch_dist / 110.0), 22, 90))
        hand_detected = True

    # Glatko kretanje meseca (stabilno pracenje bez trzanja)
    if hand_detected:
        if smooth_x is None:
            smooth_x, smooth_y = target_x, target_y
            smooth_r = target_r
        else:
            smooth_x = int(smooth_x * 0.65 + target_x * 0.35)
            smooth_y = int(smooth_y * 0.65 + target_y * 0.35)
            smooth_r = int(smooth_r * 0.75 + target_r * 0.25)

        # Iscrtavanje meseca sa osvetljenjem
        current_theme = COLOR_MODES[current_mode_idx]
        draw_realistic_moon(frame, smooth_x, smooth_y, smooth_r, current_theme)
    else:
        smooth_x, smooth_y = None, None

    # FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if prev_time != 0 else 0
    prev_time = curr_time

    # Prikaz na ekranu
    theme_name = COLOR_MODES[current_mode_idx]["name"]
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Mesec: {theme_name} [m]", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    if not hand_detected:
        cv2.putText(frame, "Pruzi ruku u kadar da drzis Mesec...", (w // 2 - 180, h - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2)

    cv2.imshow("Mesec Svetlost - RPi 5", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == ord('m'):
        current_mode_idx = (current_mode_idx + 1) % len(COLOR_MODES)
        print(f"[INFO] Promenjena tema: {COLOR_MODES[current_mode_idx]['name']}")
    elif key == ord('+') or key == ord('='):
        base_radius = min(90, base_radius + 5)
    elif key == ord('-'):
        base_radius = max(15, base_radius - 5)

if use_picam2:
    picam2.stop()
else:
    cap.release()

cv2.destroyAllWindows()
