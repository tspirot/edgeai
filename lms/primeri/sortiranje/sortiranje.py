#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
          AI DEČIJA IGRA SPAJANJA SLIČICA RUKOM U VAZDUHU (PREDŠKOLCI)
                         Raspberry Pi 5 (sortiranje)
================================================================================
Opis:
  Edukativna interaktivna igra spajanja sličica i oblika prilagođena deci
  predškolskog uzrasta (koja još uvek ne znaju da čitaju).
  Igra se pokretima šake u vazduhu (Air Gesture Pinch & Drag) preko kamere:
  - Spajanje palca i kažiprsta (Pinch): Uhvati sličicu u vazduhu.
  - Otvaranje prstiju: Spusti sličicu u odgovarajuće polje sa istom slikom.
  - Sadrži vizuelne siluete/duhove u kućicama tako da dete odmah prepoznaje
    gde koja sličica pripada!

Teme nivoa:
  1. Oblici i Nebo (Srce, Zvezda, Sunce, Mesec)
  2. Vesele Životinje (Maca, Kuca, Zeka, Ribica)
  3. Slatko Voće (Jabuka, Banana, Jagoda, Grožđe)
  4. Igračke i Vozila (Autić, Lopta, Raketa, Poklon)
  5. Brojanje Balona (1, 2, 3, 4 šarena balona)

Kontrole (za vaspitače / roditelje):
  - [Pinch prstima] Hvatanje i prevlačenje sličice
  - [r] Resetuj trenutni nivo
  - [n] Sledeći nivo
  - [p] Prethodni nivo
  - [c] Uključi / isključi kameru u pozadini (dete vidi sebe)
  - [m] Uključi / isključi zvuk (Mute)
  - [q] ili [ESC] Izlaz iz igre
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

# Inicijalizacija zvuka preko pygame (sintetisani zvučni efekti bez spoljnih fajlova)
sound_enabled = True
snd_grab = None
snd_snap = None
snd_win = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def synthesize_chime(freqs, durations, volume=0.22):
        sr = 44100
        chunks = []
        for f, d in zip(freqs, durations):
            n = int(sr * d)
            t = np.linspace(0, d, n, False)
            env = np.exp(-3.5 * t / d)
            wave = np.sin(2 * np.pi * f * t) * env * volume
            chunks.append(wave)
        full = np.concatenate(chunks)
        audio = (full * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    snd_grab = synthesize_chime([440, 587], [0.06, 0.08], volume=0.20)
    snd_snap = synthesize_chime([523, 659], [0.08, 0.12], volume=0.25)
    snd_win  = synthesize_chime([523, 659, 784, 1046], [0.12, 0.12, 0.16, 0.35], volume=0.30)
    print("[INFO] Zvučni sistem (Pygame Mixer) uspešno inicijalizovan.")
except Exception as e:
    print(f"[UPOZORENJE] Audio sistem nije dostupan ({e}), igra radi bez zvuka.")
    sound_enabled = False

def play_sound(snd):
    global sound_enabled
    if sound_enabled and snd is not None:
        try:
            snd.play()
        except Exception:
            pass

# Asinhroni vid i kamera za maksimalan FPS i prirodne boje (Zero Latency)
class FastVisionHands:
    def __init__(self, cam_w=640, cam_h=480, out_w=1280, out_h=720):
        self.cam_w = cam_w
        self.cam_h = cam_h
        self.out_w = out_w
        self.out_h = out_h
        self.use_picam2 = False
        self.latest_frame = None
        self.detected_hands = []
        self.lock = threading.Lock()
        self.running = True

        try:
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"format": "RGB888", "size": (cam_w, cam_h)}
            )
            self.picam2.configure(config)
            self.picam2.start()
            self.use_picam2 = True
            print("[INFO] Picamera2 aktivirana sa prirodnim bojama.")
        except Exception as e:
            print(f"[INFO] OpenCV VideoCapture fallback: {e}")
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)

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

            frame_flipped = cv2.flip(frame_to_process, 1)
            rgb = cv2.cvtColor(frame_flipped, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            hands_list = []
            if results.multi_hand_landmarks:
                for hlms in results.multi_hand_landmarks:
                    pts = [(int(lm.x * self.out_w), int(lm.y * self.out_h)) for lm in hlms.landmark]
                    hands_list.append(pts)

            with self.lock:
                self.detected_hands = hands_list

            time.sleep(0.002)

    def get_state(self):
        with self.lock:
            if self.latest_frame is not None:
                f = cv2.flip(self.latest_frame, 1)
                h_pts = [list(pts) for pts in self.detected_hands]
                return f, h_pts
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

vision = FastVisionHands(cam_w=640, cam_h=480, out_w=1280, out_h=720)

# Dimenzije ekrana (1280x720 HD format za TV / monitor)
CANVAS_W = 1280
CANVAS_H = 720

# Boje (BGR format za OpenCV)
COLOR_BG_DARK = (42, 22, 28)         # Topla tamno-ljubičasta svemirska noć
COLOR_BG_GRAD = (70, 36, 48)         # Topliji centar gradijenta
COLOR_CARD_BG = (65, 45, 40)         # Mekana podloga kartice
COLOR_CARD_BORDER = (245, 215, 120)  # Zlatna ivica
COLOR_CARD_DRAG = (0, 245, 255)      # Neon žuta kad je dete drži
COLOR_SLOT_BG = (45, 30, 30)         # Kućica podloga
COLOR_SLOT_BORDER = (160, 130, 110)  # Diskretna ivica kućice
COLOR_SLOT_ACTIVE = (0, 255, 220)    # Kad se sličica nadvije
COLOR_SLOT_MATCH = (0, 240, 130)     # Kad se sličica tačno spoji
COLOR_HAND_1 = (255, 220, 60)        # Ruka 1 (Cyan)
COLOR_HAND_2 = (60, 215, 255)        # Ruka 2 (Zlatno-narandžasta)
COLOR_TEXT_WHITE = (250, 250, 250)
COLOR_TEXT_GOLD = (90, 225, 255)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (0, 9), (9, 10), (10, 11), (11, 12),
    (0, 13), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20),
    (5, 9), (9, 13), (13, 17)
]

# ================= POMOĆNE GRAFIČKE FUNKCIJE =================

