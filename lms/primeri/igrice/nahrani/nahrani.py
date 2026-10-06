#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
             🐰 NAHRANI GLADNE ŽIVOTINJE — PREDŠKOLCI
================================================================================
Opis:
  Ultra-brza igra gde deca prstićima (štipanjem/hvatanjem) hrane životinje.
  Asinhrona obrada slike i MediaPipe-a za 40+ FPS i prirodne boje.
  Prilagođeno deci: velike ikone, animacije žvakanja, veseli zvuci.

Kontrole:
  - [Spoj palac i kažiprst] Uhvati hranu
  - [Prevuc u usta] Životinja otvara usta i jede!
  - [n] Sledeća životinja
  - [m] Zvuk uključivanje/isključivanje
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
snd_nom = None
snd_grab = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def make_nom_sound():
        sr = 44100
        d = 0.12
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        f = np.linspace(350, 650, n)
        wave = np.sin(2 * np.pi * f * t) * 0.35
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_grab_sound():
        sr = 44100
        d = 0.05
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        wave = np.sin(2 * np.pi * 550 * t) * 0.20
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    snd_nom = make_nom_sound()
    snd_grab = make_grab_sound()
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
WINDOW_NAME = "Nahrani Zivotinje - Predskolci"

# Asinhroni vid i kamera za maksimalan FPS i prirodne boje
class FastVisionNahrani:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.use_picam2 = False
        self.latest_frame = None
        self.hand_x = -1
        self.hand_y = -1
        self.is_pinching = False
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

            hx, hy = -1, -1
            pinching = False

            if results.multi_hand_landmarks:
                hlm = results.multi_hand_landmarks[0]
                lm8 = hlm.landmark[8]
                lm4 = hlm.landmark[4]
                hx = int(((lm8.x + lm4.x) / 2.0) * self.width)
                hy = int(((lm8.y + lm4.y) / 2.0) * self.height)
                dist = math.hypot((lm8.x - lm4.x) * self.width, (lm8.y - lm4.y) * self.height)
                pinching = (dist < 45)

            with self.lock:
                self.hand_x = hx
                self.hand_y = hy
                self.is_pinching = pinching

            time.sleep(0.002)

    def get_state(self):
        with self.lock:
            if self.latest_frame is not None:
                # 100% prirodne boje - direktan flip
                f = cv2.flip(self.latest_frame, 1)
                return f, self.hand_x, self.hand_y, self.is_pinching
            return None, -1, -1, False

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

vision = FastVisionNahrani(WIDTH, HEIGHT)

ANIMALS = [
    {"type": "ZEKA",    "name": "BELI ZEKA",     "fav_food": "SARGAREPA"},
    {"type": "MAJMUN",  "name": "VESELI MAJMUN", "fav_food": "BANANA"},
    {"type": "MACA",    "name": "CICA MACA",     "fav_food": "RIBA"}
]

current_animal_idx = 0

