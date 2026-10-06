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

# -------------------------------------------------------------
# Inicijalizacija MediaPipe modela (Hands + SelfieSegmentation)
# -------------------------------------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

mp_selfie = mp.solutions.selfie_segmentation
segmentor = mp_selfie.SelfieSegmentation(model_selection=1)

# -------------------------------------------------------------
# Inicijalizacija kamere (Picamera2 za RPi 5 sa fallback-om na OpenCV)
# -------------------------------------------------------------
use_picam2 = False
picam2 = None
cap = None

try:
    from picamera2 import Picamera2
    print("[INFO] Pokrecem kameru preko nativnog Picamera2 drajvera (IMX708)...")
    picam2 = Picamera2()
    # BGR888 je nativan format za OpenCV prikaz (daje tacne prirodne boje)
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "BGR888"}
    )
    picam2.configure(config)
    picam2.start()
    use_picam2 = True
    print("[INFO] Camera Module 3 je uspesno aktiviran sa BGR formatom boja!")
except Exception as e:
    print(f"[INFO] Picamera2 nije ucitana ({e}), pokusavam standardni OpenCV VideoCapture...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not use_picam2 and (cap is None or not cap.isOpened()):
    print("\n[GRESKA] Kamera nije pronadjena! Pokreni skriptu sa: libcamerify python pucketanje.py")
    exit(1)

# Ostavljamo senzoru vreme za automatsku ekspoziciju i balans bele
time.sleep(2.0)

# Opcije boja i filtera
swap_rb = False
noir_filter = False

def apply_noir_balance(img):
    """Blaga korekcija infracrvenog spektra za NoIR senzore."""
    img_float = img.astype(np.float32)
    img_float[:, :, 2] = img_float[:, :, 2] * 0.85  # Crveni kanal
    img_float[:, :, 0] = img_float[:, :, 0] * 0.90  # Plavi kanal
    img_float[:, :, 1] = np.clip(img_float[:, :, 1] * 1.06, 0, 255)  # Zeleni kanal
    return np.clip(img_float, 0, 255).astype(np.uint8)

# -------------------------------------------------------------
# 1. Kalibracija pozadine i stabilizacija parametara
# -------------------------------------------------------------
def snimi_pozadinu():
    print("\n" + "=" * 60)
    print("--- SKLONITE SE IZ KADRA ---")
    print("Kamera snima cistu pozadinu za 2 sekunde...")
    print("=" * 60)
    time.sleep(2.0)

    # Stabilizacija frejmova pre snimanja
    for _ in range(15):
        if use_picam2:
            _ = picam2.capture_array()
        else:
            _, _ = cap.read()

    if use_picam2:
        raw_bg = picam2.capture_array()
        meta = picam2.capture_metadata()
        exp_time = meta.get("ExposureTime", 20000)
        gain = meta.get("AnalogueGain", 1.0)
        lens_pos = meta.get("LensPosition", 0.0)
        cg = meta.get("ColourGains", None)

        # Fiksiramo ekspoziciju i fokus da pozadina ne 'dise' kad udje covek,
        # ali zakljucavamo i tacne ColourGains balansa bele
        ctrls = {
            "AfMode": 0,
            "LensPosition": lens_pos,
            "AeEnable": False,
            "ExposureTime": exp_time,
            "AnalogueGain": gain
        }
        if cg is not None:
            ctrls["AwbEnable"] = False
            ctrls["ColourGains"] = cg

        try:
            picam2.set_controls(ctrls)
        except Exception as err:
            print(f"[INFO] set_controls info: {err}")
    else:
        ret, raw_bg = cap.read()
        if not ret:
            raw_bg = None

    if raw_bg is None:
        print("[GRESKA] Nije moguce snimiti pozadinu!")
        return None

    bg = cv2.flip(raw_bg, 1)
    print("✅ Pozadina uspesno snimljena! Udjite u kadar.")
    print("Puknite prstima za nevidljivost | [c] Obrni R/B boje | [n] NoIR filter | [r] Nova pozadina | [q] Izlaz\n")
    return bg

background_bgr = snimi_pozadinu()
if background_bgr is None:
    if use_picam2:
        picam2.stop()
    else:
        cap.release()
    exit(1)

# -------------------------------------------------------------
# Logika za detekciju pucketanja (Snap Gesture)
# -------------------------------------------------------------
invisible = False
snap_state = "IDLE"
ready_timestamp = 0
last_snap_time = 0
COOLDOWN = 0.9

dilate_kernel = np.ones((5, 5), np.uint8)

def get_dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

prev_time = 0

try:
    while True:
        if use_picam2:
            raw_frame = picam2.capture_array()
            frame = cv2.flip(raw_frame, 1)
        else:
            success, raw_frame = cap.read()
            if not success:
                break
            frame = cv2.flip(raw_frame, 1)

        current_time = time.time()

        # Opcioni filteri boja po zelji korisnika
        if swap_rb:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if noir_filter:
            frame = apply_noir_balance(frame)

        # MediaPipe radi na RGB formatu
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detekcija sake
        hand_results = hands.process(rgb_frame)
        snap_detected = False

        display_frame = frame.copy()

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_draw.draw_landmarks(display_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                lm = hand_landmarks.landmark

                # Normalizacija prema duzini dlana
                palm_size = get_dist(lm[0], lm[9])
                if palm_size == 0:
                    continue

                thumb_tip = lm[4]      # Vrh palca
                middle_tip = lm[12]    # Vrh srednjeg prsta
                index_tip = lm[8]      # Vrh kaziprsta

                thumb_middle_dist = get_dist(thumb_tip, middle_tip) / palm_size
                thumb_index_dist = get_dist(thumb_tip, index_tip) / palm_size

                # Faza 1: Priprema (palac i srednji prst spojeni, kaziprst opruzen)
                if thumb_middle_dist < 0.28 and thumb_index_dist > 0.35:
                    if snap_state == "IDLE" and (current_time - last_snap_time > COOLDOWN):
                        snap_state = "READY"
                        ready_timestamp = current_time

                # Faza 2: Pucanj (srednji prst naglo otpusti ka dlanu)
                elif snap_state == "READY":
                    if current_time - ready_timestamp > 1.2:
                        snap_state = "IDLE"
                    elif thumb_middle_dist > 0.48:
                        snap_detected = True
                        snap_state = "IDLE"
                        last_snap_time = current_time

        if snap_detected:
            invisible = not invisible
            print(f"💥 PUCKETANJE DETEKTOVANO! Stanje: {'NEVIDLJIV' if invisible else 'VIDLJIV'}")

        # Renderovanje nevidljivosti (Segmentacija tela)
        if invisible:
            seg_results = segmentor.process(rgb_frame)
            mask = seg_results.segmentation_mask > 0.55
            mask_dilated = cv2.dilate(mask.astype(np.uint8), dilate_kernel, iterations=2).astype(bool)
            mask_3d = np.dstack((mask_dilated, mask_dilated, mask_dilated))

            # Primeni NoIR filter i na pozadinu ako je aktivan
            bg_to_use = background_bgr
            if swap_rb:
                bg_to_use = cv2.cvtColor(bg_to_use, cv2.COLOR_BGR2RGB)
            if noir_filter:
                bg_to_use = apply_noir_balance(bg_to_use)

            output = np.where(mask_3d, bg_to_use, display_frame)
        else:
            output = display_frame

        # FPS proracun
        fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
        prev_time = current_time

        # HUD status na ekranu
        status_text = "NEVIDLJIV (CLOAK ON)" if invisible else "VIDLJIV (NORMAL)"
        status_color = (0, 165, 255) if invisible else (0, 220, 0)
        cv2.rectangle(output, (10, 10), (380, 100), (20, 20, 20), -1)
        cv2.rectangle(output, (10, 10), (380, 100), (60, 60, 60), 1)

        cv2.putText(output, f"Status: {status_text}", (20, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, status_color, 2)

        ready_color = (0, 255, 255) if snap_state == "READY" else (140, 140, 140)
        cv2.putText(output, f"Snap Detektor: {snap_state}", (20, 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, ready_color, 2)

        info_flags = f"FPS: {int(fps)} | [c] R/B: {'SWAP' if swap_rb else 'NORM'} | [n] NoIR: {'ON' if noir_filter else 'OFF'}"
        cv2.putText(output, info_flags, (20, 92),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        # Direktan prikaz frejma u BGR formatu
        cv2.imshow("Pucketanje Prstima - Nevidljivost (RPi 5)", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord(' '):
            invisible = not invisible
            print(f"[RUCNO] Nevidljivost: {'UKLJUCENA' if invisible else 'ISKLJUCENA'}")
        elif key == ord('c'):
            swap_rb = not swap_rb
            print(f"[BOJE] Obrtanje Crvena/Plava: {'UKLJUCENO' if swap_rb else 'ISKLJUCENO'}")
        elif key == ord('n'):
            noir_filter = not noir_filter
            print(f"[FILTER] NoIR balans svetla: {'UKLJUCEN' if noir_filter else 'ISKLJUCEN'}")
        elif key == ord('r'):
            novi_bg = snimi_pozadinu()
            if novi_bg is not None:
                background_bgr = novi_bg

finally:
    if use_picam2:
        picam2.stop()
    else:
        cap.release()
    cv2.destroyAllWindows()
