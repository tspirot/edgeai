#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
             ✨ ČAROBNO OGLEDALO (FACE MAGIC MIRROR) — PREDŠKOLCI
================================================================================
Opis:
  Ultra-brzo magično ogledalo sa maskicama životinja i kruna za decu.
  Asinhrona obrada slike i MediaPipe FaceMesh-a za 40+ FPS i prirodne boje.
  Prilagođeno deci: uši mace, kuce, zeke, zlatna kruna i svetleće zvezdice!

Kontrole:
  - [Otvori usta] Izleću svetlucave zvezdice i magični zvuci!
  - [Razmaknica] ili [n] Promeni masku
  - [m] Zvuk uključen / isključen
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
snd_magic = None
snd_pop = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def make_magic_chime():
        sr = 44100
        notes = [587, 740, 880, 1174]
        d = 0.08
        n = int(sr * d)
        chunks = []
        for f in notes:
            t = np.linspace(0, d, n, False)
            env = np.exp(-4.0 * t / d)
            chunks.append(np.sin(2 * np.pi * f * t) * env * 0.22)
        full = np.concatenate(chunks)
        audio = (full * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_switch_sound():
        sr = 44100
        d = 0.06
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        f = np.linspace(350, 750, n)
        wave = np.sin(2 * np.pi * f * t) * 0.20
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    snd_magic = make_magic_chime()
    snd_pop = make_switch_sound()
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
WINDOW_NAME = "Carobno Ogledalo - Predskolci"

class FastVisionFace:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.use_picam2 = False
        self.latest_frame = None
        self.face_points = None
        self.mouth_open = False
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
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
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
            results = face_mesh.process(rgb)

            pts_dict = {}
            is_open = False

            if results.multi_face_landmarks:
                flms = results.multi_face_landmarks[0]
                # Ključne tačke lica
                key_indices = [10, 4, 152, 234, 454, 13, 14, 33, 263]
                for idx in key_indices:
                    lm = flms.landmark[idx]
                    pts_dict[idx] = (int(lm.x * self.width), int(lm.y * self.height))

                # Otvorena usta (gornja usna 13, donja usna 14, nos 4, brada 152)
                p13 = pts_dict.get(13)
                p14 = pts_dict.get(14)
                p10 = pts_dict.get(10)
                p152 = pts_dict.get(152)

                if p13 and p14 and p10 and p152:
                    mouth_h = abs(p14[1] - p13[1])
                    face_h = max(1, abs(p152[1] - p10[1]))
                    if (mouth_h / face_h) > 0.08:
                        is_open = True

            with self.lock:
                self.face_points = pts_dict if len(pts_dict) > 0 else None
                self.mouth_open = is_open

            time.sleep(0.002)

    def get_state(self):
        with self.lock:
            if self.latest_frame is not None:
                f = cv2.flip(self.latest_frame, 1)
                pts = dict(self.face_points) if self.face_points else None
                return f, pts, self.mouth_open
            return None, None, False

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

vision = FastVisionFace(WIDTH, HEIGHT)

MASKS = [
    {"id": "MACA",   "name": "CICA MACA",   "color": (0, 165, 255)},
    {"id": "KUCA",   "name": "VESELI KUCA", "color": (70, 130, 185)},
    {"id": "ZEKA",   "name": "BELI ZEKA",   "color": (245, 240, 245)},
    {"id": "KRUNA",  "name": "ZLATNA KRUNA","color": (0, 215, 255)}
]

current_mask_idx = 0
particles = []
mouth_open_prev = False

def draw_mask_maca(img, pts):
    p_forehead = pts[10]
    p_nose = pts[4]
    p_left = pts[234]
    p_right = pts[454]

    face_w = int(math.hypot(p_right[0] - p_left[0], p_right[1] - p_left[1]))
    ear_w = int(face_w * 0.35)
    ear_h = int(face_w * 0.50)

    # Uši mace
    pts_el = np.array([
        (p_forehead[0] - int(face_w * 0.45), p_forehead[1] + 5),
        (p_forehead[0] - int(face_w * 0.40), p_forehead[1] - ear_h),
        (p_forehead[0] - int(face_w * 0.08), p_forehead[1] - int(ear_h * 0.3))
    ], np.int32)
    pts_er = np.array([
        (p_forehead[0] + int(face_w * 0.45), p_forehead[1] + 5),
        (p_forehead[0] + int(face_w * 0.40), p_forehead[1] - ear_h),
        (p_forehead[0] + int(face_w * 0.08), p_forehead[1] - int(ear_h * 0.3))
    ], np.int32)

    cv2.fillPoly(img, [pts_el, pts_er], (0, 165, 255), cv2.LINE_AA)
    cv2.polylines(img, [pts_el, pts_er], True, (255, 255, 255), 2, cv2.LINE_AA)

    # Unutrašnjost ušiju (roze)
    pts_iel = np.array([
        (p_forehead[0] - int(face_w * 0.38), p_forehead[1]),
        (p_forehead[0] - int(face_w * 0.35), p_forehead[1] - int(ear_h * 0.78)),
        (p_forehead[0] - int(face_w * 0.15), p_forehead[1] - int(ear_h * 0.35))
    ], np.int32)
    pts_ier = np.array([
        (p_forehead[0] + int(face_w * 0.38), p_forehead[1]),
        (p_forehead[0] + int(face_w * 0.35), p_forehead[1] - int(ear_h * 0.78)),
        (p_forehead[0] + int(face_w * 0.15), p_forehead[1] - int(ear_h * 0.35))
    ], np.int32)
    cv2.fillPoly(img, [pts_iel, pts_ier], (180, 140, 255), cv2.LINE_AA)

    # Slatki nosić
    cv2.circle(img, p_nose, int(face_w * 0.09), (180, 100, 255), -1, cv2.LINE_AA)
    cv2.circle(img, p_nose, int(face_w * 0.09), (255, 255, 255), 2, cv2.LINE_AA)

    # Brkovi
    w_len = int(face_w * 0.50)
    for dy in [-5, 5]:
        cv2.line(img, (p_nose[0] - 15, p_nose[1] + dy), (p_nose[0] - 15 - w_len, p_nose[1] + dy * 2), (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(img, (p_nose[0] + 15, p_nose[1] + dy), (p_nose[0] + 15 + w_len, p_nose[1] + dy * 2), (255, 255, 255), 2, cv2.LINE_AA)

def draw_mask_kuca(img, pts):
    p_forehead = pts[10]
    p_nose = pts[4]
    p_left = pts[234]
    p_right = pts[454]

    face_w = int(math.hypot(p_right[0] - p_left[0], p_right[1] - p_left[1]))
    ear_w = int(face_w * 0.22)
    ear_h = int(face_w * 0.60)

    # Spuštene pseće uši
    cv2.ellipse(img, (p_left[0] - 10, p_left[1] + int(ear_h * 0.25)), (ear_w, ear_h), -20, 0, 360, (50, 95, 140), -1, cv2.LINE_AA)
    cv2.ellipse(img, (p_right[0] + 10, p_right[1] + int(ear_h * 0.25)), (ear_w, ear_h), 20, 0, 360, (50, 95, 140), -1, cv2.LINE_AA)
    cv2.ellipse(img, (p_left[0] - 10, p_left[1] + int(ear_h * 0.25)), (ear_w, ear_h), -20, 0, 360, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.ellipse(img, (p_right[0] + 10, p_right[1] + int(ear_h * 0.25)), (ear_w, ear_h), 20, 0, 360, (255, 255, 255), 2, cv2.LINE_AA)

    # Pseći nos
    cv2.ellipse(img, (p_nose[0], p_nose[1] - 4), (int(face_w * 0.12), int(face_w * 0.08)), 0, 0, 360, (30, 30, 30), -1, cv2.LINE_AA)
    cv2.circle(img, (p_nose[0] - 3, p_nose[1] - 6), 2, (255, 255, 255), -1, cv2.LINE_AA)

def draw_mask_zeka(img, pts):
    p_forehead = pts[10]
    p_nose = pts[4]
    p_left = pts[234]
    p_right = pts[454]

    face_w = int(math.hypot(p_right[0] - p_left[0], p_right[1] - p_left[1]))
    ear_w = int(face_w * 0.20)
    ear_h = int(face_w * 0.90)

    # Dugačke uši zeke
    cv2.ellipse(img, (p_forehead[0] - int(face_w * 0.30), p_forehead[1] - ear_h // 2), (ear_w, ear_h // 2), -10, 0, 360, (245, 245, 250), -1, cv2.LINE_AA)
    cv2.ellipse(img, (p_forehead[0] + int(face_w * 0.30), p_forehead[1] - ear_h // 2), (ear_w, ear_h // 2), 10, 0, 360, (245, 245, 250), -1, cv2.LINE_AA)
    cv2.ellipse(img, (p_forehead[0] - int(face_w * 0.30), p_forehead[1] - ear_h // 2), (ear_w // 2, ear_h // 3), -10, 0, 360, (200, 180, 255), -1, cv2.LINE_AA)
    cv2.ellipse(img, (p_forehead[0] + int(face_w * 0.30), p_forehead[1] - ear_h // 2), (ear_w // 2, ear_h // 3), 10, 0, 360, (200, 180, 255), -1, cv2.LINE_AA)

    # Nos zeke
    cv2.circle(img, p_nose, int(face_w * 0.08), (180, 140, 255), -1, cv2.LINE_AA)
    cv2.circle(img, p_nose, int(face_w * 0.08), (255, 255, 255), 2, cv2.LINE_AA)

def draw_mask_kruna(img, pts):
    p_forehead = pts[10]
    p_left = pts[234]
    p_right = pts[454]

    face_w = int(math.hypot(p_right[0] - p_left[0], p_right[1] - p_left[1]))
    cw = int(face_w * 0.90)
    ch = int(face_w * 0.55)

    base_y = p_forehead[1] - 10
    cx = p_forehead[0]

    pts_crown = np.array([
        (cx - cw // 2, base_y),
        (cx - cw // 2, base_y - ch // 2),
        (cx - cw // 4, base_y - ch // 3),
        (cx, base_y - ch),
        (cx + cw // 4, base_y - ch // 3),
        (cx + cw // 2, base_y - ch // 2),
        (cx + cw // 2, base_y)
    ], np.int32)

    cv2.fillPoly(img, [pts_crown], (0, 215, 255), cv2.LINE_AA)
    cv2.polylines(img, [pts_crown], True, (255, 255, 255), 3, cv2.LINE_AA)

    # Dragulji na kruni
    for pt in [(cx - cw // 2, base_y - ch // 2), (cx, base_y - ch), (cx + cw // 2, base_y - ch // 2)]:
        cv2.circle(img, pt, 8, (60, 50, 245), -1, cv2.LINE_AA)
        cv2.circle(img, pt, 8, (255, 255, 255), 2, cv2.LINE_AA)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)

print("=" * 60)
print("POKRENUTO BRZO 'ČAROBNO OGLEDALO' (PRIRODNE BOJE & 40+ FPS)")
print("Otvarajte usta za zvezdice! [n] ili [Razmaknica] Promena maske")
print("Kontrole: [m] Zvuk  |  [q] Izlaz")
print("=" * 60)

try:
    while True:
        frame, pts, mouth_open = vision.get_state()
        if frame is None:
            time.sleep(0.005)
            continue

        if pts:
            # Iscrtaj odabranu maskicu
            m_id = MASKS[current_mask_idx]["id"]
            if m_id == "MACA":
                draw_mask_maca(frame, pts)
            elif m_id == "KUCA":
                draw_mask_kuca(frame, pts)
            elif m_id == "ZEKA":
                draw_mask_zeka(frame, pts)
            elif m_id == "KRUNA":
                draw_mask_kruna(frame, pts)

            # Reakcija na otvorena usta
            if mouth_open and not mouth_open_prev:
                play_sound(snd_magic)
                mouth_pt = pts.get(14, (WIDTH // 2, HEIGHT // 2))
                for _ in range(25):
                    particles.append({
                        "x": mouth_pt[0],
                        "y": mouth_pt[1],
                        "vx": random.uniform(-5, 5),
                        "vy": random.uniform(-6, -1),
                        "color": random.choice([(0, 240, 255), (255, 255, 255), (240, 100, 255), (100, 240, 100)]),
                        "size": random.randint(3, 7),
                        "life": random.randint(18, 35)
                    })
            mouth_open_prev = mouth_open

        # Čestice zvezdica
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.22
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)
            else:
                cv2.circle(frame, (int(p["x"]), int(p["y"])), p["size"], p["color"], -1, cv2.LINE_AA)

        # Header info
        m_name = MASKS[current_mask_idx]["name"]
        cv2.rectangle(frame, (10, 10), (280, 55), (30, 30, 40), -1)
        cv2.rectangle(frame, (10, 10), (280, 55), (0, 215, 255), 2)
        cv2.putText(frame, m_name, (20, 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord(' ') or key == ord('n'):
            current_mask_idx = (current_mask_idx + 1) % len(MASKS)
            play_sound(snd_pop)
        elif key == ord('m'):
            sound_enabled = not sound_enabled

finally:
    vision.stop()
    cv2.destroyAllWindows()
    print("[INFO] Igra ogledalo završena.")