def draw_rounded_rect(img, x, y, w, h, radius, color, thickness=-1):
    """Crta pravougaonik sa lepim zaobljenim uglovima."""
    x, y, w, h, radius = int(x), int(y), int(w), int(h), int(radius)
    radius = min(radius, w // 2, h // 2)
    if radius <= 0:
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
        return

    if thickness == -1:
        cv2.rectangle(img, (x + radius, y), (x + w - radius, y + h), color, -1)
        cv2.rectangle(img, (x, y + radius), (x + w, y + h - radius), color, -1)
        cv2.circle(img, (x + radius, y + radius), radius, color, -1)
        cv2.circle(img, (x + w - radius, y + radius), radius, color, -1)
        cv2.circle(img, (x + radius, y + h - radius), radius, color, -1)
        cv2.circle(img, (x + w - radius, y + h - radius), radius, color, -1)
    else:
        cv2.line(img, (x + radius, y), (x + w - radius, y), color, thickness, cv2.LINE_AA)
        cv2.line(img, (x + radius, y + h), (x + w - radius, y + h), color, thickness, cv2.LINE_AA)
        cv2.line(img, (x, y + radius), (x, y + h - radius), color, thickness, cv2.LINE_AA)
        cv2.line(img, (x + w, y + radius), (x + w, y + h - radius), color, thickness, cv2.LINE_AA)

        cv2.ellipse(img, (x + radius, y + radius), (radius, radius), 180, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(img, (x + w - radius, y + radius), (radius, radius), 270, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(img, (x + radius, y + h - radius), (radius, radius), 90, 0, 90, color, thickness, cv2.LINE_AA)
        cv2.ellipse(img, (x + w - radius, y + h - radius), (radius, radius), 0, 0, 90, color, thickness, cv2.LINE_AA)

def draw_dashed_rounded_rect(img, x, y, w, h, radius, color, thickness=2, dash_len=12):
    """Crta isprekidane zaobljene kućice za sličice."""
    x, y, w, h, radius = int(x), int(y), int(w), int(h), int(radius)
    for i in range(x + radius, x + w - radius, dash_len * 2):
        end = min(i + dash_len, x + w - radius)
        cv2.line(img, (i, y), (end, y), color, thickness, cv2.LINE_AA)
        cv2.line(img, (i, y + h), (end, y + h), color, thickness, cv2.LINE_AA)
    for j in range(y + radius, y + h - radius, dash_len * 2):
        end = min(j + dash_len, y + h - radius)
        cv2.line(img, (x, j), (x, end), color, thickness, cv2.LINE_AA)
        cv2.line(img, (x + w, j), (x + w, end), color, thickness, cv2.LINE_AA)

    cv2.ellipse(img, (x + radius, y + radius), (radius, radius), 180, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + w - radius, y + radius), (radius, radius), 270, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + radius, y + h - radius), (radius, radius), 90, 0, 90, color, thickness, cv2.LINE_AA)
    cv2.ellipse(img, (x + w - radius, y + h - radius), (radius, radius), 0, 0, 90, color, thickness, cv2.LINE_AA)

# ================= DEČIJE VEKTORSKE SLIČICE =================

def draw_srce(img, cx, cy, size=65, ghost=False):
    """Crveno / roze slatko srce sa sjajem."""
    col = (100, 70, 180) if ghost else (90, 80, 245)
    r = int(size * 0.38)
    cv2.circle(img, (cx - r + 3, cy - 6), r, col, -1, cv2.LINE_AA)
    cv2.circle(img, (cx + r - 3, cy - 6), r, col, -1, cv2.LINE_AA)
    tri = np.array([(cx - int(r * 1.95), cy - 3), (cx + int(r * 1.95), cy - 3), (cx, cy + int(size * 0.55))], np.int32)
    cv2.fillPoly(img, [tri], col, cv2.LINE_AA)
    if not ghost:
        # Beli odsjaj
        cv2.ellipse(img, (cx - r + 1, cy - 10), (int(r * 0.45), int(r * 0.25)), -30, 0, 360, (255, 230, 240), -1, cv2.LINE_AA)

def draw_zvezda(img, cx, cy, size=70, ghost=False):
    """Zlatna sjajna zvezda petokraka."""
    col = (50, 150, 180) if ghost else (0, 215, 255)
    pts = []
    r_outer = size // 2
    r_inner = int(r_outer * 0.45)
    for i in range(10):
        ang = math.radians(i * 36 - 90)
        rad = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + int(rad * math.cos(ang)), cy + int(rad * math.sin(ang))))
    cv2.fillPoly(img, [np.array(pts, np.int32)], col, cv2.LINE_AA)
    if not ghost:
        cv2.circle(img, (cx, cy), 6, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - 7, cy - 2), 2, (30, 30, 30), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 7, cy - 2), 2, (30, 30, 30), -1, cv2.LINE_AA)

def draw_sunce(img, cx, cy, size=70, ghost=False):
    """Veselo žuto sunce sa toplim zracima."""
    col = (30, 140, 180) if ghost else (0, 215, 255)
    r = size // 3
    # Zzraci
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        x1 = cx + int((r + 4) * math.cos(rad))
        y1 = cy + int((r + 4) * math.sin(rad))
        x2 = cx + int((r + 14) * math.cos(rad))
        y2 = cy + int((r + 14) * math.sin(rad))
        cv2.line(img, (x1, y1), (x2, y2), col, 4 if not ghost else 2, cv2.LINE_AA)
    cv2.circle(img, (cx, cy), r, col, -1, cv2.LINE_AA)
    if not ghost:
        # Smešak i okice
        cv2.circle(img, (cx - 7, cy - 4), 3, (20, 20, 20), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 7, cy - 4), 3, (20, 20, 20), -1, cv2.LINE_AA)
        cv2.ellipse(img, (cx, cy + 5), (8, 6), 0, 0, 180, (20, 20, 20), 2, cv2.LINE_AA)
        # Obrazi
        cv2.circle(img, (cx - 13, cy + 4), 4, (100, 120, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 13, cy + 4), 4, (100, 120, 255), -1, cv2.LINE_AA)

def draw_mesec(img, cx, cy, size=70, ghost=False):
    """Zlatno-beli polumesec."""
    col = (130, 130, 140) if ghost else (240, 235, 170)
    bg_cut = COLOR_SLOT_BG if ghost else COLOR_CARD_BG
    r = size // 2 - 4
    cv2.circle(img, (cx, cy), r, col, -1, cv2.LINE_AA)
    cv2.circle(img, (cx + int(r * 0.55), cy - int(r * 0.35)), int(r * 0.88), bg_cut, -1, cv2.LINE_AA)
    if not ghost:
        # Mala zvezdica pored meseca
        cv2.circle(img, (cx + 18, cy + 12), 4, (0, 220, 255), -1, cv2.LINE_AA)

def draw_macka(img, cx, cy, size=70, ghost=False):
    """Narandžasta cica-maca."""
    col = (50, 110, 160) if ghost else (0, 165, 255)
    r = size // 2 - 4
    cv2.circle(img, (cx, cy + 4), int(r * 0.8), col, -1, cv2.LINE_AA)
    # Uši
    pts_l = np.array([(cx - r + 4, cy - 2), (cx - r + 2, cy - r), (cx - 5, cy - r + 15)], np.int32)
    pts_r = np.array([(cx + r - 4, cy - 2), (cx + r - 2, cy - r), (cx + 5, cy - r + 15)], np.int32)
    cv2.fillPoly(img, [pts_l, pts_r], col, cv2.LINE_AA)
    if not ghost:
        # Unutrašnjost ušiju
        pts_il = np.array([(cx - r + 10, cy - 2), (cx - r + 6, cy - r + 10), (cx - 10, cy - r + 18)], np.int32)
        pts_ir = np.array([(cx + r - 10, cy - 2), (cx + r - 6, cy - r + 10), (cx + 10, cy - r + 18)], np.int32)
        cv2.fillPoly(img, [pts_il, pts_ir], (180, 150, 255), cv2.LINE_AA)
        # Oči
        cv2.circle(img, (cx - 11, cy - 2), 5, (30, 30, 30), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 11, cy - 2), 5, (30, 30, 30), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - 9, cy - 4), 2, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 13, cy - 4), 2, (255, 255, 255), -1, cv2.LINE_AA)
        # Nosić i brkovi
        cv2.circle(img, (cx, cy + 7), 3, (180, 100, 255), -1, cv2.LINE_AA)
        cv2.line(img, (cx - 15, cy + 6), (cx - 32, cy + 4), (50, 50, 50), 2, cv2.LINE_AA)
        cv2.line(img, (cx - 15, cy + 11), (cx - 31, cy + 14), (50, 50, 50), 2, cv2.LINE_AA)
        cv2.line(img, (cx + 15, cy + 6), (cx + 32, cy + 4), (50, 50, 50), 2, cv2.LINE_AA)
        cv2.line(img, (cx + 15, cy + 11), (cx + 31, cy + 14), (50, 50, 50), 2, cv2.LINE_AA)

