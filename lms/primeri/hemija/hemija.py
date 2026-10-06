#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
         🧪 AR INTERAKTIVNA HEMIJA — CEPANJE I SPAJANJE ATOMA (RPi 5)
================================================================================
Opis:
  Proširena stvarnost (AR) u kojoj rukama u vazduhu birate elemente iz Periodnog
  sistema, cepate hemijske veze razvlačenjem obema rukama, i spajate atome
  u nove molekule uz spektakularne AR efekte, zvuke i fiziku opruga.

Kontrole:
  - [Štipanje obema rukama] Uhvati dva atoma (palac + kažiprst) i razvuci ih da pukne veza!
  - [Prinos atoma] Prinesi atome jedan drugom da se spoje po pravilima hemijskih valenci
  - [1 - 6] Brzi eksperimenti i molekuli:
      [1] Voda (H2 + O -> H2O)
      [2] Ugljen-dioksid (C + O2 -> CO2)
      [3] Kuhinjska so (Na + Cl -> NaCl)
      [4] Metan (C + 4H -> CH4)
      [5] Amonijak (N + 3H -> NH3)
      [6] Hlorovodonik (H2 + Cl2 -> 2 HCl)
  - [p] Otvori / zatvori Periodni sistem elemenata (dodavanje novih atoma)
  - [r] ili [Space] Resetuj trenutni eksperiment
  - [m] Zvuk (Uključi / Isključi)
  - [q] ili [ESC] Izlaz