def draw_food(img, f_type, x, y, size=45):
    cx, cy = int(x), int(y)
    r = size // 2

    if f_type == "SARGAREPA":
        pts = np.array([(cx - r//3, cy - r), (cx + r//3, cy - r), (cx, cy + r)], np.int32)
        cv2.fillPoly(img, [pts], (20, 140, 255), cv2.LINE_AA)
        cv2.circle(img, (cx, cy - r), r//4, (60, 200, 60), -1, cv2.LINE_AA)
        cv2.line(img, (cx, cy - r), (cx, cy - r - 10), (50, 180, 50), 3, cv2.LINE_AA)
    elif f_type == "BANANA":
        cv2.ellipse(img, (cx, cy), (r, r//2), 35, 30, 210, (0, 220, 255), -1, cv2.LINE_AA)
        cv2.ellipse(img, (cx, cy), (r, r//2), 35, 30, 210, (20, 170, 210), 2, cv2.LINE_AA)
        cv2.circle(img, (cx - r//2, cy + r//3), 4, (40, 70, 110), -1, cv2.LINE_AA)
    elif f_type == "RIBA":
        cv2.ellipse(img, (cx, cy), (r, r//2), 0, 0, 360, (230, 140, 50), -1, cv2.LINE_AA)
        pts_tail = np.array([(cx + r//2, cy), (cx + r + 10, cy - r//2), (cx + r + 10, cy + r//2)], np.int32)
        cv2.fillPoly(img, [pts_tail], (230, 140, 50), cv2.LINE_AA)
        cv2.circle(img, (cx - r//2, cy - r//6), 5, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - r//2, cy - r//6), 2, (0, 0, 0), -1, cv2.LINE_AA)

class FoodItem:
    def __init__(self, food_type, home_x, home_y):
        self.food_type = food_type
        self.home_x = home_x
        self.home_y = home_y
        self.x = home_x
        self.y = home_y
        self.radius = 32
        self.is_dragging = False

    def is_inside(self, px, py):
        return math.hypot(self.x - px, self.y - py) < (self.radius + 15)

    def update(self):
        if not self.is_dragging:
            self.x += (self.home_x - self.x) * 0.25
            self.y += (self.home_y - self.y) * 0.25

food_types = ["SARGAREPA", "BANANA", "RIBA"]
food_items = [
    FoodItem(food_types[0], 90, 80),
    FoodItem(food_types[1], 90, 200),
    FoodItem(food_types[2], 90, 320)
]

def draw_big_animal(img, a_type, mouth_open=False, happy=False):
    cx, cy = WIDTH // 2, HEIGHT - 55

    # Telo/Glava
    cv2.circle(img, (cx, cy), 110, (235, 235, 240) if a_type == "ZEKA" else ((40, 100, 180) if a_type == "MAJMUN" else (70, 170, 245)), -1, cv2.LINE_AA)
    cv2.circle(img, (cx, cy), 110, (255, 255, 255), 3, cv2.LINE_AA)

    # Uši
    if a_type == "ZEKA":
        cv2.ellipse(img, (cx - 45, cy - 130), (22, 60), -15, 0, 360, (235, 235, 240), -1, cv2.LINE_AA)
        cv2.ellipse(img, (cx + 45, cy - 130), (22, 60), 15, 0, 360, (235, 235, 240), -1, cv2.LINE_AA)
        cv2.ellipse(img, (cx - 45, cy - 130), (12, 45), -15, 0, 360, (190, 180, 255), -1, cv2.LINE_AA)
        cv2.ellipse(img, (cx + 45, cy - 130), (12, 45), 15, 0, 360, (190, 180, 255), -1, cv2.LINE_AA)
    elif a_type == "MAJMUN":
        cv2.circle(img, (cx - 100, cy - 30), 32, (40, 100, 180), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 100, cy - 30), 32, (40, 100, 180), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - 100, cy - 30), 20, (100, 170, 240), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 100, cy - 30), 20, (100, 170, 240), -1, cv2.LINE_AA)
    elif a_type == "MACA":
        pts_l = np.array([(cx - 90, cy - 40), (cx - 70, cy - 110), (cx - 20, cy - 75)], np.int32)
        pts_r = np.array([(cx + 90, cy - 40), (cx + 70, cy - 110), (cx + 20, cy - 75)], np.int32)
        cv2.fillPoly(img, [pts_l], (70, 170, 245), cv2.LINE_AA)
        cv2.fillPoly(img, [pts_r], (70, 170, 245), cv2.LINE_AA)

    # Oči
    eye_y = cy - 25
    if happy:
        cv2.ellipse(img, (cx - 35, eye_y), (14, 10), 0, 180, 360, (30, 30, 30), 3, cv2.LINE_AA)
        cv2.ellipse(img, (cx + 35, eye_y), (14, 10), 0, 180, 360, (30, 30, 30), 3, cv2.LINE_AA)
    else:
        cv2.circle(img, (cx - 35, eye_y), 14, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 35, eye_y), 14, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - 35, eye_y), 7, (20, 20, 20), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 35, eye_y), 7, (20, 20, 20), -1, cv2.LINE_AA)

    # Obrazi
    cv2.circle(img, (cx - 60, cy + 5), 16, (160, 160, 255), -1, cv2.LINE_AA)
    cv2.circle(img, (cx + 60, cy + 5), 16, (160, 160, 255), -1, cv2.LINE_AA)

    # Usta
    mouth_y = cy + 25
    if mouth_open:
        cv2.ellipse(img, (cx, mouth_y + 10), (32, 28), 0, 0, 360, (30, 30, 180), -1, cv2.LINE_AA)
        cv2.circle(img, (cx, mouth_y + 20), 14, (120, 100, 245), -1, cv2.LINE_AA)
    else:
        cv2.ellipse(img, (cx, mouth_y), (22, 14), 0, 0, 180, (20, 20, 20), 3, cv2.LINE_AA)

dragged_food = None
particles = []
score = 0
happy_timer = 0
auto_switch_time = 0
last_btn_touch = 0

BTN_X, BTN_Y, BTN_W, BTN_H = WIDTH - 165, 70, 155, 42

def switch_next_animal():
    global current_animal_idx, happy_timer, auto_switch_time
    current_animal_idx = (current_animal_idx + 1) % len(ANIMALS)
    happy_timer = 0
    auto_switch_time = 0
    play_sound(snd_grab)

def on_mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if (BTN_X <= x <= BTN_X + BTN_W) and (BTN_Y <= y <= BTN_Y + BTN_H):
            switch_next_animal()

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)
cv2.setMouseCallback(WINDOW_NAME, on_mouse)

print("=" * 60)
print("POKRENUT BRZI 'NAHRANI GLADNE ŽIVOTINJE' (PRIRODNE BOJE & 40+ FPS)")
print("Kako se menja životinja:")
print("  1. Automatski: Čim nahranite životinju, posle 2s dolazi sledeća!")
print("  2. Na ekranu: Dodirnite prstićem ili kliknite dugme 'SLEDECI ->'")
print("  3. Na tastaturi: [n] ili [Razmaknica] (Space) ili [Desna strelica]")
print("Kontrole: [m] Zvuk  |  [q] Izlaz")
print("=" * 60)

try:
    while True:
        frame, cur_x, cur_y, is_pinching = vision.get_state()
        if frame is None:
            time.sleep(0.005)
            continue

        # Automatski prelaz na sledeću životinju nakon što pojede
        if auto_switch_time > 0 and time.time() > auto_switch_time:
            switch_next_animal()

        # Pozadina za životinju
        cv2.circle(frame, (WIDTH // 2, HEIGHT - 50), 130, (50, 40, 35), -1)

        # Dugme na ekranu za prelaz na sledeću životinju
        btn_hovered = cur_x > 0 and (BTN_X <= cur_x <= BTN_X + BTN_W) and (BTN_Y <= cur_y <= BTN_Y + BTN_H)
        btn_bg = (0, 180, 140) if btn_hovered else (40, 35, 50)
        cv2.rectangle(frame, (BTN_X, BTN_Y), (BTN_X + BTN_W, BTN_Y + BTN_H), btn_bg, -1)
        cv2.rectangle(frame, (BTN_X, BTN_Y), (BTN_X + BTN_W, BTN_Y + BTN_H), (0, 235, 255), 2)
        cv2.putText(frame, "SLEDECI >", (BTN_X + 16, BTN_Y + 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        if btn_hovered and (is_pinching or time.time() - last_btn_touch > 1.2):
            switch_next_animal()
            last_btn_touch = time.time()

        # Drag & drop logika
        if is_pinching and not btn_hovered:
            if dragged_food is None and cur_x > 0:
                for f in food_items:
                    if f.is_inside(cur_x, cur_y):
                        dragged_food = f
                        f.is_dragging = True
                        play_sound(snd_grab)
                        break
            elif dragged_food is not None:
                dragged_food.x = cur_x
                dragged_food.y = cur_y
        else:
            if dragged_food is not None:
                mouth_cx, mouth_cy = WIDTH // 2, HEIGHT - 35
                curr_animal = ANIMALS[current_animal_idx]
                if math.hypot(dragged_food.x - mouth_cx, dragged_food.y - mouth_cy) < 85:
                    if dragged_food.food_type == curr_animal["fav_food"]:
                        play_sound(snd_nom)
                        score += 20
                        happy_timer = time.time() + 2.0
                        auto_switch_time = time.time() + 2.2 # Nakon 2s dolazi sledeća životinja!
                        for _ in range(25):
                            particles.append({
                                "x": mouth_cx,
                                "y": mouth_cy,
                                "vx": random.uniform(-4, 4),
                                "vy": random.uniform(-6, -1),
                                "color": random.choice([(0, 215, 255), (100, 80, 245), (0, 255, 120)]),
                                "size": random.randint(3, 7),
                                "life": random.randint(20, 35)
                            })
                dragged_food.is_dragging = False
                dragged_food = None

        for f in food_items:
            f.update()

        near_mouth = False
        if dragged_food is not None:
            if math.hypot(dragged_food.x - WIDTH // 2, dragged_food.y - (HEIGHT - 35)) < 110:
                near_mouth = True

        is_happy = (time.time() < happy_timer)
        draw_big_animal(frame, ANIMALS[current_animal_idx]["type"], mouth_open=near_mouth, happy=is_happy)

        # Iscrtavanje hrane
        for f in food_items:
            cv2.circle(frame, (int(f.home_x), int(f.home_y)), 38, (45, 35, 30), -1)
            cv2.circle(frame, (int(f.home_x), int(f.home_y)), 38, (90, 70, 60), 2)
            draw_food(frame, f.food_type, f.x, f.y, size=48)

        # Čestice slavlja
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.22
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)
            else:
                cv2.circle(frame, (int(p["x"]), int(p["y"])), p["size"], p["color"], -1, cv2.LINE_AA)

        # Kursor šake
        if cur_x > 0:
            col = (0, 245, 255) if is_pinching else (255, 255, 255)
            cv2.circle(frame, (cur_x, cur_y), 14, col, 2, cv2.LINE_AA)
            cv2.circle(frame, (cur_x, cur_y), 6, col, -1, cv2.LINE_AA)

        # Oblačić kada je srećan
        if is_happy:
            cv2.rectangle(frame, (WIDTH // 2 - 160, HEIGHT - 180), (WIDTH // 2 + 160, HEIGHT - 135), (20, 120, 50), -1)
            cv2.rectangle(frame, (WIDTH // 2 - 160, HEIGHT - 180), (WIDTH // 2 + 160, HEIGHT - 135), (0, 255, 180), 2)
            cv2.putText(frame, "NJAM! HVALA! (+20)", (WIDTH // 2 - 135, HEIGHT - 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

        # Header
        cv2.rectangle(frame, (WIDTH - 210, 10), (WIDTH - 10, 55), (30, 30, 40), -1)
        cv2.rectangle(frame, (WIDTH - 210, 10), (WIDTH - 10, 55), (0, 215, 255), 2)
        cv2.putText(frame, f"BODOVI: {score}", (WIDTH - 195, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key in [ord('n'), ord(' '), 13, 83]: # 'n', space, enter, desna strelica
            switch_next_animal()
        elif key in [ord('p'), 81]:               # 'p', leva strelica
            current_animal_idx = (current_animal_idx - 1) % len(ANIMALS)
            play_sound(snd_grab)
        elif key == ord('m'):
            sound_enabled = not sound_enabled

finally:
    vision.stop()
    cv2.destroyAllWindows()
    print("[INFO] Igra nahrani završena.")