def draw_kuca(img, cx, cy, size=70, ghost=False):
    """Veseli kuca sa spuštenim ušima."""
    col = (70, 90, 120) if ghost else (70, 130, 180)
    r = size // 2 - 4
    cv2.circle(img, (cx, cy + 4), int(r * 0.82), col, -1, cv2.LINE_AA)
    # Spuštene uši
    ear_col = (50, 70, 95) if ghost else (50, 95, 140)
    cv2.ellipse(img, (cx - int(r*0.75), cy - 2), (10, 22), -25, 0, 360, ear_col, -1, cv2.LINE_AA)
    cv2.ellipse(img, (cx + int(r*0.75), cy - 2), (10, 22), 25, 0, 360, ear_col, -1, cv2.LINE_AA)
    if not ghost:
        # Njuškica
        cv2.ellipse(img, (cx, cy + 12), (16, 12), 0, 0, 360, (230, 240, 245), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - 11, cy - 2), 4, (25, 25, 25), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 11, cy - 2), 4, (25, 25, 25), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - 9, cy - 4), 2, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 13, cy - 4), 2, (255, 255, 255), -1, cv2.LINE_AA)
        # Nosić
        cv2.ellipse(img, (cx, cy + 8), (6, 4), 0, 0, 360, (30, 30, 30), -1, cv2.LINE_AA)
        # Jezik
        cv2.ellipse(img, (cx, cy + 20), (5, 8), 0, 0, 180, (130, 100, 255), -1, cv2.LINE_AA)

def draw_zeka(img, cx, cy, size=70, ghost=False):
    """Beli zeka sa velikim ušima."""
    col = (130, 130, 140) if ghost else (240, 240, 245)
    r = size // 2 - 4
    # Velike uspravne uši
    cv2.ellipse(img, (cx - 13, cy - int(r*0.8)), (9, 25), -10, 0, 360, col, -1, cv2.LINE_AA)
    cv2.ellipse(img, (cx + 13, cy - int(r*0.8)), (9, 25), 10, 0, 360, col, -1, cv2.LINE_AA)
    if not ghost:
        cv2.ellipse(img, (cx - 13, cy - int(r*0.8)), (4, 18), -10, 0, 360, (190, 180, 255), -1, cv2.LINE_AA)
        cv2.ellipse(img, (cx + 13, cy - int(r*0.8)), (4, 18), 10, 0, 360, (190, 180, 255), -1, cv2.LINE_AA)
    # Glava
    cv2.circle(img, (cx, cy + 8), int(r * 0.75), col, -1, cv2.LINE_AA)
    if not ghost:
        # Obrazi i okice
        cv2.circle(img, (cx - 14, cy + 13), 5, (200, 200, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 14, cy + 13), 5, (200, 200, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - 9, cy + 4), 4, (40, 40, 40), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 9, cy + 4), 4, (40, 40, 40), -1, cv2.LINE_AA)
        # Nosić
        pts_n = np.array([(cx - 3, cy + 10), (cx + 3, cy + 10), (cx, cy + 14)], np.int32)
        cv2.fillPoly(img, [pts_n], (160, 130, 255), cv2.LINE_AA)

def draw_ribica(img, cx, cy, size=70, ghost=False):
    """Zlatna ribica sa perajima."""
    col = (40, 90, 150) if ghost else (0, 140, 255)
    r = size // 2 - 4
    cv2.ellipse(img, (cx - 4, cy), (int(r * 0.7), int(r * 0.48)), 0, 0, 360, col, -1, cv2.LINE_AA)
    # Rep
    tail_col = (30, 80, 140) if ghost else (0, 120, 240)
    pts_tail = np.array([(cx + int(r * 0.48), cy), (cx + r + 6, cy - 16), (cx + r + 2, cy), (cx + r + 6, cy + 16)], np.int32)
    cv2.fillPoly(img, [pts_tail], tail_col, cv2.LINE_AA)
    if not ghost:
        # Oko
        cv2.circle(img, (cx - int(r*0.35), cy - 4), 5, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(img, (cx - int(r*0.35), cy - 4), 3, (20, 20, 20), -1, cv2.LINE_AA)
        # Mehurići
        cv2.circle(img, (cx - r - 5, cy - 10), 3, (240, 220, 120), 1, cv2.LINE_AA)
        cv2.circle(img, (cx - r - 13, cy - 18), 5, (240, 220, 120), 1, cv2.LINE_AA)

def draw_jabuka(img, cx, cy, size=70, ghost=False):
    """Crvena sočna jabuka sa listom."""
    col = (50, 50, 140) if ghost else (35, 45, 235)
    r = size // 2 - 4
    cv2.circle(img, (cx - 9, cy + 2), int(r * 0.65), col, -1, cv2.LINE_AA)
    cv2.circle(img, (cx + 9, cy + 2), int(r * 0.65), col, -1, cv2.LINE_AA)
    if not ghost:
        cv2.ellipse(img, (cx - 12, cy - 4), (5, 10), -25, 0, 360, (100, 110, 255), -1, cv2.LINE_AA)
        # Peteljka i list
        cv2.line(img, (cx, cy - 16), (cx + 3, cy - int(r * 0.85)), (40, 70, 110), 3, cv2.LINE_AA)
        cv2.ellipse(img, (cx + 12, cy - int(r * 0.72)), (10, 5), 25, 0, 360, (50, 190, 50), -1, cv2.LINE_AA)

def draw_banana(img, cx, cy, size=70, ghost=False):
    """Zakrivljena žuta banana."""
    col = (40, 140, 160) if ghost else (30, 220, 255)
    r = size // 2 - 4
    cv2.ellipse(img, (cx, cy - 4), (int(r * 0.8), int(r * 0.65)), 20, 30, 150, col, 16 if not ghost else 10, cv2.LINE_AA)
    if not ghost:
        cv2.circle(img, (cx - 24, cy - 12), 3, (40, 120, 80), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 22, cy + 16), 3, (40, 70, 110), -1, cv2.LINE_AA)

def draw_jagoda(img, cx, cy, size=70, ghost=False):
    """Slatka crvena jagoda sa kapicom."""
    col = (50, 50, 140) if ghost else (40, 45, 235)
    r = size // 2 - 4
    pts_b = np.array([(cx - int(r*0.65), cy - 8), (cx + int(r*0.65), cy - 8), (cx, cy + int(r*0.85))], np.int32)
    cv2.fillPoly(img, [pts_b], col, cv2.LINE_AA)
    cv2.circle(img, (cx - 10, cy - 8), int(r * 0.4), col, -1, cv2.LINE_AA)
    cv2.circle(img, (cx + 10, cy - 8), int(r * 0.4), col, -1, cv2.LINE_AA)
    if not ghost:
        # Tačkice
        for sx, sy in [(-7, -1), (7, -1), (0, 7), (-6, 12), (6, 12), (0, 19)]:
            cv2.circle(img, (cx + sx, cy + sy), 2, (120, 220, 255), -1, cv2.LINE_AA)
        # Zelena kapica
        for lx in [-14, -5, 5, 14]:
            cv2.ellipse(img, (cx + lx, cy - 15), (5, 3), 0, 0, 360, (50, 190, 50), -1, cv2.LINE_AA)

def draw_grozdje(img, cx, cy, size=70, ghost=False):
    """Ljubičasti grozd."""
    col = (100, 50, 90) if ghost else (180, 50, 130)
    pts_grapes = [(-12, -8), (0, -8), (12, -8), (-6, 3), (6, 3), (0, 14)]
    for gx, gy in pts_grapes:
        cv2.circle(img, (cx + gx, cy + gy), 8, col, -1, cv2.LINE_AA)
        if not ghost:
            cv2.circle(img, (cx + gx - 2, cy + gy - 2), 2, (215, 120, 180), -1, cv2.LINE_AA)
    if not ghost:
        cv2.line(img, (cx, cy - 12), (cx, cy - 22), (40, 90, 60), 3, cv2.LINE_AA)
        cv2.ellipse(img, (cx + 7, cy - 18), (8, 4), -20, 0, 360, (60, 180, 60), -1, cv2.LINE_AA)

