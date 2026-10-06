import time
import math
import cv2
import mediapipe as mp
import numpy as np
from picamera2 import Picamera2

# -------------------------------------------------------------
# Inicijalizacija MediaPipe modela
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
# Inicijalizacija Picamera2 (IMX708 na RPi 5)
# -------------------------------------------------------------
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(config)
picam2.start()

# Dajemo senzoru kratko vreme da podesi automatsku ekspoziciju i balans bele
time.sleep(1.0)

# -------------------------------------------------------------
# 1. Kalibracija pozadine
# -------------------------------------------------------------
print("\n--- SKLONITE SE IZ KADRA ---")
print("Kamera snima praznu pozadinu za 2 sekunde...")
time.sleep(2)

# Čitamo nekoliko frejmova radi stabilizacije slike
background_rgb = None
for _ in range(15):
    background_rgb = picam2.capture_array()

if background_rgb is None:
    print("Greška: Nije moguće pročitati sliku sa kamere.")
    picam2.stop()
    exit()

print("✅ Pozadina uspešno snimljena! Uđite u kadar.")
print("Puknite prstima ispred kamere da nestanete / vratite se (taster 'q' za izlaz).\n")

# -------------------------------------------------------------
# Logika i varijable stanja za pucketanje
# -------------------------------------------------------------
invisible = False
snap_state = "IDLE"
ready_timestamp = 0
last_snap_time = 0
COOLDOWN = 1.0  # Minimalni razmak između dva pucketanja u sekundama

def get_dist(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

try:
    while True:
        # Picamera2 vraća NumPy niz direktno u RGB formatu
        frame_rgb = picam2.capture_array()
        
        # Horizontalno ogledalo radi prirodnijeg praćenja na ekranu
        frame_rgb = cv2.flip(frame_rgb, 1)
        current_time = time.time()

        # Detekcija šake
        hand_results = hands.process(frame_rgb)
        snap_detected = False

        # Pravimo kopiju za iscrtavanje linija prstiju
        display_rgb = frame_rgb.copy()

        if hand_results.multi_hand_landmarks:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                mp_draw.draw_landmarks(display_rgb, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                lm = hand_landmarks.landmark

                # Dužina dlana (tačka 0 do tačke 9) služi kao referenca za normalizaciju
                palm_size = get_dist(lm[0], lm[9])
                if palm_size == 0:
                    continue

                thumb_tip = lm[4]      # Vrh palca
                middle_tip = lm[12]    # Vrh srednjeg prsta
                index_tip = lm[8]      # Vrh kažiprsta

                thumb_middle_dist = get_dist(thumb_tip, middle_tip) / palm_size
                thumb_index_dist = get_dist(thumb_tip, index_tip) / palm_size

                # Faza 1: PRIPREMA (palac i srednji prst su pritisnuti, kažiprst nije)
                if thumb_middle_dist < 0.28 and thumb_index_dist > 0.35:
                    if snap_state == "IDLE" and (current_time - last_snap_time > COOLDOWN):
                        snap_state = "READY"
                        ready_timestamp = current_time

                # Faza 2: PUCANJE (srednji prst se naglo odvaja od palca ka dlanu)
                elif snap_state == "READY":
                    if current_time - ready_timestamp > 1.2:
                        snap_state = "IDLE"
                    elif thumb_middle_dist > 0.50:
                        snap_detected = True
                        snap_state = "IDLE"
                        last_snap_time = current_time

        # Promena stanja kada se detektuje pucanj
        if snap_detected:
            invisible = not invisible
            print(f"💥 PUCKETANJE! Stanje: {'NEVIDLJIV' if invisible else 'VIDLJIV'}")

        # Renderovanje efekta nevidljivosti
        if invisible:
            seg_results = segmentor.process(frame_rgb)
            mask = seg_results.segmentation_mask > 0.65
            mask_3d = np.dstack((mask, mask, mask))
            
            # Gde je prepoznato telo, zamenjujemo ga sačuvanom pozadinom
            output_rgb = np.where(mask_3d, background_rgb, display_rgb)
        else:
            output_rgb = display_rgb

        # Statusni tekst na ekranu
        status_text = "NEVIDLJIV" if invisible else "VIDLJIV"
        status_color = (255, 0, 0) if invisible else (0, 255, 0)
        cv2.putText(output_rgb, f"Status: {status_text}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)

        ready_color = (255, 255, 0) if snap_state == "READY" else (160, 160, 160)
        cv2.putText(output_rgb, f"Snap Ready: {snap_state}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, ready_color, 2)

        # OpenCV imshow očekuje BGR format
        output_bgr = cv2.cvtColor(output_rgb, cv2.COLOR_RGB2BGR)
        cv2.imshow("Hand Snap Invisibility Demo", output_bgr)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # Ručni prekidač preko razmaka za test
            invisible = not invisible

finally:
    picam2.stop()
    cv2.destroyAllWindows()