================================================================================
"""

import os
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

import sys
import time
import math
import random
import threading
import cv2
import numpy as np

try:
    import mediapipe as mp
except Exception:
    mp = None

# ================= ZVUČNI SISTEM =================
sound_enabled = True
snd_snap = None
snd_bond = None
snd_water = None
snd_crystal = None
snd_gas = None
snd_acid = None
snd_fanfare = None

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    def make_bond_break_sound():
        sr = 44100
        d = 0.12
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        f = np.linspace(800, 150, n)
        noise = (np.random.rand(n) - 0.5) * 0.4
        env = np.exp(-15.0 * t / d)
        wave = (np.sin(2 * np.pi * f * t) * 0.6 + noise) * env * 0.35
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_bond_form_sound():
        sr = 44100
        d = 0.15
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        wave = (np.sin(2 * np.pi * 587.33 * t) + np.sin(2 * np.pi * 880.0 * t) * 0.5) * np.exp(-10.0 * t / d) * 0.25
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_water_splash_sound():
        sr = 44100
        d = 0.6
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        f_bubble = 450 + 350 * np.sin(2 * np.pi * 12 * t)
        sine = np.sin(2 * np.pi * f_bubble * t) * 0.3
        noise = (np.random.rand(n) - 0.5) * 0.35
        env = np.exp(-4.5 * t / d)
        wave = (sine + noise) * env * 0.4
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_crystal_chime_sound():
        sr = 44100
        d = 0.55
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        wave = (np.sin(2 * np.pi * 1318.5 * t) * 0.4 +
                np.sin(2 * np.pi * 1661.2 * t) * 0.3 +
                np.sin(2 * np.pi * 1975.5 * t) * 0.3) * np.exp(-6.0 * t / d) * 0.3
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_gas_whoosh_sound():
        sr = 44100
        d = 0.45
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        noise = (np.random.rand(n) - 0.5) * 0.5
        f_mod = 250 + 150 * np.sin(2 * np.pi * 4 * t)
        sine = np.sin(2 * np.pi * f_mod * t) * 0.3
        env = np.sin(np.pi * t / d) ** 1.5
        wave = (noise + sine) * env * 0.35
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_acid_hiss_sound():
        sr = 44100
        d = 0.40
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        noise = (np.random.rand(n) - 0.5) * 0.6
        f_bub = 750 + 200 * np.sin(2 * np.pi * 20 * t)
        sine = np.sin(2 * np.pi * f_bub * t) * 0.25
        env = np.exp(-3.5 * t / d)
        wave = (noise + sine) * env * 0.35
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    def make_victory_fanfare():
        sr = 44100
        d = 0.36
        n = int(sr * d)
        t = np.linspace(0, d, n, False)
        seg = n // 3
        w1 = np.sin(2 * np.pi * 523.25 * t[:seg]) * np.exp(-4.0 * t[:seg] / (d/3))
        w2 = np.sin(2 * np.pi * 659.25 * t[:seg]) * np.exp(-4.0 * t[:seg] / (d/3))
        w3 = np.sin(2 * np.pi * 783.99 * t[:n - 2*seg]) * np.exp(-3.0 * t[:n - 2*seg] / (d/3))
        wave = np.concatenate([w1, w2, w3]) * 0.28
        audio = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo)

    snd_snap = make_bond_break_sound()
    snd_bond = make_bond_form_sound()
    snd_water = make_water_splash_sound()
    snd_crystal = make_crystal_chime_sound()
    snd_gas = make_gas_whoosh_sound()
    snd_acid = make_acid_hiss_sound()
    snd_fanfare = make_victory_fanfare()
except Exception:
    sound_enabled = False

def play_sound(snd):
    if sound_enabled and snd is not None:
        try:
            snd.play()
        except Exception:
            pass

# ================= ASINHRONA KAMERA I AI VID (40+ FPS) =================
class FastVisionHands2:
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        self.use_picam2 = False
        self.latest_frame = None
        self.hands_state = []
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
            print("[INFO] Picamera2 uspesno pokrenuta u prirodnom RGB888 rezimu.")
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
        if mp is None:
            return

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

            detected = []
            if results.multi_hand_landmarks:
                for hlms in results.multi_hand_landmarks:
                    lm4 = hlms.landmark[4]   # Palac vrh
                    lm8 = hlms.landmark[8]   # Kaziprst vrh
                    lm9 = hlms.landmark[9]   # Dlan centar

                    p4 = (int(lm4.x * self.width), int(lm4.y * self.height))
                    p8 = (int(lm8.x * self.width), int(lm8.y * self.height))
                    palm = (int(lm9.x * self.width), int(lm9.y * self.height))

                    pinch_pt = ((p4[0] + p8[0]) // 2, (p4[1] + p8[1]) // 2)
                    dist = math.hypot(p4[0] - p8[0], p4[1] - p8[1])
                    is_pinching = (dist < 46)

                    detected.append({
                        "thumb": p4,
                        "index": p8,
                        "pinch": pinch_pt,
                        "palm": palm,
                        "is_pinching": is_pinching,
                        "dist": dist
                    })

            with self.lock:
                self.hands_state = detected

            time.sleep(0.002)

    def get_state(self):
        with self.lock:
            if self.latest_frame is not None:
                f = cv2.flip(self.latest_frame, 1)
                h = [dict(s) for s in self.hands_state]
                return f, h
            # Sinteticki crni frejm ako kamera jos nije spremna
            blank = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            return blank, []

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
WINDOW_NAME = "AR Hemija - Cepanje i Spajanje Atoma"

# ================= HEMIJSKI PODACI I ELEMENTI =================
ELEMENTS = {
    "H":  {
        "symbol": "H",  "name": "Hydrogen", "sr_name": "Vodonik",  "short_sr": "Vod.",
        "z": 1,  "color": (235, 235, 240), "border": (255, 255, 255), "radius": 24, "val": 1
    },
    "O":  {
        "symbol": "O",  "name": "Oxygen",   "sr_name": "Kiseonik", "short_sr": "Kis.",
        "z": 8,  "color": (40, 45, 235),   "border": (100, 110, 255), "radius": 36, "val": 2
    },
    "C":  {
        "symbol": "C",  "name": "Carbon",   "sr_name": "Ugljenik", "short_sr": "Uglj.",
        "z": 6,  "color": (50, 50, 55),    "border": (130, 130, 140), "radius": 34, "val": 4
    },
    "N":  {
        "symbol": "N",  "name": "Nitrogen", "sr_name": "Azot",     "short_sr": "Azot",
        "z": 7,  "color": (210, 110, 40),  "border": (245, 170, 90),  "radius": 32, "val": 3
    },
    "Na": {
        "symbol": "Na", "name": "Sodium",   "sr_name": "Natrijum", "short_sr": "Natr.",
        "z": 11, "color": (190, 80, 170),  "border": (240, 140, 230), "radius": 38, "val": 1
    },
    "Cl": {
        "symbol": "Cl", "name": "Chlorine", "sr_name": "Hlor",     "short_sr": "Hlor",
        "z": 17, "color": (50, 190, 80),   "border": (120, 240, 140), "radius": 36, "val": 1
    }
}

ALLOWED_PAIRS = {
    frozenset(["H", "H"]),
    frozenset(["H", "O"]),
    frozenset(["H", "C"]),
    frozenset(["H", "N"]),
    frozenset(["H", "Cl"]),
    frozenset(["O", "O"]),
    frozenset(["O", "C"]),
    frozenset(["O", "N"]),
    frozenset(["C", "C"]),
    frozenset(["C", "N"]),
    frozenset(["C", "Cl"]),
    frozenset(["N", "N"]),
    frozenset(["Na", "Cl"]),
    frozenset(["Cl", "Cl"]),
}

class Atom:
    def __init__(self, elem_key, x, y):
        self.key = elem_key
        self.data = ELEMENTS[elem_key]
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = self.data["radius"]
        self.grabbed_by = None

    def is_inside(self, px, py):
        return math.hypot(self.x - px, self.y - py) <= (self.radius + 18)

    def draw(self, img, is_grabbed=False):
        cx, cy, r = int(self.x), int(self.y), int(self.radius)

        base_color = self.data["color"]
        border_color = self.data["border"]

        # Senka
        cv2.circle(img, (cx + 3, cy + 4), r, (15, 15, 20), -1, cv2.LINE_AA)

        # Glavno telo sfere
        cv2.circle(img, (cx, cy), r, base_color, -1, cv2.LINE_AA)
        cv2.circle(img, (cx, cy), r, border_color, 2, cv2.LINE_AA)

        # 3D Specular odsjaj svetlosti gore-levo
        hl_x = cx - int(r * 0.35)
        hl_y = cy - int(r * 0.35)
        hl_r = max(4, int(r * 0.35))
        cv2.ellipse(img, (hl_x, hl_y), (hl_r, int(hl_r * 0.65)), -30, 0, 360, (255, 255, 255), -1, cv2.LINE_AA)

        # Simbol elementa u centru
        sym = self.data["symbol"]
        font_scale = 0.75 if len(sym) == 1 else 0.58
        font_th = 2
        text_col = (20, 20, 20) if self.key == "H" else (255, 255, 255)
        tsize = cv2.getTextSize(sym, cv2.FONT_HERSHEY_DUPLEX, font_scale, font_th)[0]
        cv2.putText(img, sym, (cx - tsize[0] // 2, cy + tsize[1] // 2),
                    cv2.FONT_HERSHEY_DUPLEX, font_scale, text_col, font_th, cv2.LINE_AA)

        # Srpski naziv i valenca iznad atoma
        val_str = "I" * self.data["val"] if self.data["val"] <= 3 else "IV"
        lbl = f"{self.data['symbol']} · {self.data['sr_name']}"
        if is_grabbed:
            lbl += f" (Val:{val_str})"
        lsize = cv2.getTextSize(lbl, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)[0]
        cv2.putText(img, lbl, (cx - lsize[0] // 2, cy - r - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (245, 245, 245), 1, cv2.LINE_AA)

        # Svetleci prsten kada je atom uhvacen prstima
        if is_grabbed:
            ring_col = (0, 245, 255) if self.grabbed_by == 0 else (60, 215, 255)
            cv2.circle(img, (cx, cy), r + 8, ring_col, 2, cv2.LINE_AA)
            cv2.circle(img, (cx, cy), r + 12, (255, 255, 255), 1, cv2.LINE_AA)

class ChemicalBond:
    def __init__(self, atom1, atom2):
        self.atom1 = atom1
        self.atom2 = atom2
        self.rest_length = float(atom1.radius + atom2.radius + 18)
        self.is_broken = False
        self.tension = 0.0

    def get_length(self):
        return math.hypot(self.atom1.x - self.atom2.x, self.atom1.y - self.atom2.y)

    def update(self):
        dist = self.get_length()
        self.tension = max(0.0, (dist - self.rest_length) / 100.0)

        # Opruga privlaci atome ako nisu oba uhvacena razlicitim rukama
        if self.atom1.grabbed_by is None or self.atom2.grabbed_by is None:
            diff = dist - self.rest_length
            if dist > 0.001:
                dx = (self.atom2.x - self.atom1.x) / dist
                dy = (self.atom2.y - self.atom1.y) / dist
                force = diff * 0.16
                if self.atom1.grabbed_by is None:
                    self.atom1.x += dx * force
                    self.atom1.y += dy * force
                if self.atom2.grabbed_by is None:
                    self.atom2.x -= dx * force
                    self.atom2.y -= dy * force

    def draw(self, img):
        x1, y1 = int(self.atom1.x), int(self.atom1.y)
        x2, y2 = int(self.atom2.x), int(self.atom2.y)

        if self.tension > 0.55:
            # Upozorenje na pucanje — treperenje veze
            vibrate = random.randint(-2, 2)
            y1 += vibrate
            y2 += vibrate
            bond_col = (30, 60, 255)  # Crvena pred raskid
            thickness = 6
        else:
            bond_col = (30, 150, 255) # Narandzasto-zlatna veza
            thickness = 5

        cv2.line(img, (x1, y1), (x2, y2), bond_col, thickness, cv2.LINE_AA)
        cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2, cv2.LINE_AA)

        if self.tension > 0.28:
            mx, my = (x1 + x2) // 2, (y1 + y2) // 2
            pct = int(min(100, self.tension * 100))
            txt = f"Zatezanje: {pct}%"
            if self.tension > 0.65:
                txt = "PUCANJE!"
            cv2.putText(img, txt, (mx - 35, my - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 240, 255), 1, cv2.LINE_AA)

# ================= STANJE SCENE I EKSPERIMENATA =================
atoms = []
bonds = []
particles = []
active_molecules = []
known_molecule_keys = set()
show_periodic_table = False
current_experiment_id = 1
current_experiment_name = "Voda (H2 + O -> H2O)"

# Dugmad Periodnog sistema
PT_ELEMENTS = ["H", "O", "C", "N", "Na", "Cl"]
PT_BTNS = []
btn_w, btn_h = 58, 48
start_x = (WIDTH - len(PT_ELEMENTS) * (btn_w + 10)) // 2
for idx, el_key in enumerate(PT_ELEMENTS):
    bx = start_x + idx * (btn_w + 10)
    PT_BTNS.append({"key": el_key, "rect": (bx, 10, btn_w, btn_h)})

def count_atom_bonds(atom):
    return sum(1 for b in bonds if not b.is_broken and (b.atom1 == atom or b.atom2 == atom))

def clear_scene():
    global atoms, bonds, particles, active_molecules, known_molecule_keys
    atoms.clear()
    bonds.clear()
    particles.clear()
    active_molecules.clear()
    known_molecule_keys.clear()

def set_experiment(exp_id):
    """Postavlja jedan od 6 predefinisanih hemijskih eksperimenata."""
    global current_experiment_id, current_experiment_name
    clear_scene()
    current_experiment_id = exp_id

    if exp_id == 1:
        # Voda (H2 + O -> H2O)
        current_experiment_name = "Voda (H2 + O -> H2O)"
        h1 = Atom("H", 180, 310)
        h2 = Atom("H", 260, 310)
        b_h2 = ChemicalBond(h1, h2)
        o1 = Atom("O", 460, 240)
        atoms.extend([h1, h2, o1])
        bonds.append(b_h2)
        print("[EKSPERIMENT 1] Voda: Razvuci vezu H-H obema rukama, pa spoji oba H sa O!")

    elif exp_id == 2:
        # Ugljen-dioksid (C + O2 -> CO2)
        current_experiment_name = "Ugljen-dioksid (C + O2 -> CO2)"
        o1 = Atom("O", 170, 310)
        o2 = Atom("O", 255, 310)
        b_o2 = ChemicalBond(o1, o2)
        c1 = Atom("C", 460, 240)
        atoms.extend([o1, o2, c1])
        bonds.append(b_o2)
        print("[EKSPERIMENT 2] Ugljen-dioksid: Pokidaj O-O vezu, pa spoji kiseonike sa C (O-C-O)!")

    elif exp_id == 3:
        # Kuhinjska so (Na + Cl -> NaCl)
        current_experiment_name = "Kuhinjska so (Na + Cl -> NaCl)"
        na = Atom("Na", 210, 250)
        cl = Atom("Cl", 430, 250)
        atoms.extend([na, cl])
        print("[EKSPERIMENT 3] Kuhinjska so: Prinesi natrijum (Na) i hlor (Cl) da formiras NaCl!")

    elif exp_id == 4:
        # Metan (C + 4H -> CH4)
        current_experiment_name = "Metan (C + 4H -> CH4)"
        c = Atom("C", 320, 240)
        h1 = Atom("H", 150, 160)
        h2 = Atom("H", 150, 320)
        h3 = Atom("H", 490, 160)
        h4 = Atom("H", 490, 320)
        atoms.extend([c, h1, h2, h3, h4])
        print("[EKSPERIMENT 4] Metan: Povezi 4 atoma vodonika (H) na centralni ugljenik (C)!")

    elif exp_id == 5:
        # Amonijak (N + 3H -> NH3)
        current_experiment_name = "Amonijak (N + 3H -> NH3)"
        n = Atom("N", 320, 220)
        h1 = Atom("H", 170, 180)
        h2 = Atom("H", 470, 180)
        h3 = Atom("H", 320, 360)
        atoms.extend([n, h1, h2, h3])
        print("[EKSPERIMENT 5] Amonijak: Spoj 3 vodonika (H) sa azotom (N) da napravis NH3!")

    elif exp_id == 6:
        # Hlorovodonik (H2 + Cl2 -> 2 HCl)
        current_experiment_name = "Hlorovodonik (H2 + Cl2 -> 2 HCl)"
        h1 = Atom("H", 170, 190)
        h2 = Atom("H", 250, 190)
        b_h = ChemicalBond(h1, h2)
        cl1 = Atom("Cl", 390, 290)
        cl2 = Atom("Cl", 480, 290)
        b_cl = ChemicalBond(cl1, cl2)
        atoms.extend([h1, h2, cl1, cl2])
        bonds.extend([b_h, b_cl])
        print("[EKSPERIMENT 6] Hlorovodonik: Raskini veze u gasovima H2 i Cl2, pa spoji H i Cl!")

# Inicijalni eksperiment
set_experiment(1)

# ================= PREPOZNAVANJE I SINTEZA MOLEKULA =================
def detect_molecules():
    """Analizira graf povezanih atoma i prepoznaje sintetisane molekule."""
    global active_molecules, known_molecule_keys

    # Izgradnja liste suseda
    adj = {a: [] for a in atoms}
    for b in bonds:
        if not b.is_broken:
            adj[b.atom1].append(b.atom2)
            adj[b.atom2].append(b.atom1)

    # Pronalazenje povezanih komponenti (molekula)
    visited = set()
    components = []
    for a in atoms:
        if a not in visited:
            comp = []
            q = [a]
            visited.add(a)
            while q:
                curr = q.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
            if len(comp) > 1:
                components.append(comp)

    found_molecules = []

    for comp in components:
        counts = {}
        for a in comp:
            counts[a.key] = counts.get(a.key, 0) + 1

        mol_info = None

        # 1. VODA (H2O): 1 O i 2 H, oba H vezana za O
        if counts == {"H": 2, "O": 1}:
            o_atom = next(a for a in comp if a.key == "O")
            if len(adj[o_atom]) == 2:
                mol_info = {
                    "type": "H2O",
                    "formula": "H2O",
                    "name": "VODA",
                    "sr_name": "Dihidrogen-monoksid",
                    "desc": "Uspesna sinteza! Osnova zivota na Zemlji.",
                    "center": (int(o_atom.x), int(o_atom.y)),
                    "center_atom": o_atom,
                    "atoms": comp,
                    "color": (255, 200, 50),
                    "sound": snd_water
                }

        # 2. UGLJEN-DIOKSID (CO2): 1 C i 2 O, oba O vezana za C
        elif counts == {"C": 1, "O": 2}:
            c_atom = next(a for a in comp if a.key == "C")
            if len(adj[c_atom]) == 2:
                mol_info = {
                    "type": "CO2",
                    "formula": "CO2",
                    "name": "UGLJEN-DIOKSID",
                    "sr_name": "Ugljenik(IV)-oksid",
                    "desc": "Gas neophodan biljkama za fotosintezu!",
                    "center": (int(c_atom.x), int(c_atom.y)),
                    "center_atom": c_atom,
                    "atoms": comp,
                    "color": (210, 210, 220),
                    "sound": snd_gas
                }

        # 3. KUHINJSKA SO (NaCl): 1 Na i 1 Cl
        elif counts == {"Na": 1, "Cl": 1}:
            na_atom = next(a for a in comp if a.key == "Na")
            cl_atom = next(a for a in comp if a.key == "Cl")
            cx = int((na_atom.x + cl_atom.x) / 2)
            cy = int((na_atom.y + cl_atom.y) / 2)
            mol_info = {
                "type": "NaCl",
                "formula": "NaCl",
                "name": "KUHINJSKA SO",
                "sr_name": "Natrijum-hlorid",
                "desc": "Stabilna jonska veza — zacin i esencijalni mineral!",
                "center": (cx, cy),
                "center_atom": na_atom,
                "atoms": comp,
                "color": (240, 140, 230),
                "sound": snd_crystal
            }

        # 4. METAN (CH4): 1 C i 4 H
        elif counts == {"C": 1, "H": 4}:
            c_atom = next(a for a in comp if a.key == "C")
            if len(adj[c_atom]) == 4:
                mol_info = {
                    "type": "CH4",
                    "formula": "CH4",
                    "name": "METAN",
                    "sr_name": "Ugljovodonik",
                    "desc": "Prirodni zemni gas — odlicno gorivo!",
                    "center": (int(c_atom.x), int(c_atom.y)),
                    "center_atom": c_atom,
                    "atoms": comp,
                    "color": (50, 180, 255),
                    "sound": snd_gas
                }

        # 5. AMONIJAK (NH3): 1 N i 3 H
        elif counts == {"N": 1, "H": 3}:
            n_atom = next(a for a in comp if a.key == "N")
            if len(adj[n_atom]) == 3:
                mol_info = {
                    "type": "NH3",
                    "formula": "NH3",
                    "name": "AMONIJAK",
                    "sr_name": "Azot-trihidrid",
                    "desc": "Karakteristican ostar miris — baza za djubriva!",
                    "center": (int(n_atom.x), int(n_atom.y)),
                    "center_atom": n_atom,
                    "atoms": comp,
                    "color": (245, 170, 90),
                    "sound": snd_acid
                }

        # 6. HLOROVODONIK (HCl): 1 H i 1 Cl
        elif counts == {"H": 1, "Cl": 1}:
            h_atom = next(a for a in comp if a.key == "H")
            cl_atom = next(a for a in comp if a.key == "Cl")
            cx = int((h_atom.x + cl_atom.x) / 2)
            cy = int((h_atom.y + cl_atom.y) / 2)
            mol_info = {
                "type": "HCl",
                "formula": "HCl",
                "name": "HLOROVODONIK",
                "sr_name": "Hlorovodonicna kiselina",
                "desc": "Jaka kiselina — sastojak ljudskog zeludacnog soka!",
                "center": (cx, cy),
                "center_atom": cl_atom,
                "atoms": comp,
                "color": (100, 240, 120),
                "sound": snd_acid
            }

        # 7. KISEONIK GAS (O2)
        elif counts == {"O": 2} and len(comp) == 2:
            cx = int((comp[0].x + comp[1].x) / 2)
            cy = int((comp[0].y + comp[1].y) / 2)
            mol_info = {
                "type": "O2",
                "formula": "O2",
                "name": "KISEONIK (GAS)",
                "sr_name": "Dvoatomski kiseonik",
                "desc": "Gas u vazduhu neophodan za disanje!",
                "center": (cx, cy),
                "center_atom": comp[0],
                "atoms": comp,
                "color": (80, 120, 255),
                "sound": snd_bond
            }

        # 8. VODONIK GAS (H2)
        elif counts == {"H": 2} and len(comp) == 2:
            cx = int((comp[0].x + comp[1].x) / 2)
            cy = int((comp[0].y + comp[1].y) / 2)
            mol_info = {
                "type": "H2",
                "formula": "H2",
                "name": "VODONIK (GAS)",
                "sr_name": "Dvoatomski vodonik",
                "desc": "Najlaksi i najrasprostranjeniji element u svemiru!",
                "center": (cx, cy),
                "center_atom": comp[0],
                "atoms": comp,
                "color": (220, 220, 240),
                "sound": snd_bond
            }

        if mol_info:
            found_molecules.append(mol_info)

            # Provera da li je ovaj molekul tek formiran
            comp_key = tuple(sorted([id(a) for a in comp]))
            if comp_key not in known_molecule_keys:
                known_molecule_keys.add(comp_key)
                play_sound(snd_fanfare)
                if mol_info["sound"]:
                    play_sound(mol_info["sound"])
                print(f"✨ [SINTEZA] USPESNO FORMIRAN MOLEKUL: {mol_info['name']} ({mol_info['formula']})!")

                # Eksplozija slavljenickih cestica
                mcx, mcy = mol_info["center"]
                for _ in range(40):
                    particles.append({
                        "x": mcx,
                        "y": mcy,
                        "vx": random.uniform(-6, 6),
                        "vy": random.uniform(-7, 3),
                        "color": mol_info["color"],
                        "size": random.randint(3, 8),
                        "life": random.randint(22, 45)
                    })

    active_molecules = found_molecules

# ================= AR EFEKTI I ISCRTAVANJE =================
water_bubbles = []
gas_wisps = []

def draw_molecule_effects(img):
    """Prikazuje specijalne AR efekte za svaki prepoznati molekul."""
    t = time.time()

    for mol in active_molecules:
        cx, cy = mol["center"]
        mtype = mol["type"]
        color = mol["color"]

        # 1. Efekat VODE (H2O)
        if mtype == "H2O":
            r_drop = 80 + int(math.sin(t * 3.5) * 5)
            overlay = img.copy()
            cv2.circle(overlay, (cx, cy), r_drop, (245, 170, 40), -1, cv2.LINE_AA)
            cv2.circle(overlay, (cx, cy), r_drop + 14, (255, 210, 80), -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.38, img, 0.62, 0, img)
            cv2.circle(img, (cx, cy), r_drop, (255, 235, 150), 2, cv2.LINE_AA)

            # Plivajuci mehurici
            if len(water_bubbles) < 18:
                water_bubbles.append({
                    "x": cx + random.randint(-55, 55),
                    "y": cy + random.randint(10, 60),
                    "r": random.randint(6, 18),
                    "vy": random.uniform(-2.5, -1.0),
                    "phase": random.uniform(0, 6.28)
                })

            for b in water_bubbles[:]:
                b["y"] += b["vy"]
                b["x"] += math.sin(b["phase"]) * 0.7
                b["phase"] += 0.08
                if b["y"] < cy - 110:
                    water_bubbles.remove(b)
                else:
                    cv2.circle(img, (int(b["x"]), int(b["y"])), int(b["r"]), (255, 240, 160), 2, cv2.LINE_AA)
                    cv2.circle(img, (int(b["x"]) - b["r"]//3, int(b["y"]) - b["r"]//3), max(2, b["r"]//4), (255, 255, 255), -1, cv2.LINE_AA)

        # 2. Efekat UGLJEN-DIOKSIDA (CO2)
        elif mtype == "CO2":
            r_gas = 75 + int(math.sin(t * 2.5) * 6)
            overlay = img.copy()
            cv2.circle(overlay, (cx, cy), r_gas, (180, 180, 190), -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.28, img, 0.72, 0, img)
            cv2.circle(img, (cx, cy), r_gas, (230, 230, 240), 1, cv2.LINE_AA)

            # Dimni prstenovi
            ring_r = int((t * 40) % 70) + 20
            ring_alpha = max(0, 1.0 - (ring_r / 90.0))
            if ring_alpha > 0.1:
                cv2.circle(img, (cx, cy), ring_r, (200, 200, 210), 1, cv2.LINE_AA)

        # 3. Efekat KUHINJSKE SOLI (NaCl)
        elif mtype == "NaCl":
            # Svetlucavi kristalni dijamant / oreol
            r_cryst = 70 + int(math.sin(t * 5.0) * 4)
            overlay = img.copy()
            pts = np.array([
                [cx, cy - r_cryst],
                [cx + r_cryst, cy],
                [cx, cy + r_cryst],
                [cx - r_cryst, cy]
            ], np.int32)
            cv2.fillPoly(overlay, [pts], (220, 120, 210))
            cv2.addWeighted(overlay, 0.30, img, 0.70, 0, img)
            cv2.polylines(img, [pts], True, (255, 220, 255), 2, cv2.LINE_AA)

            # Male svetlucave zvezdice
            for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
                rad = math.radians(ang + t * 40)
                sx = int(cx + math.cos(rad) * (r_cryst + 12))
                sy = int(cy + math.sin(rad) * (r_cryst + 12))
                cv2.circle(img, (sx, sy), 3, (255, 255, 255), -1, cv2.LINE_AA)

        # 4. Efekat METANA (CH4)
        elif mtype == "CH4":
            # Plavicasti plamen gasa
            r_flame = 85 + int(math.sin(t * 6.0) * 6)
            overlay = img.copy()
            cv2.circle(overlay, (cx, cy), r_flame, (255, 140, 30), -1, cv2.LINE_AA)
            cv2.circle(overlay, (cx, cy), r_flame - 20, (255, 220, 60), -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.32, img, 0.68, 0, img)

            # Plameni jeza / varnice
            for _ in range(2):
                ang = random.uniform(0, 6.28)
                dist = random.uniform(20, r_flame)
                fx = int(cx + math.cos(ang) * dist)
                fy = int(cy + math.sin(ang) * dist - random.randint(10, 25))
                cv2.circle(img, (fx, fy), random.randint(2, 5), (100, 220, 255), -1, cv2.LINE_AA)

        # 5. Efekat AMONIJAKA (NH3)
        elif mtype == "NH3":
            r_nh3 = 80 + int(math.sin(t * 3.0) * 5)
            overlay = img.copy()
            cv2.circle(overlay, (cx, cy), r_nh3, (220, 150, 60), -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.30, img, 0.70, 0, img)
            cv2.circle(img, (cx, cy), r_nh3, (255, 200, 120), 2, cv2.LINE_AA)

        # 6. Efekat HLOROVODONIKA (HCl)
        elif mtype == "HCl":
            r_hcl = 75 + int(math.sin(t * 4.0) * 5)
            overlay = img.copy()
            cv2.circle(overlay, (cx, cy), r_hcl, (60, 210, 80), -1, cv2.LINE_AA)
            cv2.addWeighted(overlay, 0.30, img, 0.70, 0, img)
            cv2.circle(img, (cx, cy), r_hcl, (180, 255, 180), 2, cv2.LINE_AA)

        # AR Informativni panel (Bedz) molekula
        bw, bh = 370, 60
        bx = cx - bw // 2
        by = cy - 110
        bx = max(10, min(WIDTH - bw - 10, bx))
        by = max(55, min(HEIGHT - bh - 60, by))

        overlay = img.copy()
        cv2.rectangle(overlay, (bx, by), (bx + bw, by + bh), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.82, img, 0.18, 0, img)
        cv2.rectangle(img, (bx, by), (bx + bw, by + bh), color, 2, cv2.LINE_AA)

        title = f"{mol['name']} ({mol['formula']}) - {mol['sr_name']}"
        cv2.putText(img, title, (bx + 12, by + 24),
                    cv2.FONT_HERSHEY_DUPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(img, mol["desc"], (bx + 12, by + 46),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)

# ================= MIŠ PODRŠKA (ZA TESTIRANJE NA RAČUNARU) =================
mouse_hand0 = {"pos": (0, 0), "down": False}
mouse_hand1 = {"pos": (0, 0), "down": False}

def on_mouse(event, x, y, flags, param):
    global mouse_hand0, mouse_hand1
    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_hand0["pos"] = (x, y)
        mouse_hand0["down"] = True
    elif event == cv2.EVENT_LBUTTONUP:
        mouse_hand0["down"] = False
    elif event == cv2.EVENT_RBUTTONDOWN:
        mouse_hand1["pos"] = (x, y)
        mouse_hand1["down"] = True
    elif event == cv2.EVENT_RBUTTONUP:
        mouse_hand1["down"] = False
    elif event == cv2.EVENT_MOUSEMOVE:
        if mouse_hand0["down"]:
            mouse_hand0["pos"] = (x, y)
        if mouse_hand1["down"]:
            mouse_hand1["pos"] = (x, y)

# ================= GLAVNA PETLJA PROGRAMA =================
vision = FastVisionHands2(WIDTH, HEIGHT)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, 1280, 720)
cv2.setMouseCallback(WINDOW_NAME, on_mouse)

print("=" * 70)
print("POKRENUTA 'AR HEMIJA — CEPANJE I SPAJANJE ATOMA' (RPi 5)")
print("Kontrole:")
print("  - Uhvatite atome obema rukama (palac + kaziprst) i razvucite da pukne veza!")
print("  - Prinesite atome jedan drugom da se spoje po hemijskim valencama")
print("  - [1-6] Brzi eksperimenti: 1:H2O | 2:CO2 | 3:NaCl | 4:CH4 | 5:NH3 | 6:HCl")
print("  - [p] Periodni sistem elemenata  |  [Space]/[r] Reset  |  [m] Zvuk  |  [q] Izlaz")
print("=" * 70)

last_spawn_time = 0

try:
    while True:
        frame, hands_list = vision.get_state()
        if frame is None:
            time.sleep(0.005)
            continue

        # Spoji MediaPipe ruke i mis (ako se testira na racunaru bez kamere)
        active_hands = list(hands_list)
        if mouse_hand0["down"]:
            active_hands.append({
                "thumb": mouse_hand0["pos"],
                "index": mouse_hand0["pos"],
                "pinch": mouse_hand0["pos"],
                "palm": mouse_hand0["pos"],
                "is_pinching": True,
                "dist": 10
            })
        if mouse_hand1["down"]:
            active_hands.append({
                "thumb": mouse_hand1["pos"],
                "index": mouse_hand1["pos"],
                "pinch": mouse_hand1["pos"],
                "palm": mouse_hand1["pos"],
                "is_pinching": True,
                "dist": 10
            })

        # 1. Resetovanje hvatanja atoma
        for a in atoms:
            a.grabbed_by = None

        # 2. Obrada stipanja prstima (Pinch)
        for hand_idx, h in enumerate(active_hands):
            px, py = h["pinch"]
            is_p = h["is_pinching"]

            ring_col = (0, 235, 255) if hand_idx == 0 else (60, 215, 255)
            cv2.circle(frame, h["thumb"], 7, ring_col, 2, cv2.LINE_AA)
            cv2.circle(frame, h["index"], 7, ring_col, 2, cv2.LINE_AA)

            if is_p:
                cv2.circle(frame, (px, py), 12, ring_col, -1, cv2.LINE_AA)
                cv2.circle(frame, (px, py), 16, (255, 255, 255), 2, cv2.LINE_AA)

                # Hvatanje atoma
                for a in atoms:
                    if a.grabbed_by is None and a.is_inside(px, py):
                        a.grabbed_by = hand_idx
                        a.x += (px - a.x) * 0.45
                        a.y += (py - a.y) * 0.45
                        break

                # Klik na Periodni sistem na vrhu ekrana
                if show_periodic_table and (time.time() - last_spawn_time > 0.6):
                    for btn in PT_BTNS:
                        bx, by, bw, bh = btn["rect"]
                        if bx <= px <= bx + bw and by <= py <= by + bh:
                            new_atom = Atom(btn["key"], px, py + 75)
                            atoms.append(new_atom)
                            play_sound(snd_bond)
                            last_spawn_time = time.time()
                            print(f"[PERIODNI SISTEM] Dodat novi atom: {btn['key']} ({ELEMENTS[btn['key']]['sr_name']})")
                            break

        # 3. Azuriranje hemijskih veza i provera CEPANJA (Breaking bonds)
        for b in bonds[:]:
            b.update()
            # Ako oba atoma drze razlicite ruke i razvuku se preko granice pucanja
            if b.atom1.grabbed_by is not None and b.atom2.grabbed_by is not None:
                if b.atom1.grabbed_by != b.atom2.grabbed_by:
                    dist = b.get_length()
                    if dist > (b.rest_length + 105):  # Granica pucanja veze
                        b.is_broken = True
                        bonds.remove(b)
                        play_sound(snd_snap)

                        mx, my = (b.atom1.x + b.atom2.x) / 2, (b.atom1.y + b.atom2.y) / 2
                        for _ in range(32):
                            particles.append({
                                "x": mx,
                                "y": my,
                                "vx": random.uniform(-6, 6),
                                "vy": random.uniform(-6, 6),
                                "color": random.choice([(0, 240, 255), (255, 255, 255), (30, 80, 255)]),
                                "size": random.randint(3, 7),
                                "life": random.randint(18, 32)
                            })
                        print(f"💥 [CEPANJE] Hemijska veza {b.atom1.key} - {b.atom2.key} je raskinuta!")

        # 4. Provera SPAJANJA atoma po hemijskim valencama
        for i in range(len(atoms)):
            for j in range(i + 1, len(atoms)):
                a1 = atoms[i]
                a2 = atoms[j]

                # Provera da vec nisu povezani
                already_bonded = any(
                    (b.atom1 == a1 and b.atom2 == a2) or (b.atom1 == a2 and b.atom2 == a1)
                    for b in bonds if not b.is_broken
                )

                if not already_bonded:
                    dist = math.hypot(a1.x - a2.x, a1.y - a2.y)
                    # Ako su prineseni dovoljno blizu
                    if dist < (a1.radius + a2.radius + 36):
                        # Provera dozvoljenog para i dostupnih valenci
                        pair = frozenset([a1.key, a2.key])
                        if pair in ALLOWED_PAIRS:
                            bonds_1 = count_atom_bonds(a1)
                            bonds_2 = count_atom_bonds(a2)
                            val_1 = a1.data["val"]
                            val_2 = a2.data["val"]

                            if bonds_1 < val_1 and bonds_2 < val_2:
                                new_b = ChemicalBond(a1, a2)
                                bonds.append(new_b)
                                play_sound(snd_bond)

                                # Blesak spajanja
                                for _ in range(16):
                                    particles.append({
                                        "x": (a1.x + a2.x) / 2,
                                        "y": (a1.y + a2.y) / 2,
                                        "vx": random.uniform(-4, 4),
                                        "vy": random.uniform(-4, 4),
                                        "color": (255, 255, 255),
                                        "size": random.randint(2, 6),
                                        "life": random.randint(12, 22)
                                    })
                                print(f"✨ [SPAJANJE] Formirana hemijska veza: {a1.key} ({a1.data['sr_name']}) - {a2.key} ({a2.data['sr_name']})")

        # 5. Detekcija formiranih molekula
        detect_molecules()

        # 6. Iscrtavanje hemijskih veza
        for b in bonds:
            b.draw(frame)

        # 7. Iscrtavanje atoma
        for a in atoms:
            a.draw(frame, is_grabbed=(a.grabbed_by is not None))

        # 8. Iscrtavanje specijalnih AR efekata i bedzeva molekula
        draw_molecule_effects(frame)

        # 9. Azuriranje i iscrtavanje cestica
        for p in particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] <= 0:
                particles.remove(p)
            else:
                cv2.circle(frame, (int(p["x"]), int(p["y"])), p["size"], p["color"], -1, cv2.LINE_AA)

        # 10. Periodni sistem elemenata (Meni na vrhu)
        if show_periodic_table:
            overlay = frame.copy()
            cv2.rectangle(overlay, (start_x - 18, 4), (start_x + len(PT_ELEMENTS)*(btn_w + 10) + 8, 72), (25, 20, 32), -1)
            cv2.addWeighted(overlay, 0.80, frame, 0.20, 0, frame)

            title_pt = "PERIODNI SISTEM ELEMENATA (Stipni ili klikni za dodavanje)"
            cv2.putText(frame, title_pt, (start_x - 10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 240, 255), 1, cv2.LINE_AA)

            for btn in PT_BTNS:
                bx, by, bw, bh = btn["rect"]
                by_mod = by + 12
                el = ELEMENTS[btn["key"]]
                cv2.rectangle(frame, (bx, by_mod), (bx + bw, by_mod + bh), el["color"], -1)
                cv2.rectangle(frame, (bx, by_mod), (bx + bw, by_mod + bh), (255, 255, 255), 2)

                tsize = cv2.getTextSize(el["symbol"], cv2.FONT_HERSHEY_DUPLEX, 0.62, 2)[0]
                tx = bx + (bw - tsize[0]) // 2
                ty = by_mod + 26
                tcol = (20, 20, 20) if el["symbol"] == "H" else (255, 255, 255)
                cv2.putText(frame, el["symbol"], (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.62, tcol, 2, cv2.LINE_AA)

                # Atomski broj Z
                cv2.putText(frame, str(el["z"]), (bx + 4, by_mod + 12),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.32, tcol, 1, cv2.LINE_AA)
                # Srpski naziv
                cv2.putText(frame, el["short_sr"], (bx + 3, by_mod + bh - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.30, tcol, 1, cv2.LINE_AA)

        # 11. Donja traka: Precice eksperimenata i status (Sve na srpskom)
        # Linija 1: Precice za eksperimente
        cv2.rectangle(frame, (8, HEIGHT - 52), (WIDTH - 8, HEIGHT - 6), (20, 20, 28), -1)
        cv2.rectangle(frame, (8, HEIGHT - 52), (WIDTH - 8, HEIGHT - 6), (60, 60, 75), 1)

        exp_bar = "[1] Voda (H2O)  [2] CO2  [3] So (NaCl)  [4] Metan (CH4)  [5] Amonijak  [6] HCl"
        cv2.putText(frame, exp_bar, (16, HEIGHT - 33),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 225, 255), 1, cv2.LINE_AA)

        # Linija 2: Trenutni status i kontrole
        if active_molecules:
            active_names = ", ".join([f"{m['name']} ({m['formula']})" for m in active_molecules])
            status_text = f"Sinteza uspela: {active_names}"
            status_col = (50, 255, 120)
        else:
            status_text = f"Eksperiment {current_experiment_id}: {current_experiment_name}"
            status_col = (240, 240, 240)

        cv2.putText(frame, status_text, (16, HEIGHT - 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, status_col, 1, cv2.LINE_AA)

        pt_toggle_col = (0, 240, 255) if show_periodic_table else (160, 160, 175)
        cv2.putText(frame, "[P] Periodni  [R] Reset  [M] Zvuk  [Q] Izlaz", (WIDTH - 280, HEIGHT - 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, pt_toggle_col, 1, cv2.LINE_AA)

        cv2.imshow(WINDOW_NAME, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('p'):
            show_periodic_table = not show_periodic_table
        elif key == ord('r') or key == ord(' '):
            set_experiment(current_experiment_id)
        elif key == ord('1'):
            set_experiment(1)
        elif key == ord('2'):
            set_experiment(2)
        elif key == ord('3'):
            set_experiment(3)
        elif key == ord('4'):
            set_experiment(4)
        elif key == ord('5'):
            set_experiment(5)
        elif key == ord('6'):
            set_experiment(6)
        elif key == ord('m'):
            sound_enabled = not sound_enabled
            print(f"[ZVUK] {'Ukljucen' if sound_enabled else 'Iskljucen'}")

finally:
    vision.stop()
    cv2.destroyAllWindows()
    print("[INFO] AR Hemija zavrsena.")