def draw_auto(img, cx, cy, size=70, ghost=False):
    """Plavi crtani autić."""
    col = (130, 80, 40) if ghost else (225, 75, 35)
    # Telo
    cv2.rectangle(img, (cx - 28, cy - 2), (cx + 28, cy + 16), col, -1)
    # Krov
    pts_roof = np.array([(cx - 20, cy - 2), (cx - 12, cy - 18), (cx + 12, cy - 18), (cx + 20, cy - 2)], np.int32)
    cv2.fillPoly(img, [pts_roof], (240, 130, 70) if not ghost else col, cv2.LINE_AA)
    if not ghost:
        # Prozor
        pts_win = np.array([(cx - 15, cy - 4), (cx - 8, cy - 15), (cx + 8, cy - 15), (cx + 15, cy - 4)], np.int32)
        cv2.fillPoly(img, [pts_win], (245, 245, 230), cv2.LINE_AA)
    # Točkovi
    cv2.circle(img, (cx - 18, cy + 16), 8, (30, 30, 30), -1, cv2.LINE_AA)
    cv2.circle(img, (cx + 18, cy + 16), 8, (30, 30, 30), -1, cv2.LINE_AA)
    if not ghost:
        cv2.circle(img, (cx - 18, cy + 16), 3, (180, 180, 180), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 18, cy + 16), 3, (180, 180, 180), -1, cv2.LINE_AA)
        cv2.circle(img, (cx + 26, cy + 5), 3, (0, 230, 255), -1, cv2.LINE_AA)

def draw_lopta(img, cx, cy, size=70, ghost=False):
    """Šarena dečija lopta."""
    r = size // 2 - 4
    col = (110, 110, 120) if ghost else (245, 245, 245)
    cv2.circle(img, (cx, cy), r, col, -1, cv2.LINE_AA)
    cv2.circle(img, (cx, cy), r, (40, 40, 40), 2, cv2.LINE_AA)
    if not ghost:
        cv2.ellipse(img, (cx, cy), (r, r), 0, -45, 45, (30, 70, 230), -1, cv2.LINE_AA)
        cv2.ellipse(img, (cx, cy), (r, r), 0, 135, 225, (0, 200, 240), -1, cv2.LINE_AA)
        cv2.circle(img, (cx, cy), 6, (240, 180, 30), -1, cv2.LINE_AA)

def draw_raketa(img, cx, cy, size=70, ghost=False):
    """Svemirska raketa."""
    col = (120, 120, 130) if ghost else (240, 240, 245)
    pts_body = np.array([(cx, cy - 28), (cx + 14, cy + 8), (cx - 14, cy + 8)], np.int32)
    cv2.fillPoly(img, [pts_body], col, cv2.LINE_AA)
    # Krilca
    fin_col = (60, 60, 140) if ghost else (40, 40, 230)
    pts_lfin = np.array([(cx - 14, cy), (cx - 24, cy + 15), (cx - 14, cy + 14)], np.int32)
    pts_rfin = np.array([(cx + 14, cy), (cx + 24, cy + 15), (cx + 14, cy + 14)], np.int32)
    cv2.fillPoly(img, [pts_lfin, pts_rfin], fin_col, cv2.LINE_AA)
    if not ghost:
        # Vrh
        pts_nose = np.array([(cx, cy - 28), (cx + 8, cy - 12), (cx - 8, cy - 12)], np.int32)
        cv2.fillPoly(img, [pts_nose], (40, 40, 230), cv2.LINE_AA)
        # Prozorčić
        cv2.circle(img, (cx, cy - 2), 6, (220, 180, 50), -1, cv2.LINE_AA)
        cv2.circle(img, (cx, cy - 2), 3, (250, 250, 250), -1, cv2.LINE_AA)
        # Plamen
        pts_flame = np.array([(cx - 7, cy + 9), (cx, cy + 22), (cx + 7, cy + 9)], np.int32)
        cv2.fillPoly(img, [pts_flame], (0, 140, 255), cv2.LINE_AA)

def draw_poklon(img, cx, cy, size=70, ghost=False):
    """Rođendanski paketić sa mašnom."""
    col = (110, 60, 95) if ghost else (200, 50, 160)
    cv2.rectangle(img, (cx - 22, cy - 10), (cx + 22, cy + 22), col, -1)
    cv2.rectangle(img, (cx - 25, cy - 18), (cx + 25, cy - 8), (220, 70, 180) if not ghost else col, -1)
    if not ghost:
        # Mašna i traka
        cv2.rectangle(img, (cx - 5, cy - 18), (cx + 5, cy + 22), (0, 220, 255), -1)
        cv2.rectangle(img, (cx - 22, cy + 2), (cx + 22, cy + 8), (0, 220, 255), -1)
        cv2.circle(img, (cx - 7, cy - 21), 5, (0, 220, 255), 2, cv2.LINE_AA)
        cv2.circle(img, (cx + 7, cy - 21), 5, (0, 220, 255), 2, cv2.LINE_AA)

def draw_single_balloon(img, bx, by, color, scale=1.0, ghost=False):
    rx, ry = int(13 * scale), int(17 * scale)
    cv2.ellipse(img, (bx, by), (rx, ry), 0, 0, 360, color, -1, cv2.LINE_AA)
    if not ghost:
        cv2.circle(img, (bx - int(4 * scale), by - int(5 * scale)), max(1, int(3 * scale)), (255, 255, 255), -1, cv2.LINE_AA)
        pts_k = np.array([(bx - 3, by + ry), (bx + 3, by + ry), (bx, by + ry + 3)], np.int32)
        cv2.fillPoly(img, [pts_k], color, cv2.LINE_AA)
        cv2.line(img, (bx, by + ry + 3), (bx - 2, by + ry + 15), (200, 200, 200), 1, cv2.LINE_AA)

def draw_baloni(img, cx, cy, count=1, size=70, ghost=False):
    """Crta 1, 2, 3 ili 4 šarena balona za brojanje."""
    c_red   = (50, 50, 130) if ghost else (50, 60, 240)
    c_blue  = (130, 80, 40) if ghost else (0, 200, 240)
    c_green = (40, 110, 60) if ghost else (60, 210, 80)
    c_pink  = (110, 60, 110) if ghost else (220, 70, 190)
    if count == 1:
        draw_single_balloon(img, cx, cy - 4, c_red, 1.45, ghost)
    elif count == 2:
        draw_single_balloon(img, cx - 13, cy - 6, c_red, 1.15, ghost)
        draw_single_balloon(img, cx + 13, cy - 2, c_blue, 1.15, ghost)
    elif count == 3:
        draw_single_balloon(img, cx - 18, cy - 1, c_red, 0.98, ghost)
        draw_single_balloon(img, cx, cy - 12, c_blue, 0.98, ghost)
        draw_single_balloon(img, cx + 18, cy - 1, c_green, 0.98, ghost)
    elif count == 4:
        draw_single_balloon(img, cx - 20, cy - 10, c_red, 0.88, ghost)
        draw_single_balloon(img, cx - 7, cy - 1, c_blue, 0.88, ghost)
        draw_single_balloon(img, cx + 7, cy - 12, c_green, 0.88, ghost)
        draw_single_balloon(img, cx + 20, cy - 3, c_pink, 0.88, ghost)

