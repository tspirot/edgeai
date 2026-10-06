#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
             🎈 ČAROBNI MEHURIĆI (MAGIC BUBBLE POP) — PREDŠKOLCI
================================================================================
Opis:
  Ultra-brza i prirodno obojena interaktivna igra puckanja balona.
  Asinhrona obrada kamere i MediaPipe-a za 40+ FPS bez kašnjenja.
  Boje su 100% prirodne (ispravno mapirane za OpenCV).

Kontrole:
  - [Dodir šakom / prstićem] Puckanje balona
  - [r] Resetuj igru (očisti balone)
  - [m] Uključi / isključi zvuk
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

# Audio sistem (Pygame sintetizovani zvuci)
sound_enabled = True
snd_pop = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def make_pop():
        sr = 44100
        d = 0.07
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        f = np.linspace(750, 180, n)
        env = np.exp(-12.0 * t / d)
        wave = np.sin(2 * np.pi * f * t) * env * 0.35
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    snd_pop = make_pop()
except Exception:
    sound_enabled = False

def play_sound(snd):
    if sound_enabled and snd is not None:
        try:
            snd.play()
        except Exception:
            pass

# Asinhroni vid i kamera za maksimalan FPS i prirodne boje
class FastVisionHands:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.use_picam2 = False
        self.latest_frame = None
        self.touch_points = []
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
            max_num_hands=2,
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

            # Ogledalo za prirodan prikaz
            frame_flipped = cv2.flip(frame_to_process, 1)
            # Picamera2 RGB888 u OpenCV memoriji ima BGR raspored, za MediaPipe konvertujemo u RGB
            rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            pts = []
            if results.multi_hand_landmarks:
                for hlms in results.multi_hand_landmarks:
                    for idx in [4, 8, 12]:
                        lm = hlms.landmark[idx]
                        pts.append((int(lm.x * self.width), int(lm.y * self.height)))

            with self.lock:
                self.touch_points = pts
            time.sleep(0.002)

    def get_frame_and_points(self):
        with self.lock:
            if self.latest_frame is not None:
                # Frame se okreće kao ogledalo i prikazuje DIREKTNO bez kolor konverzije (100% prirodne boje)
                f = cv2.flip(self.latest_frame, 1)
                pts = list(self.touch_points)
                return f, pts
            return None, []

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

WIDTH = 640
HEIGHT = 480
WINDOW_NAME = "Carobni Mehurici - Predskolci"

vision = FastVisionHands(WIDTH, HEIGHT)

BALLOON_PALETTES = [
    {"body": (40, 80, 245),   "shine": (120, 160, 255)}, # Crveni
    {"body": (230, 110, 40),  "shine": (250, 170, 100)}, # Plavi
    {"body": (60, 205, 80),   "shine": (130, 245, 140)}, # Zeleni
    {"body": (210, 70, 190),  "shine": (245, 140, 230)}, # Ljubičasti
    {"body": (30, 160, 255),  "shine": (120, 210, 255)}, # Narandžasti
]

class Balloon:
    def __init__(self):
        self.r = random.randint(28, 42)
        self.x = random.randint(self.r + 20, WIDTH - self.r - 20)
        self.y = HEIGHT + self.r + random.randint(10, 80)
        self.speed_y = random.uniform(2.5, 4.5)
        self.wobble_phase = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(0.05, 0.09)
        self.wobble_amp = random.uniform(15, 30)
        self.base_x = self.x

        self.palette = random.choice(BALLOON_PALETTES)
        self.is_popped = False

    def update(self):
        self.y -= self.speed_y
        self.wobble_phase += self.wobble_speed
        self.x = self.base_x + math.sin(self.wobble_phase) * self.wobble_amp

    def is_touching(self, px, py):
        return math.hypot(self.x - px, self.y - py) < (self.r + 12)

def draw_balloon(img, b):
    cx, cy, r = int(b.x), int(b.y), int(b.r)
    # Telo balona
    cv2.circle(img, (cx, cy), r, b.palette["body"], -1, cv2.LINE_AA)
    cv2.circle(img, (cx, cy), r, (255, 255, 255), 2, cv2.LINE_AA)
    # Sjaj
    cv2.ellipse(img, (cx - int(r * 0.35), cy - int(r * 0.35)), (int(r * 0.32), int(r * 0.18)), -35, 0, 360, b.palette["shine"], -1, cv2.LINE_AA)
    # Čvorić
    pts_knot = np.array([(cx - 3, cy + r), (cx + 3, cy + r), (cx, cy + r + 4)], np.int32)
    cv2.fillPoly(img, [pts_knot], b.palette["body"], cv2.LINE_AA)
    # Beli sjaj u centru
    cv2.circle(img, (cx, cy), int(r * 0.22), (255, 255, 255), -1, cv2.LINE_AA)

balloons = [Balloon() for _ in range(6)]
particles = []
score = 0

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("=" * 60)
print("POKRENUTI BRZI ČAROBNI MEHURIĆI (PRIRODNE BOJE & 40+ FPS)")
print("Mahite rukama i dodirujte balone na ekranu!")
print("Kontrole: [r] Reset  |  [m] Zvuk  |  [q] Izlaz")
print("=" * 60)

try:
    while True:
        frame, touch_points = vision.get_frame_and_points()
        if frame is None:
            time.sleep(0.005)
            continue

        # Svetlucave tačkice na prstićima
        for pt in touch_points:
            cv2.circle(frame, pt, 12, (0, 240, 255), -1, cv2.LINE_AA)
            cv2.circle(frame, pt, 16, (255, 255, 255), 2, cv2.LINE_AA)

        # Provera sudara balona
        for b in balloons:
            b.update()
            for tp in touch_points:
                if b.is_touching(tp[0], tp[1]):
                    b.is_popped = True
                    play_sound(snd_pop)
                    score += 10

                    for _ in range(20):
                        particles.append({
                            "x": b.x,
                            "y": b.y,
                            "vx": random.uniform(-5, 5),
                            "vy": random.uniform(-6, 2),
                            "color": random.choice([b.palette["body"], (0, 240, 255), (255, 255, 255)]),
                            "size": random.randint(3, 7),
                            "life": random.randint(15, 28)
                        })

        # Ukloni puknute i balone koji su izašli van ekrana
        new_balloons = []
        for b in balloons:
            if not b.is_popped and b.y > -b.r - 20:
                new_balloons.append(b)
            else:
                new_balloons.append(Balloon())
        balloons = new_balloons

        # Iscrtaj balone
        for b in balloons:
            draw_balloon(frame, b)

        # Ažuriraj i iscrtaj čestice
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)
            else:
                cv2.circle(frame, (int(p["x"]), int(p["y"])), int(p["size"]), p["color"], -1, cv2.LINE_AA)

        # Header - Zvezdice i rezultat
        cv2.rectangle(frame, (10, 10), (220, 60), (30, 30, 40), -1)
        cv2.rectangle(frame, (10, 10), (220, 60), (0, 215, 255), 2)
        cv2.putText(frame, f"BODOVI: {score}", (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)

        # Prikaz na ekranu
        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            balloons = [Balloon() for _ in range(6)]
            particles.clear()
            score = 0
        elif key == ord('m'):
            sound_enabled = not sound_enabled

finally:
    vision.stop()
    cv2.destroyAllWindows()
    print("[INFO] Igra baloni završena.")
