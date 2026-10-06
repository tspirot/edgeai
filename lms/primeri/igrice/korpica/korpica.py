#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
             🧺 ČAROBNA KORPICA (CATCH THE STARS) — PREDŠKOLCI
================================================================================
Opis:
  Ultra-brza igra hvatanja zvezdica i voćkica u korpicu pomeranjem šake.
  Asinhrona obrada slike i MediaPipe-a za 40+ FPS i prirodne boje.
  Prilagođeno deci: krupni svetleći objekti, veseli zvuci i konfete.

Kontrole:
  - [Pomeraj šaku levo-desno] Korpica prati pokret šake
  - [r] Resetuj rezultat
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

# Audio sistem
sound_enabled = True
snd_catch = None
snd_celebrate = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def make_catch():
        sr = 44100
        d = 0.09
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        f = np.linspace(480, 880, n)
        env = np.exp(-5.0 * t / d)
        wave = np.sin(2 * np.pi * f * t) * env * 0.30
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_celebrate():
        sr = 44100
        notes = [523, 659, 784, 1046]
        d = 0.08
        n = int(sr * d)
        chunks = []
        for f in notes:
            t = np.linspace(0, d, n, False)
            env = np.exp(-3.5 * t / d)
            chunks.append(np.sin(2 * np.pi * f * t) * env * 0.25)
        full = np.concatenate(chunks)
        audio = (full * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    snd_catch = make_catch()
    snd_celebrate = make_celebrate()
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
WINDOW_NAME = "Carobna Korpica - Predskolci"

class FastVisionBasket:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.use_picam2 = False
        self.latest_frame = None
        self.target_x = width // 2
        self.hand_detected = False
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

            tx = self.width // 2
            detected = False

            if results.multi_hand_landmarks:
                hlm = results.multi_hand_landmarks[0]
                # Dlan / centar šake (landmark 9)
                lm = hlm.landmark[9]
                tx = int(lm.x * self.width)
                detected = True

            with self.lock:
                if detected:
                    self.target_x = tx
                    self.hand_detected = True
                else:
                    self.hand_detected = False

            time.sleep(0.002)

    def get_state(self):
        with self.lock:
            if self.latest_frame is not None:
                f = cv2.flip(self.latest_frame, 1)
                return f, self.target_x, self.hand_detected
            return None, self.width // 2, False

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

vision = FastVisionBasket(WIDTH, HEIGHT)

BASKET_W = 120
BASKET_H = 50
BASKET_Y = HEIGHT - 65

class FallingItem:
    def __init__(self):
        self.item_type = random.choice(["ZVEZDA", "ZVEZDA", "JABUKA", "POKLON"])
        self.x = random.randint(40, WIDTH - 40)
        self.y = random.randint(-80, -20)
        self.speed_y = random.uniform(2.5, 4.2)
        self.size = random.randint(34, 44)
        self.is_caught = False

    def update(self):
        self.y += self.speed_y

def draw_basket(img, x, y, w, h):
    pts = np.array([
        (x - w // 2, y),
        (x + w // 2, y),
        (x + w // 2 - 15, y + h),
        (x - w // 2 + 15, y + h)
    ], np.int32)
    cv2.fillPoly(img, [pts], (30, 95, 175), cv2.LINE_AA)
    cv2.polylines(img, [pts], True, (60, 160, 240), 3, cv2.LINE_AA)
    # Drška
    cv2.ellipse(img, (x, y), (w // 2 - 10, h), 0, 180, 360, (60, 160, 240), 4, cv2.LINE_AA)

def draw_item(img, item):
    cx, cy, s = int(item.x), int(item.y), item.size
    r = s // 2
    if item.item_type == "ZVEZDA":
        pts = []
        for i in range(10):
            ang = math.radians(i * 36 - 90)
            rad = r if i % 2 == 0 else r * 0.45
            pts.append((cx + int(rad * math.cos(ang)), cy + int(rad * math.sin(ang))))
        cv2.fillPoly(img, [np.array(pts, np.int32)], (0, 235, 255), cv2.LINE_AA)
        cv2.polylines(img, [np.array(pts, np.int32)], True, (255, 255, 255), 2, cv2.LINE_AA)
    elif item.item_type == "JABUKA":
        cv2.circle(img, (cx, cy), r, (40, 50, 240), -1, cv2.LINE_AA)
        cv2.circle(img, (cx, cy), r, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(img, (cx - r//3, cy - r//3), r//4, (120, 140, 255), -1, cv2.LINE_AA)
        cv2.line(img, (cx, cy - r), (cx + 5, cy - r - 8), (40, 120, 40), 3, cv2.LINE_AA)
    elif item.item_type == "POKLON":
        cv2.rectangle(img, (cx - r, cy - r), (cx + r, cy + r), (210, 70, 180), -1)
        cv2.rectangle(img, (cx - r, cy - r), (cx + r, cy + r), (255, 255, 255), 2)
        cv2.line(img, (cx, cy - r), (cx, cy + r), (0, 240, 255), 3)
        cv2.line(img, (cx - r, cy), (cx + r, cy), (0, 240, 255), 3)

items = [FallingItem() for _ in range(4)]
particles = []
score = 0
basket_x = WIDTH // 2

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("=" * 60)
print("POKRENUTA BRZA 'ČAROBNA KORPICA' (PRIRODNE BOJE & 40+ FPS)")
print("Pomerajte ruku levo-desno za hvatanje zvezdica!")
print("Kontrole: [r] Reset  |  [m] Zvuk  |  [q] Izlaz")
print("=" * 60)

try:
    while True:
        frame, target_x, hand_detected = vision.get_state()
        if frame is None:
            time.sleep(0.005)
            continue

        # Glatko praćenje korpice (LERP)
        basket_x += (target_x - basket_x) * 0.28
        basket_x = max(BASKET_W // 2, min(WIDTH - BASKET_W // 2, basket_x))

        # Ažuriraj padajuće objekte
        for it in items:
            it.update()

            # Provera hvatanja u korpicu
            if not it.is_caught:
                if (BASKET_Y - 15) <= it.y <= (BASKET_Y + 25):
                    if abs(it.x - basket_x) < (BASKET_W // 2 + 10):
                        it.is_caught = True
                        score += 15
                        play_sound(snd_catch)

                        for _ in range(20):
                            particles.append({
                                "x": it.x,
                                "y": BASKET_Y,
                                "vx": random.uniform(-5, 5),
                                "vy": random.uniform(-6, -1),
                                "color": random.choice([(0, 240, 255), (255, 255, 255), (50, 210, 90)]),
                                "size": random.randint(3, 7),
                                "life": random.randint(15, 30)
                            })

        # Zameniti uhvaćene ili objekte koji su pali na dno
        new_items = []
        for it in items:
            if not it.is_caught and it.y < HEIGHT + 40:
                new_items.append(it)
            else:
                new_items.append(FallingItem())
        items = new_items

        # Iscrtaj predmete
        for it in items:
            draw_item(frame, it)

        # Iscrtaj korpicu
        draw_basket(frame, int(basket_x), BASKET_Y, BASKET_W, BASKET_H)

        # Čestice
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.22
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)
            else:
                cv2.circle(frame, (int(p["x"]), int(p["y"])), p["size"], p["color"], -1, cv2.LINE_AA)

        # Indikator ruke
        if hand_detected:
            cv2.circle(frame, (int(basket_x), BASKET_Y + BASKET_H + 12), 6, (0, 240, 255), -1, cv2.LINE_AA)

        # Header bodovi
        cv2.rectangle(frame, (10, 10), (220, 55), (30, 30, 40), -1)
        cv2.rectangle(frame, (10, 10), (220, 55), (0, 215, 255), 2)
        cv2.putText(frame, f"BODOVI: {score}", (20, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.80, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            score = 0
            items = [FallingItem() for _ in range(4)]
            particles.clear()
        elif key == ord('m'):
            sound_enabled = not sound_enabled

finally:
    vision.stop()
    cv2.destroyAllWindows()
    print("[INFO] Igra korpica završena.")