def draw_kid_icon(img, icon_type, cx, cy, size=70, ghost=False):
    """Univerzalni dispečer za crtanje dečijih sličica."""
    cx, cy = int(cx), int(cy)
    if icon_type == "SRCE":
        draw_srce(img, cx, cy, size, ghost)
    elif icon_type == "ZVEZDA":
        draw_zvezda(img, cx, cy, size, ghost)
    elif icon_type == "SUNCE":
        draw_sunce(img, cx, cy, size, ghost)
    elif icon_type == "MESEC":
        draw_mesec(img, cx, cy, size, ghost)
    elif icon_type == "MACKA":
        draw_macka(img, cx, cy, size, ghost)
    elif icon_type == "KUCA":
        draw_kuca(img, cx, cy, size, ghost)
    elif icon_type == "ZEKA":
        draw_zeka(img, cx, cy, size, ghost)
    elif icon_type == "RIBICA":
        draw_ribica(img, cx, cy, size, ghost)
    elif icon_type == "JABUKA":
        draw_jabuka(img, cx, cy, size, ghost)
    elif icon_type == "BANANA":
        draw_banana(img, cx, cy, size, ghost)
    elif icon_type == "JAGODA":
        draw_jagoda(img, cx, cy, size, ghost)
    elif icon_type == "GROZDJE":
        draw_grozdje(img, cx, cy, size, ghost)
    elif icon_type == "AUTO":
        draw_auto(img, cx, cy, size, ghost)
    elif icon_type == "LOPTA":
        draw_lopta(img, cx, cy, size, ghost)
    elif icon_type == "RAKETA":
        draw_raketa(img, cx, cy, size, ghost)
    elif icon_type == "POKLON":
        draw_poklon(img, cx, cy, size, ghost)
    elif icon_type.startswith("BALON_"):
        cnt = int(icon_type.split("_")[1])
        draw_baloni(img, cx, cy, count=cnt, size=size, ghost=ghost)
    else:
        # Fallback zvezdica
        draw_zvezda(img, cx, cy, size, ghost)

# ================= DEFINICIJA NIVOA ZA PREDŠKOLCE =================

LEVELS = [
    {
        "id": 1,
        "title": "NIVO 1: OBLICI I NEBO",
        "hint": "Spoji iste slicice: Srce, Zvezdu, Sunce i Mesec!",
        "items": [
            {"id": 0, "name": "SRCE",   "icon": "SRCE",   "color": (90, 80, 245),  "correct_slot": 0},
            {"id": 1, "name": "ZVEZDA", "icon": "ZVEZDA", "color": (0, 215, 255),  "correct_slot": 1},
            {"id": 2, "name": "SUNCE",  "icon": "SUNCE",  "color": (0, 200, 255),  "correct_slot": 2},
            {"id": 3, "name": "MESEC",  "icon": "MESEC",  "color": (240, 235, 170), "correct_slot": 3}
        ]
    },
    {
        "id": 2,
        "title": "NIVO 2: VESELI LJUBIMCI",
        "hint": "Stavi svaku zivotinjicu u njenu kucicu!",
        "items": [
            {"id": 0, "name": "MACA",   "icon": "MACKA",  "color": (0, 165, 255),  "correct_slot": 0},
            {"id": 1, "name": "KUCA",   "icon": "KUCA",   "color": (70, 130, 180), "correct_slot": 1},
            {"id": 2, "name": "ZEKA",   "icon": "ZEKA",   "color": (240, 240, 245), "correct_slot": 2},
            {"id": 3, "name": "RIBA",   "icon": "RIBICA", "color": (0, 140, 255),  "correct_slot": 3}
        ]
    },
    {
        "id": 3,
        "title": "NIVO 3: SLATKO VOCE",
        "hint": "Spoji vocice: Jabuku, Bananu, Jagodicu i Grozdje!",
        "items": [
            {"id": 0, "name": "JABUKA",  "icon": "JABUKA",  "color": (35, 45, 235),  "correct_slot": 0},
            {"id": 1, "name": "BANANA",  "icon": "BANANA",  "color": (30, 220, 255), "correct_slot": 1},
            {"id": 2, "name": "JAGODA",  "icon": "JAGODA",  "color": (40, 45, 235),  "correct_slot": 2},
            {"id": 3, "name": "GROZDJE", "icon": "GROZDJE", "color": (180, 50, 130), "correct_slot": 3}
        ]
    },
    {
        "id": 4,
        "title": "NIVO 4: IGRACKE I VOZILA",
        "hint": "Spoji igracke: Autic, Loptu, Raketu i Poklon!",
        "items": [
            {"id": 0, "name": "AUTIC",  "icon": "AUTO",   "color": (225, 75, 35),  "correct_slot": 0},
            {"id": 1, "name": "LOPTA",  "icon": "LOPTA",  "color": (30, 70, 230),  "correct_slot": 1},
            {"id": 2, "name": "RAKETA", "icon": "RAKETA", "color": (240, 240, 245), "correct_slot": 2},
            {"id": 3, "name": "POKLON", "icon": "POKLON", "color": (200, 50, 160), "correct_slot": 3}
        ]
    },
    {
        "id": 5,
        "title": "NIVO 5: BROJANJE BALONA",
        "hint": "Povezi balone: 1, 2, 3 i 4 baloncica!",
        "items": [
            {"id": 0, "name": "1 BALON",  "icon": "BALON_1", "color": (50, 60, 240),  "correct_slot": 0},
            {"id": 1, "name": "2 BALONA", "icon": "BALON_2", "color": (0, 200, 240),  "correct_slot": 1},
            {"id": 2, "name": "3 BALONA", "icon": "BALON_3", "color": (60, 210, 80),  "correct_slot": 2},
            {"id": 3, "name": "4 BALONA", "icon": "BALON_4", "color": (220, 70, 190), "correct_slot": 3}
        ]
    }
]

# Dimenzije i pozicije kartica i kućica
CARD_W = 210
CARD_H = 195
DECK_Y = 115
SLOT_Y = 375

start_slot_x = 135
slot_gap = 265

SLOT_POSITIONS = []
DECK_POSITIONS = []
for i in range(4):
    sx = start_slot_x + i * slot_gap
    SLOT_POSITIONS.append((sx, SLOT_Y))
    DECK_POSITIONS.append((sx, DECK_Y))

class GameCard:
    def __init__(self, item_info, start_x, start_y):
        self.id = item_info["id"]
        self.name = item_info["name"]
        self.icon = item_info["icon"]
        self.theme_color = item_info["color"]
        self.correct_slot = item_info["correct_slot"]

        self.home_x = float(start_x)
        self.home_y = float(start_y)
        self.x = float(start_x)
        self.y = float(start_y)
        self.target_x = float(start_x)
        self.target_y = float(start_y)

        self.is_dragging = False
        self.current_slot = None

    def update_physics(self):
        """Glatko opružno privlačenje kartice na ciljnu poziciju (Lerp)."""
        if not self.is_dragging:
            self.x += (self.target_x - self.x) * 0.30
            self.y += (self.target_y - self.y) * 0.30

    def is_point_inside(self, px, py):
        return (self.x <= px <= self.x + CARD_W) and (self.y <= py <= self.y + CARD_H)

# Stanje igre
current_level_idx = 0
game_score = 0
cards = []
show_camera_bg = False

particles = []
floating_balloons = []
level_solved = False
level_solved_time = 0

def init_level(level_idx):
    """Postavlja i meša sličice na gornjoj polici za novi nivo."""
    global cards, level_solved, particles, floating_balloons
    if 'hand_controllers' in globals():
        for hc in hand_controllers:
            hc.dragged_card = None
            hc.is_pinching = False
    level_data = LEVELS[level_idx]
    level_solved = False
    particles = []
    floating_balloons = []

    # Promešaj kartice tako da nisu odmah u pravom redosledu
    shuffled_items = list(level_data["items"])
    for _ in range(6):
        random.shuffle(shuffled_items)
        if any(item["correct_slot"] != i for i, item in enumerate(shuffled_items)):
            break

    cards = []
    for i, item in enumerate(shuffled_items):
        pos_x, pos_y = DECK_POSITIONS[i]
        c = GameCard(item, pos_x, pos_y)
        cards.append(c)

    print(f"[NIVO] Pokrenut za predškolce: {level_data['title']}")

init_level(current_level_idx)

# Pragovi za dečiji Pinch (prilagođeni manjoj šaci):
PINCH_GRAB_DIST = 68.0       # Lakše hvatanje za male prste (< 68px)
PINCH_RELEASE_DIST = 100.0   # Sprečava slučajno ispadanje (> 100px)
GRACE_FRAMES_LOST = 24       # Do 0.8s zadržavanja u vazduhu ako kamera izgubi ruku

