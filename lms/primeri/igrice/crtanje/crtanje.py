#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
             🎨 SVETLEĆI ČAROBNI ŠTAPIĆ (AIR GLOW PAINTER) — PREDŠKOLCI
================================================================================
Opis:
  Ultra-brzo crtanje svetlom u vazduhu pomoću kažiprsta.
  Asinhrona obrada slike i MediaPipe-a za 40+ FPS bez seckanja.
  Boje su 100% prirodne i jasne.

Kontrole:
  - [Kažiprst gore] Crtaj čarobnom svetlošću u vazduhu
  - [c] Obriši crtež
  - [t] Promeni šablon za bojenje (Prazno / Zvezda / Srce / Maca)
  - [q] ili [ESC] Povratak u meni
================================================================================
"""

import os
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

import cv2
import numpy as np
import mediapipe as mp
import time
import math
import random
import threading
import sys

# Audio sistem
sound_enabled = True
snd_sparkle = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def make_sparkle():
        sr = 44100
        d = 0.08
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        f = np.linspace(600, 1100, n)
        wave = np.sin(2 * np.pi * f * t) * 0.18
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    snd_sparkle = make_sparkle()
except Exception:
    sound_enabled = False

def play_sound(snd):
    if sound_enabled and snd is not None:
        try:
            snd.play()
        except Exception:
            pass

WIDTH = 640
HEIGHT = 480
WINDOW_NAME = "Carobni Stapic - Crtanje"

class FastVisionDrawing:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.use_picam2 = False
        self.latest_frame = None
        self.pointer_pos = (-1, -1)
        self.is_drawing = False
        self.lock = threading.Lock()
        self.running = True

        try:
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"format": "RGB888", "size": (width, height)}
            )
            self.picam2.configure(config)
            self.picam2.start()
            self.use_picam2 = True
            print("[INFO] Picamera2 aktivirana sa prirodnim bojama.")
        except Exception as e:
            print(f"[INFO] OpenCV VideoCapture fallback: {e}")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self.cam_thread = threading.Thread(target=self._cam_worker, daemon=True)
        self.cam_thread.start()

        self.ai_thread = threading.Thread(target=self._ai_worker, daemon=True)
        self.ai_thread.start()
        time.sleep(0.3)

    def _cam_worker(self):
        while self.running:
            try:
                if self.use_picam2:
                    frame = self.picam2.capture_array()
                else:
                    ret, frame = self.cap.read()
                    if not ret:
                        time.sleep(0.01)
                        continue
                with self.lock:
                    self.latest_frame = frame
            except Exception:
                time.sleep(0.005)

    def _ai_worker(self):
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            model_complexity=0,
            max_num_hands=1,
            min_detection_confidence=0.45,
            min_tracking_confidence=0.45
        )
        while self.running:
            frame_to_process = None
            with self.lock:
                if self.latest_frame is not None:
                    frame_to_process = self.latest_frame.copy()

            if frame_to_process is None:
                time.sleep(0.01)
                continue

            frame_flipped = cv2.flip(frame_to_process, 1)
            rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            px, py = -1, -1
            drawing = False

            if results.multi_hand_landmarks:
                hlm = results.multi_hand_landmarks[0]
                lm8 = hlm.landmark[8]  # Kažiprst vrh
                lm6 = hlm.landmark[6]  # Kažiprst zglob
                lm12 = hlm.landmark[12] # Srednji prst vrh

                px = int(lm8.x * self.width)
                py = int(lm8.y * self.height)

                # Crtanje je aktivno kada je kažiprst podignut iznad zgloba
                if lm8.y < lm6.y:
                    drawing = True

            with self.lock:
                self.pointer_pos = (px, py)
                self.is_drawing = drawing

            time.sleep(0.002)

    def get_state(self):
        with self.lock:
            if self.latest_frame is not None:
                f = cv2.flip(self.latest_frame, 1)
                return f, self.pointer_pos, self.is_drawing
            return None, (-1, -1), False

    def stop(self):
        self.running = False
        try:
            self.cam_thread.join(timeout=0.5)
            self.ai_thread.join(timeout=0.5)
            if self.use_picam2:
                self.picam2.stop()
                self.picam2.close()
            else:
                self.cap.release()
        except Exception:
            pass

vision = FastVisionDrawing(WIDTH, HEIGHT)

drawing_layer = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

TEMPLATES = ["PRAZNO", "ZVEZDA", "SRCE", "MACA"]
current_template_idx = 0

def draw_template(img, t_type):
    cx, cy = WIDTH // 2, HEIGHT // 2
    col = (130, 130, 150)
    th = 2
    if t_type == "ZVEZDA":
        pts = []
        r_out, r_in = 110, 48
        for i in range(10):
            ang = math.radians(i * 36 - 90)
            r = r_out if i % 2 == 0 else r_in
            pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
        cv2.polylines(img, [np.array(pts, np.int32)], True, col, th, cv2.LINE_AA)
        cv2.putText(img, "OBOJ ZVEZDU!", (cx - 85, cy + 150), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 240), 2, cv2.LINE_AA)
    elif t_type == "SRCE":
        r = 55
        c1 = (cx - r//2, cy - r//2)
        c2 = (cx + r//2, cy - r//2)
        cv2.circle(img, c1, r//2, col, th, cv2.LINE_AA)
        cv2.circle(img, c2, r//2, col, th, cv2.LINE_AA)
        pts_tri = np.array([(cx - r, cy - r//3), (cx + r, cy - r//3), (cx, cy + r)], np.int32)
        cv2.polylines(img, [pts_tri], True, col, th, cv2.LINE_AA)
        cv2.putText(img, "OBOJ SRCE!", (cx - 75, cy + 140), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 240), 2, cv2.LINE_AA)
    elif t_type == "MACA":
        cv2.circle(img, (cx, cy + 10), 75, col, th, cv2.LINE_AA)
        pts_l = np.array([(cx - 70, cy - 25), (cx - 55, cy - 90), (cx - 15, cy - 60)], np.int32)
        pts_r = np.array([(cx + 70, cy - 25), (cx + 55, cy - 90), (cx + 15, cy - 60)], np.int32)
        cv2.polylines(img, [pts_l], True, col, th, cv2.LINE_AA)
        cv2.polylines(img, [pts_r], True, col, th, cv2.LINE_AA)
        cv2.putText(img, "NACRTAJ MACU!", (cx - 95, cy + 150), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 240), 2, cv2.LINE_AA)

prev_pt = None
hue_counter = 0
particles = []

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("=" * 60)
print("POKRENUT BRZI 'SVETLEĆI ČAROBNI ŠTAPIĆ' (PRIRODNE BOJE & 40+ FPS)")
print("Kontrole: [c] Očisti  |  [t] Šablon  |  [q] Izlaz")
print("=" * 60)

try:
    while True:
        frame, (px, py), is_drawing = vision.get_state()
        if frame is None:
            time.sleep(0.005)
            continue

        # Dugačke boje (HSV spektar za čarobni sjaj)
        hue_counter = (hue_counter + 3) % 180
        hsv_color = np.uint8([[[hue_counter, 255, 255]]])
        glow_bgr = cv2.cvtColor(hsv_color, cv2.COLOR_HSV2BGR)[0][0]
        glow_color = (int(glow_bgr[0]), int(glow_bgr[1]), int(glow_bgr[2]))

        # Crtanje linija
        if is_drawing and px > 0 and py > 0:
            if prev_pt is not None:
                # Glavna linija i mekani sjaj
                cv2.line(drawing_layer, prev_pt, (px, py), glow_color, 8, cv2.LINE_AA)
                cv2.line(drawing_layer, prev_pt, (px, py), (255, 255, 255), 3, cv2.LINE_AA)

            prev_pt = (px, py)

            # Čestice iskrica
            if random.random() < 0.65:
                play_sound(snd_sparkle)
                for _ in range(3):
                    particles.append({
                        "x": px + random.randint(-8, 8),
                        "y": py + random.randint(-8, 8),
                        "vx": random.uniform(-2, 2),
                        "vy": random.uniform(-2, 2),
                        "color": glow_color,
                        "life": random.randint(12, 24),
                        "size": random.randint(2, 5)
                    })
        else:
            prev_pt = None

        # Template
        draw_template(frame, TEMPLATES[current_template_idx])

        # Spajanje sloja crteža sa živom kamerom
        mask = cv2.cvtColor(drawing_layer, cv2.COLOR_BGR2GRAY)
        _, mask_bin = cv2.threshold(mask, 10, 255, cv2.THRESH_BINARY)
        inv_mask = cv2.bitwise_not(mask_bin)

        frame_bg = cv2.bitwise_and(frame, frame, mask=inv_mask)
        frame = cv2.add(frame_bg, drawing_layer)

        # Čestice zvezdica
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)
            else:
                cv2.circle(frame, (int(p["x"]), int(p["y"])), p["size"], p["color"], -1, cv2.LINE_AA)

        # Kursor vrha štapića
        if px > 0 and py > 0:
            cv2.circle(frame, (px, py), 12, (0, 240, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, (px, py), 16, (255, 255, 255), 2, cv2.LINE_AA)

        # Header info
        cv2.rectangle(frame, (10, 10), (280, 50), (30, 30, 40), -1)
        cv2.rectangle(frame, (10, 10), (280, 50), (0, 215, 255), 2)
        cv2.putText(frame, f"SABLON: {TEMPLATES[current_template_idx]}", (20, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('c'):
            drawing_layer[:] = 0
            particles.clear()
        elif key == ord('t'):
            current_template_idx = (current_template_idx + 1) % len(TEMPLATES)

finally:
    vision.stop()
    cv2.destroyAllWindows()
    print("[INFO] Igra crtanje završena.")