class HandController:
    def __init__(self, hand_id, color, label):
        self.hand_id = hand_id
        self.color = color
        self.label = label

        self.cursor_x = CANVAS_W // 3 if hand_id == 0 else (CANVAS_W * 2) // 3
        self.cursor_y = CANVAS_H // 2
        self.is_pinching = False
        self.dragged_card = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.lost_frames = 999
        self.hand_pts = []
        self.pinch_release_counter = 0

    def update_with_landmarks(self, pts_canvas, all_cards):
        self.hand_pts = pts_canvas
        self.lost_frames = 0

        idx_pt = pts_canvas[8]
        thumb_pt = pts_canvas[4]
        raw_cur_x = (idx_pt[0] + thumb_pt[0]) // 2
        raw_cur_y = (idx_pt[1] + thumb_pt[1]) // 2

        # Glatko filtriranje pokreta kursora (bez podrhtavanja dečije ruke)
        self.cursor_x += int((raw_cur_x - self.cursor_x) * 0.40)
        self.cursor_y += int((raw_cur_y - self.cursor_y) * 0.40)

        pinch_dist = math.hypot(idx_pt[0] - thumb_pt[0], idx_pt[1] - thumb_pt[1])

        if not self.is_pinching:
            if pinch_dist < PINCH_GRAB_DIST:
                self.is_pinching = True
                self.pinch_release_counter = 0
                for c in reversed(all_cards):
                    if not c.is_dragging and c.is_point_inside(self.cursor_x, self.cursor_y):
                        self.dragged_card = c
                        c.is_dragging = True
                        self.drag_offset_x = self.cursor_x - c.x
                        self.drag_offset_y = self.cursor_y - c.y
                        c.current_slot = None
                        play_sound(snd_grab)
                        break
        else:
            if pinch_dist > PINCH_RELEASE_DIST:
                self.pinch_release_counter += 1
                if self.pinch_release_counter >= 2:
                    self.is_pinching = False
                    self.pinch_release_counter = 0
                    if self.dragged_card is not None:
                        self.release_card(all_cards)
            else:
                self.pinch_release_counter = 0

        if self.dragged_card is not None:
            self.dragged_card.x = self.cursor_x - self.drag_offset_x
            self.dragged_card.y = self.cursor_y - self.drag_offset_y
            self.dragged_card.target_x = self.dragged_card.x
            self.dragged_card.target_y = self.dragged_card.y

    def handle_lost_frame(self, all_cards):
        self.lost_frames += 1
        self.hand_pts = []
        if self.dragged_card is not None:
            if self.lost_frames <= GRACE_FRAMES_LOST:
                self.dragged_card.is_dragging = True
            else:
                self.is_pinching = False
                self.release_card(all_cards)
        else:
            self.is_pinching = False

    def release_card(self, all_cards):
        if self.dragged_card is None:
            return
        c = self.dragged_card
        c.is_dragging = False

        card_cx = c.x + CARD_W // 2
        card_cy = c.y + CARD_H // 2
        placed_in_slot = None

        for s_idx, (sx, sy) in enumerate(SLOT_POSITIONS):
            slot_cx = sx + CARD_W // 2
            slot_cy = sy + CARD_H // 2
            if math.hypot(card_cx - slot_cx, card_cy - slot_cy) < 140:
                placed_in_slot = s_idx
                break

        if placed_in_slot is not None:
            # Oslobodi kućicu ako je druga sličica već unutra
            for other_c in all_cards:
                if other_c != c and other_c.current_slot == placed_in_slot:
                    other_c.current_slot = None
                    other_c.target_x = other_c.home_x
                    other_c.target_y = other_c.home_y
            c.current_slot = placed_in_slot
            c.target_x = SLOT_POSITIONS[placed_in_slot][0]
            c.target_y = SLOT_POSITIONS[placed_in_slot][1]
            play_sound(snd_snap)
        else:
            # Vrati sličicu nazad na gornju policu
            c.current_slot = None
            c.target_x = c.home_x
            c.target_y = c.home_y

        self.dragged_card = None

hand_controllers = [
    HandController(0, COLOR_HAND_1, "RUKICA 1"),
    HandController(1, COLOR_HAND_2, "RUKICA 2")
]

prev_time = time.time()

print("=" * 65)
print("POKRENUTA AI IGRA SPAJANJA SLIČICA ZA PREDŠKOLCE")
print("Primaknite dečiju šaku kameri.")
print("Spojite palac i kažiprst (Pinch) da uhvatite sličicu!")
print("Kontrole: [r] Ponovo  |  [n] Sledeći  |  [c] Kamera  |  [m] Mute  |  [q] Izlaz")
print("=" * 65)

# ================= GLAVNA PETLJA IGRE =================

while True:
    frame, detected_hands_pts = vision.get_state()
    if frame is None:
        time.sleep(0.005)
        continue

    # 1. Pozadina ekrana (1280x720)
    if show_camera_bg:
        cam_resized = cv2.resize(frame, (CANVAS_W, CANVAS_H))
        dark_overlay = np.full((CANVAS_H, CANVAS_W, 3), (35, 20, 25), dtype=np.uint8)
        canvas = cv2.addWeighted(cam_resized, 0.70, dark_overlay, 0.30, 0)
    else:
        # Topla magična indigo-ljubičasta tema sa sjajnim zvezdanim centrom
        canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
        canvas[:] = COLOR_BG_DARK
        cv2.circle(canvas, (CANVAS_W // 2, 280), 480, COLOR_BG_GRAD, -1)
        cv2.circle(canvas, (CANVAS_W // 2, 280), 280, (90, 48, 62), -1)

    # 2. Detekcija dečijih ruku (podrška za do 2 ruke)
    num_detected = len(detected_hands_pts)
    if num_detected == 1:
        pts = detected_hands_pts[0]
        cur_x = (pts[8][0] + pts[4][0]) // 2
        cur_y = (pts[8][1] + pts[4][1]) // 2

        if hand_controllers[0].dragged_card is not None:
            hand_controllers[0].update_with_landmarks(pts, cards)
            hand_controllers[1].handle_lost_frame(cards)
        elif hand_controllers[1].dragged_card is not None:
            hand_controllers[1].update_with_landmarks(pts, cards)
            hand_controllers[0].handle_lost_frame(cards)
        else:
            d0 = math.hypot(cur_x - hand_controllers[0].cursor_x, cur_y - hand_controllers[0].cursor_y)
            d1 = math.hypot(cur_x - hand_controllers[1].cursor_x, cur_y - hand_controllers[1].cursor_y)
            if d0 <= d1:
                hand_controllers[0].update_with_landmarks(pts, cards)
                hand_controllers[1].handle_lost_frame(cards)
            else:
                hand_controllers[1].update_with_landmarks(pts, cards)
                hand_controllers[0].handle_lost_frame(cards)

    elif num_detected >= 2:
        pts_A = detected_hands_pts[0]
        pts_B = detected_hands_pts[1]
        cur_A = ((pts_A[8][0] + pts_A[4][0]) // 2, (pts_A[8][1] + pts_A[4][1]) // 2)
        cur_B = ((pts_B[8][0] + pts_B[4][0]) // 2, (pts_B[8][1] + pts_B[4][1]) // 2)

        cost_direct = (math.hypot(cur_A[0] - hand_controllers[0].cursor_x, cur_A[1] - hand_controllers[0].cursor_y) +
                       math.hypot(cur_B[0] - hand_controllers[1].cursor_x, cur_B[1] - hand_controllers[1].cursor_y))
        cost_swap = (math.hypot(cur_A[0] - hand_controllers[1].cursor_x, cur_A[1] - hand_controllers[1].cursor_y) +
                     math.hypot(cur_B[0] - hand_controllers[0].cursor_x, cur_B[1] - hand_controllers[0].cursor_y))

        if cost_direct <= cost_swap:
            hand_controllers[0].update_with_landmarks(pts_A, cards)
            hand_controllers[1].update_with_landmarks(pts_B, cards)
        else:
            hand_controllers[1].update_with_landmarks(pts_A, cards)
            hand_controllers[0].update_with_landmarks(pts_B, cards)
    else:
        hand_controllers[0].handle_lost_frame(cards)
        hand_controllers[1].handle_lost_frame(cards)

    # Iscrtavanje magičnih linija za ruke
    for hc in hand_controllers:
        if len(hc.hand_pts) > 0:
            for p1, p2 in HAND_CONNECTIONS:
                cv2.line(canvas, hc.hand_pts[p1], hc.hand_pts[p2], hc.color, 1, cv2.LINE_AA)
            for p in hc.hand_pts:
                cv2.circle(canvas, p, 3, (255, 255, 255), -1, cv2.LINE_AA)
                cv2.circle(canvas, p, 4, hc.color, 1, cv2.LINE_AA)

    # Ažuriranje fizike sličica
    for c in cards:
        c.update_physics()

    # 3. Iscrtavanje donjih kućica (Ciljna polja sa siluetama sličica)
    current_level_items = LEVELS[current_level_idx]["items"]

    for s_idx, (sx, sy) in enumerate(SLOT_POSITIONS):
        target_item = current_level_items[s_idx]

        # Da li bilo koja ruka drži sličicu iznad ovog slota?
        is_hovered = False
        for hc in hand_controllers:
            if hc.dragged_card is not None:
                c_cx = hc.dragged_card.x + CARD_W // 2
                c_cy = hc.dragged_card.y + CARD_H // 2
                if math.hypot(c_cx - (sx + CARD_W // 2), c_cy - (sy + CARD_H // 2)) < 140:
                    is_hovered = True
                    break

        # Da li je unutra već spuštena neka sličica?
        card_in_slot = None
        for c in cards:
            if c.current_slot == s_idx:
                card_in_slot = c
                break

        is_matched = (card_in_slot is not None and card_in_slot.id == target_item["id"])

        if is_matched:
            border_col = COLOR_SLOT_MATCH
            thickness = 3
        elif is_hovered:
            border_col = COLOR_SLOT_ACTIVE
            thickness = 3
        else:
            border_col = COLOR_SLOT_BORDER
            thickness = 2

        # Zaobljena kućica sa senkom
        draw_rounded_rect(canvas, sx + 3, sy + 5, CARD_W, CARD_H, 18, (20, 12, 14), -1)
        draw_rounded_rect(canvas, sx, sy, CARD_W, CARD_H, 18, (38, 25, 28), -1)
        draw_dashed_rounded_rect(canvas, sx, sy, CARD_W, CARD_H, 18, border_col, thickness=thickness)

        # Unutrašnjost kućice: Ako je prazna, prikaži siluetu/duha sličice!
        if card_in_slot is None:
            # Svetleća pozadina kad je iznad
            if is_hovered:
                draw_rounded_rect(canvas, sx + 5, sy + 5, CARD_W - 10, CARD_H - 10, 14, (60, 45, 35), -1)

            # Silueta/duh ciljne sličice (dete odmah vidi šta tu ide!)
            draw_kid_icon(canvas, target_item["icon"], sx + CARD_W // 2, sy + 88, size=75, ghost=True)

            # Oznaka / strelica "OVDE"
            badge_y = sy + CARD_H - 32
            draw_rounded_rect(canvas, sx + 35, badge_y, CARD_W - 70, 24, 10, (50, 32, 35), -1)
            cv2.putText(canvas, "STAVI OVDE", (sx + 55, badge_y + 16),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.40, (190, 190, 190), 1, cv2.LINE_AA)
        else:
            if is_matched:
                # Zlatna zvezda / kvačica uspeha u uglu
                cv2.circle(canvas, (sx + CARD_W - 22, sy + 22), 14, COLOR_SLOT_MATCH, -1, cv2.LINE_AA)
                cv2.circle(canvas, (sx + CARD_W - 22, sy + 22), 14, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.putText(canvas, "OK", (sx + CARD_W - 32, sy + 27),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (10, 50, 20), 2, cv2.LINE_AA)

    # 4. Iscrtavanje dečijih sličica (kartica)
    cards_to_draw = [c for c in cards if not c.is_dragging]
    for hc in hand_controllers:
        if hc.dragged_card is not None and hc.dragged_card not in cards_to_draw:
            cards_to_draw.append(hc.dragged_card)

    for c in cards_to_draw:
        cx, cy = int(c.x), int(c.y)
        card_col = COLOR_CARD_DRAG if c.is_dragging else c.theme_color
        bg_col = (85, 55, 45) if c.is_dragging else COLOR_CARD_BG

        # Meka dečija senka
        draw_rounded_rect(canvas, cx + 4, cy + 6, CARD_W, CARD_H, 20, (15, 8, 10), -1)

        # Glavno telo kartice
        draw_rounded_rect(canvas, cx, cy, CARD_W, CARD_H, 20, bg_col, -1)
        border_th = 4 if c.is_dragging else 2
        draw_rounded_rect(canvas, cx, cy, CARD_W, CARD_H, 20, card_col, border_th)

        # Vektorska ilustracija u sredini
        draw_kid_icon(canvas, c.icon, cx + CARD_W // 2, cy + 85, size=75, ghost=False)

        # Donja lajsnica sa slatkim natpisom (za roditelje/vaspitače, a detetu lepa pilulica)
        draw_rounded_rect(canvas, cx + 14, cy + CARD_H - 42, CARD_W - 28, 30, 10, (35, 22, 25), -1)
        draw_rounded_rect(canvas, cx + 14, cy + CARD_H - 42, CARD_W - 28, 30, 10, card_col, 1)

        txt_size = cv2.getTextSize(c.name, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 2)[0]
        text_x = cx + (CARD_W - txt_size[0]) // 2
        text_y = cy + CARD_H - 22
        cv2.putText(canvas, c.name, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.52, COLOR_TEXT_WHITE, 2, cv2.LINE_AA)

    # 5. Provera tačnosti nivoa
    slots_filled = [None] * 4
    for c in cards:
        if c.current_slot is not None:
            slots_filled[c.current_slot] = c

    if all(s is not None for s in slots_filled):
        is_all_correct = all(slots_filled[i].id == current_level_items[i]["id"] for i in range(4))
        if is_all_correct and not level_solved:
            level_solved = True
            level_solved_time = time.time()
            game_score += 50
            play_sound(snd_win)

            # Generiši šarene konfete i balone koji lete uvis
            for _ in range(75):
                particles.append({
                    "x": random.randint(80, CANVAS_W - 80),
                    "y": random.randint(180, 500),
                    "vx": random.uniform(-5, 5),
                    "vy": random.uniform(-8, -2),
                    "color": (random.randint(60, 255), random.randint(100, 255), random.randint(150, 255)),
                    "size": random.randint(5, 11),
                    "life": random.randint(45, 90)
                })

            for _ in range(12):
                floating_balloons.append({
                    "x": random.randint(100, CANVAS_W - 100),
                    "y": random.randint(550, 720),
                    "vy": random.uniform(-4.5, -2.5),
                    "color": random.choice([(50, 60, 240), (0, 200, 240), (60, 210, 80), (220, 70, 190), (0, 215, 255)]),
                    "scale": random.uniform(1.2, 1.7)
                })
            print(f"[POBEDA] Nivo {current_level_idx + 1} uspešno rešen! Svaka čast!")

    # 6. Slavlje sa konfetama i balonima
    if level_solved:
        alive_particles = []
        for p in particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.20
            p["life"] -= 1
            if p["life"] > 0:
                cv2.circle(canvas, (int(p["x"]), int(p["y"])), p["size"], p["color"], -1)
                alive_particles.append(p)
        particles = alive_particles

        # Baloni koji lete uvis
        alive_balloons = []
        for b in floating_balloons:
            b["y"] += b["vy"]
            if b["y"] > -50:
                draw_single_balloon(canvas, int(b["x"]), int(b["y"]), b["color"], b["scale"], False)
                alive_balloons.append(b)
        floating_balloons = alive_balloons

        # Veliki pobednički bedž za decu na sredini
        bw, bh = 680, 95
        bx = (CANVAS_W - bw) // 2
        by = 250
        draw_rounded_rect(canvas, bx + 5, by + 6, bw, bh, 24, (10, 40, 15), -1)
        draw_rounded_rect(canvas, bx, by, bw, bh, 24, (20, 120, 45), -1)
        draw_rounded_rect(canvas, bx, by, bw, bh, 24, (0, 255, 180), 4)

        # Zvezdice na krajevima banera
        draw_zvezda(canvas, bx + 45, by + 47, size=46)
        draw_zvezda(canvas, bx + bw - 45, by + 47, size=46)

        cv2.putText(canvas, "BRAVO! SVAKA CAST!", (bx + 85, by + 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(canvas, "SVE SLICICE SU NA SVOM MESTU! (+50)", (bx + 115, by + 78),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, (120, 255, 200), 2, cv2.LINE_AA)

        if time.time() - level_solved_time > 3.6:
            current_level_idx = (current_level_idx + 1) % len(LEVELS)
            init_level(current_level_idx)

    # 7. Donji baner sa zadatkom (Vesela pilula)
    prompt_w = 980
    prompt_h = 56
    px = (CANVAS_W - prompt_w) // 2
    py = 585
    draw_rounded_rect(canvas, px, py, prompt_w, prompt_h, 16, (36, 22, 26), -1)
    draw_rounded_rect(canvas, px, py, prompt_w, prompt_h, 16, (140, 90, 80), 2)

    level_hint = LEVELS[current_level_idx]["hint"]
    cv2.putText(canvas, level_hint, (px + 30, py + 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.64, COLOR_TEXT_GOLD, 2, cv2.LINE_AA)

    # 8. Gornje zaglavlje (HUD): Naslov, Zvezdice, Nivo
    draw_rounded_rect(canvas, 20, 15, CANVAS_W - 40, 70, 18, (28, 18, 22), -1)
    draw_rounded_rect(canvas, 20, 15, CANVAS_W - 40, 70, 18, (90, 55, 60), 1)

    # Levo: Glavni naslov i status rukica
    cv2.putText(canvas, "IGRA SPAJANJA SLICICA", (45, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
    active_hands_count = sum(1 for hc in hand_controllers if hc.lost_frames == 0)
    if active_hands_count >= 1:
        cv2.circle(canvas, (45, 66), 5, (0, 255, 0), -1)
        hand_msg = f"{active_hands_count} RUKICA AKTIVNA - SPOJ PRSTICE DA UHVATIS SLICICU"
        cv2.putText(canvas, hand_msg, (60, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 120), 1, cv2.LINE_AA)
    else:
        holding_any = any(hc.dragged_card is not None for hc in hand_controllers)
        if holding_any:
            cv2.circle(canvas, (45, 66), 5, (0, 220, 255), -1)
            cv2.putText(canvas, "ZADRZAVANJE SLICICE...", (60, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 220, 255), 1, cv2.LINE_AA)
        else:
            cv2.circle(canvas, (45, 66), 5, (80, 80, 255), -1)
            cv2.putText(canvas, "PRINESITE RUKICU KAMERI...", (60, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (120, 120, 255), 1, cv2.LINE_AA)

    # Sredina: Naziv nivoa
    lvl_title = LEVELS[current_level_idx]["title"]
    title_size = cv2.getTextSize(lvl_title, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)[0]
    cv2.putText(canvas, lvl_title, ((CANVAS_W - title_size[0]) // 2, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 230, 255), 2, cv2.LINE_AA)

    # Desno: Bedževi za zvezdice (bodove) i nivo
    draw_rounded_rect(canvas, CANVAS_W - 275, 22, 115, 52, 12, (20, 70, 45), -1)
    draw_rounded_rect(canvas, CANVAS_W - 275, 22, 115, 52, 12, (0, 255, 160), 2)
    cv2.putText(canvas, "ZVEZDICE", (CANVAS_W - 262, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 160), 1, cv2.LINE_AA)
    cv2.putText(canvas, f"{game_score}", (CANVAS_W - 250, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    draw_rounded_rect(canvas, CANVAS_W - 145, 22, 115, 52, 12, (75, 40, 30), -1)
    draw_rounded_rect(canvas, CANVAS_W - 145, 22, 115, 52, 12, (0, 200, 255), 2)
    cv2.putText(canvas, "NIVO", (CANVAS_W - 122, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 200, 255), 1, cv2.LINE_AA)
    cv2.putText(canvas, f"{current_level_idx + 1}/{len(LEVELS)}", (CANVAS_W - 128, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)

    # 9. Vazdušni kursor za dečije ruke
    for hc in hand_controllers:
        if hc.lost_frames <= GRACE_FRAMES_LOST:
            cur_x, cur_y = hc.cursor_x, hc.cursor_y
            if hc.is_pinching or hc.dragged_card is not None:
                # Sjajni zvezdani prsten kada ruka drži sličicu
                cv2.circle(canvas, (cur_x, cur_y), 22, hc.color, 3, cv2.LINE_AA)
                cv2.circle(canvas, (cur_x, cur_y), 8, (0, 255, 150), -1, cv2.LINE_AA)
                cv2.putText(canvas, "[DRZI]", (cur_x + 18, cur_y - 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 255, 150), 1, cv2.LINE_AA)
            else:
                # Lebdeći magični kružić
                cv2.circle(canvas, (cur_x, cur_y), 15, (255, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(canvas, (cur_x, cur_y), 5, hc.color, -1, cv2.LINE_AA)
                cv2.putText(canvas, hc.label, (cur_x + 15, cur_y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.38, hc.color, 1, cv2.LINE_AA)

    # 10. Traka sa prečicama na dnu (za vaspitače / roditelje)
    snd_status = "UKLJ" if sound_enabled else "ISKLJ"
    footer_txt = f"[Pinch] Uhvati slicicu  |  [r] Ponovo  |  [n] Sledeci  |  [p] Prethodni  |  [c] Kamera  |  [m] Zvuk ({snd_status})  |  [q] Izlaz"
    cv2.putText(canvas, footer_txt, (150, 698), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (170, 160, 165), 1, cv2.LINE_AA)

    # FPS indikator
    curr_time = time.time()
    fps = 1.0 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time
    cv2.putText(canvas, f"FPS: {int(fps)}", (35, 698), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 100), 1, cv2.LINE_AA)

    # Prikaz na ekranu
    cv2.imshow("AI Igra Spajanja Slicica za Predskolce (RPi 5)", canvas)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break
    elif key == ord('r'):
        for hc in hand_controllers:
            hc.dragged_card = None
            hc.is_pinching = False
        init_level(current_level_idx)
    elif key == ord('n'):
        for hc in hand_controllers:
            hc.dragged_card = None
            hc.is_pinching = False
        current_level_idx = (current_level_idx + 1) % len(LEVELS)
        init_level(current_level_idx)
    elif key == ord('p'):
        for hc in hand_controllers:
            hc.dragged_card = None
            hc.is_pinching = False
        current_level_idx = (current_level_idx - 1) % len(LEVELS)
        init_level(current_level_idx)
    elif key == ord('c'):
        show_camera_bg = not show_camera_bg
        print(f"[INFO] Pozadina kamere: {'UKLJUČENA' if show_camera_bg else 'ISKLJUČENA'}")
    elif key == ord('m'):
        sound_enabled = not sound_enabled
        print(f"[INFO] Zvuk: {'UKLJUČEN' if sound_enabled else 'ISKLJUČEN'}")

# Gašenje resursa
vision.stop()
cv2.destroyAllWindows()
