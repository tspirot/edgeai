#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
     RPLIDAR C1 — MATRIX FACE CONTOURS & HOLOGRAPHIC SCANNER (RPi 5)
================================================================================
Aplikacija koja na osnovu merenja sa Slamtec RPLIDAR C1 laserskog senzora
rekonstruiše i iscrtava konture lica u prepoznatljivom "Matrix" sajber stilu:
- Digitalna zelena kiša (Matrix Digital Rain)
- 3D žičani (Wireframe) model lica koji se deformiše, rotira i približava
  u zavisnosti od stvarne udaljenosti i ugla glave detektovane LiDAR-om
- Horizontalni laserski profil lica (nos, obrazi, profil) mapiran u realnom vremenu
- Mogućnost rada sa pravim senzorom ili u interaktivnoj simulaciji (taster 's')
"""

import os
import sys
import time
import math
import random
import threading
import numpy as np
import cv2

# Osiguravanje prikaza na lokalnom TV ekranu kada se pokreće preko SSH
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

try:
    import serial
    import serial.tools.list_ports
    from rplidar import RPLidar
    LIDAR_AVAILABLE = True
except ImportError:
    LIDAR_AVAILABLE = False

# ------------------------------------------------------------------------------
# PODEŠAVANJA PRIKAZA I TEMA
# ------------------------------------------------------------------------------
WIN_W = 1024
WIN_H = 720
DEFAULT_BAUDRATE = 460800

THEMES = [
    {
        "name": "Classic Matrix (Zeleni fosfor)",
        "bg": (6, 12, 8),
        "primary": (0, 255, 100),       # Jarko zelena
        "secondary": (0, 180, 70),      # Srednje zelena
        "dark": (0, 60, 25),           # Tamno zelena
        "highlight": (180, 255, 200),   # Beličasto zelena (glava kiše)
        "alert": (0, 0, 255),          # Crvena za opasnost
        "hud": (0, 230, 90)
    },
    {
        "name": "Cyberpunk Cyan (Tron stil)",
        "bg": (8, 12, 20),
        "primary": (255, 230, 0),       # Cijan
        "secondary": (200, 150, 0),     # Plava
        "dark": (80, 50, 10),
        "highlight": (255, 255, 200),
        "alert": (0, 140, 255),
        "hud": (255, 200, 0)
    },
    {
        "name": "Zion Alert (Crveni alarm)",
        "bg": (16, 6, 6),
        "primary": (40, 50, 255),       # Jarko crvena
        "secondary": (20, 30, 180),
        "dark": (10, 15, 70),
        "highlight": (200, 200, 255),
        "alert": (0, 255, 255),
        "hud": (50, 80, 255)
    }
]

# ------------------------------------------------------------------------------
# 3D KONTURE I TAČKE MODELA LICA (KANONSKA TOPOLOGIJA)
# ------------------------------------------------------------------------------
# x, y, z koordinate normalizovane u opsegu [-1.0, 1.0]
# z ide prema napred (nos ima najveći z)
BASE_FACE_POINTS = np.array([
    # Kontura vilice i brade (0-8)
    [-0.85, -0.20, -0.40],  # 0: Levo uvo / gornja vilica
    [-0.75,  0.20, -0.30],  # 1: Leva vilica
    [-0.55,  0.55, -0.15],  # 2: Donja leva vilica
    [-0.30,  0.80,  0.05],  # 3: Leva strana brade
    [ 0.00,  0.92,  0.20],  # 4: Vrh brade
    [ 0.30,  0.80,  0.05],  # 5: Desna strana brade
    [ 0.55,  0.55, -0.15],  # 6: Donja desna vilica
    [ 0.75,  0.20, -0.30],  # 7: Desna vilica
    [ 0.85, -0.20, -0.40],  # 8: Desno uvo / gornja vilica

    # Čelo i gornji luk lobanje (9-13)
    [-0.70, -0.55, -0.25],  # 9: Levo slepoočnica
    [-0.40, -0.80, -0.10],  # 10: Levo gornje čelo
    [ 0.00, -0.88,  0.00],  # 11: Centar čela vrh
    [ 0.40, -0.80, -0.10],  # 12: Desno gornje čelo
    [ 0.70, -0.55, -0.25],  # 13: Desna slepoočnica

    # Obrve (14-19)
    [-0.55, -0.38, -0.05],  # 14: Leva obrva spolja
    [-0.35, -0.44,  0.05],  # 15: Leva obrva sredina
    [-0.12, -0.40,  0.15],  # 16: Leva obrva unutra
    [ 0.12, -0.40,  0.15],  # 17: Desna obrva unutra
    [ 0.35, -0.44,  0.05],  # 18: Desna obrva sredina
    [ 0.55, -0.38, -0.05],  # 19: Desna obrva spolja

    # Oči (20-27)
    [-0.48, -0.26, -0.02],  # 20: Levo oko spolja
    [-0.32, -0.30,  0.02],  # 21: Levo oko gore
    [-0.18, -0.26,  0.08],  # 22: Levo oko unutra
    [-0.32, -0.22,  0.00],  # 23: Levo oko dole
    [ 0.18, -0.26,  0.08],  # 24: Desno oko unutra
    [ 0.32, -0.30,  0.02],  # 25: Desno oko gore
    [ 0.48, -0.26, -0.02],  # 26: Desno oko spolja
    [ 0.32, -0.22,  0.00],  # 27: Desno oko dole

    # Nos (28-33)
    [ 0.00, -0.30,  0.22],  # 28: Koren nosa
    [ 0.00, -0.08,  0.35],  # 29: Greben nosa
    [ 0.00,  0.12,  0.50],  # 30: Vrh nosa (najistureniji)
    [-0.15,  0.15,  0.28],  # 31: Leva nozdrva
    [ 0.15,  0.15,  0.28],  # 32: Desna nozdrva
    [ 0.00,  0.22,  0.32],  # 33: Dno nosa

    # Usta (34-41)
    [-0.28,  0.42,  0.15],  # 34: Levi ugao usana
    [-0.12,  0.36,  0.24],  # 35: Gornja usna levo
    [ 0.00,  0.38,  0.28],  # 36: Gornja usna centar
    [ 0.12,  0.36,  0.24],  # 37: Gornja usna desno
    [ 0.28,  0.42,  0.15],  # 38: Desni ugao usana
    [ 0.14,  0.54,  0.22],  # 39: Donja usna desno
    [ 0.00,  0.56,  0.25],  # 40: Donja usna centar
    [-0.14,  0.54,  0.22],  # 41: Donja usna levo

    # Jagodice obraza (42-45)
    [-0.50,  0.05,  0.05],  # 42: Leva jagodica
    [-0.28,  0.08,  0.18],  # 43: Levi unutrašnji obraz
    [ 0.28,  0.08,  0.18],  # 44: Desni unutrašnji obraz
    [ 0.50,  0.05,  0.05],  # 45: Desna jagodica
], dtype=np.float32)

# Linijske veze (Wireframe linije lica)
FACE_CONNECTIONS = [
    # Vilica
    (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8),
    # Čelo
    (0, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 8),
    # Obrve
    (14, 15), (15, 16), (16, 28), (28, 17), (17, 18), (18, 19),
    # Levo oko
    (20, 21), (21, 22), (22, 23), (23, 20),
    # Desno oko
    (24, 25), (25, 26), (26, 27), (27, 24),
    # Nos
    (28, 29), (29, 30), (30, 31), (30, 32), (31, 33), (32, 33), (29, 33),
    # Usta
    (34, 35), (35, 36), (36, 37), (37, 38), (38, 39), (39, 40), (40, 41), (41, 34),
    (34, 36), (36, 38), (34, 40), (38, 40),
    # Obrazi i struktura
    (2, 42), (42, 20), (42, 43), (43, 31), (43, 34),
    (6, 45), (45, 26), (45, 44), (44, 32), (44, 38),
    (11, 28), (4, 40), (9, 14), (13, 19),
    (10, 15), (12, 18), (16, 22), (17, 24)
]


# ------------------------------------------------------------------------------
# DIGITALNA MATRIX KIŠA (MATRIX DIGITAL RAIN)
# ------------------------------------------------------------------------------
class MatrixRain:
    def __init__(self, width, height, col_width=18):
        self.w = width
        self.h = height
        self.col_w = col_width
        self.num_cols = width // col_width
        self.chars = "0123456789ABCDEFｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜ"
        self.drops = [random.randint(-50, 0) for _ in range(self.num_cols)]
        self.speeds = [random.randint(1, 3) for _ in range(self.num_cols)]
        self.lens = [random.randint(8, 22) for _ in range(self.num_cols)]

    def update_and_draw(self, canvas, theme):
        overlay = np.zeros_like(canvas)
        for i in range(self.num_cols):
            x = i * self.col_w + 4
            head_y = self.drops[i]
            length = self.lens[i]

            for j in range(length):
                char_y = head_y - j * 16
                if 0 <= char_y < self.h - 10:
                    char = random.choice(self.chars)
                    if j == 0:
                        # Glava kapi svetli skoro belo/svetlo zeleno
                        col = theme["highlight"]
                    elif j < 3:
                        col = theme["primary"]
                    else:
                        # Bledi ka tamno zelenoj
                        col = theme["dark"]

                    cv2.putText(overlay, char, (x, char_y),
                                cv2.FONT_HERSHEY_PLAIN, 0.9, col, 1, cv2.LINE_AA)

            self.drops[i] += self.speeds[i]
            if self.drops[i] - length * 16 > self.h:
                self.drops[i] = random.randint(-40, 0)
                self.speeds[i] = random.randint(1, 3)
                self.lens[i] = random.randint(8, 22)

        # Polu-transparentno dodavanje kiše preko pozadine
        cv2.add(canvas, overlay, canvas)


# ------------------------------------------------------------------------------
# LIDAR ANALIZA I PRAĆENJE GLAVE / LICA
# ------------------------------------------------------------------------------
class LidarFaceTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.running = True
        self.connected = False
        self.simulation_mode = False
        self.port_name = "Nije pronađen"

        # Telemetrija lica dobijena sa LiDAR-a
        self.target_detected = False
        self.face_dist_cm = 85.0          # Udaljenost lica od senzora
        self.face_angle_deg = 0.0         # Horizontalni ugao (-45 do +45)
        self.face_width_cm = 20.0         # Širina detektovanog profila
        self.head_yaw = 0.0               # Procenjen zakret glave (radijani)
        self.scan_points_frontal = []     # (ugao, dist_mm) frontalnog luka
        self.total_points = 0
        self.scan_rate_hz = 10.0
        self.closest_dist_cm = 85.0

    def find_port(self):
        for p in ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]:
            if os.path.exists(p):
                return p
        try:
            for p in serial.tools.list_ports.comports():
                desc = p.description.lower()
                if any(k in desc for k in ["cp210", "ch340", "ftdi", "rplidar", "usb serial"]):
                    return p.device
        except Exception:
            pass
        return None

    def worker_loop(self):
        lidar = None
        while self.running:
            if self.simulation_mode:
                time.sleep(0.05)
                continue

            port = self.find_port()
            if not port:
                with self.lock:
                    self.connected = False
                    self.port_name = "Čekam USB..."
                time.sleep(1.0)
                continue

            with self.lock:
                self.port_name = port

            try:
                print(f"[MATRIX LIDAR] Otvaram {port} na {DEFAULT_BAUDRATE} baud...")
                lidar = RPLidar(port, baudrate=DEFAULT_BAUDRATE, timeout=2)
                lidar.start_motor()
                time.sleep(0.5)

                with self.lock:
                    self.connected = True
                print("[MATRIX LIDAR] Senzor povezan i motor pokrenut!")

                scan_start = time.time()
                scans_c = 0

                for scan in lidar.iter_scans(max_buf_meas=800):
                    if not self.running or self.simulation_mode:
                        break

                    now = time.time()
                    scans_c += 1
                    if now - scan_start >= 1.0:
                        with self.lock:
                            self.scan_rate_hz = scans_c / (now - scan_start)
                        scans_c = 0
                        scan_start = now

                    # Izdvajanje frontalnih tačaka (od -50° do +50°, tj. 310° do 50°)
                    frontal_pts = []
                    for q, angle, dist_mm in scan:
                        if dist_mm <= 0:
                            continue
                        # Normalizacija ugla na raspon [-180, 180]
                        norm_angle = angle if angle <= 180 else angle - 360
                        # Zadrži objekte u zoni glave/tela: 25cm do 180cm, u uglu [-50, +50] stepeni
                        if -50 <= norm_angle <= 50 and 250 <= dist_mm <= 1800:
                            frontal_pts.append((norm_angle, dist_mm))

                    self.process_frontal_scan(frontal_pts)

            except Exception as e:
                print(f"[MATRIX LIDAR] Greška: {e}")
                with self.lock:
                    self.connected = False
            finally:
                if lidar:
                    try:
                        lidar.stop()
                        lidar.stop_motor()
                        lidar.disconnect()
                    except Exception:
                        pass
                time.sleep(1.0)

    def process_frontal_scan(self, pts):
        """Analizira frontalne tačke LiDAR-a i pronalazi profil lica/glave."""
        if not pts:
            with self.lock:
                self.target_detected = False
                self.scan_points_frontal = []
            return

        # Sortiraj po uglu
        pts.sort(key=lambda x: x[0])

        # Pronađi najistureniju tačku (najmanja udaljenost = nos / lice)
        min_pt = min(pts, key=lambda x: x[1])
        min_ang, min_d_mm = min_pt

        # Izdvoj tačke koje pripadaju istom telu/glavi (unutar 25 cm od najisturenije tačke)
        cluster = [p for p in pts if abs(p[1] - min_d_mm) < 260 and abs(p[0] - min_ang) < 25]

        with self.lock:
            self.scan_points_frontal = pts
            self.total_points = len(pts)

            if len(cluster) >= 4:
                self.target_detected = True
                # Centar lica po uglovima
                avg_ang = sum(p[0] for p in cluster) / len(cluster)
                avg_d_cm = (min_d_mm / 10.0)

                # Širina klastera u cm
                min_a = min(p[0] for p in cluster)
                max_a = max(p[0] for p in cluster)
                arc_rad = math.radians(max_a - min_a)
                width_cm = 2 * (avg_d_cm * math.tan(arc_rad / 2.0))

                # Procena zakreta glave (yaw) na osnovu asimetrije rastojanja leve i desne strane
                left_pts = [p[1] for p in cluster if p[0] < avg_ang - 4]
                right_pts = [p[1] for p in cluster if p[0] > avg_ang + 4]
                yaw_est = 0.0
                if left_pts and right_pts:
                    diff_mm = (sum(right_pts)/len(right_pts)) - (sum(left_pts)/len(left_pts))
                    yaw_est = np.clip(diff_mm / 120.0, -0.6, 0.6)

                # Glatko filtriranje vrednosti (Low-pass)
                self.face_dist_cm = self.face_dist_cm * 0.75 + avg_d_cm * 0.25
                self.face_angle_deg = self.face_angle_deg * 0.75 + avg_ang * 0.25
                self.head_yaw = self.head_yaw * 0.75 + yaw_est * 0.25
                self.face_width_cm = np.clip(width_cm, 12, 35)
                self.closest_dist_cm = avg_d_cm
            else:
                self.target_detected = False

    def update_simulation(self):
        """Generiše dinamično virtuelno kretanje lica kada nema senzora."""
        t = time.time()
        with self.lock:
            self.connected = True
            self.port_name = "SIMULACIJA (Demo)"
            self.target_detected = True

            # Glatko pomeranje glave u prostoru
            self.face_dist_cm = 80.0 + math.sin(t * 0.8) * 25.0
            self.face_angle_deg = math.sin(t * 1.2) * 18.0
            self.head_yaw = math.sin(t * 1.2) * 0.45
            self.face_width_cm = 20.0
            self.closest_dist_cm = self.face_dist_cm

            # Generiši frontalni LiDAR profil (nos u centru isturen, obrazi nazad)
            sim_pts = []
            for a in range(-40, 41, 2):
                rad = math.radians(a - self.face_angle_deg)
                # Model profila nosa i lica
                nose_profile = math.exp(- (abs(a - self.face_angle_deg) / 8.0)**2) * 80.0
                d_mm = (self.face_dist_cm * 10.0) - nose_profile + (math.sin(a * 4 + t) * 6.0)
                sim_pts.append((a, d_mm))
            self.scan_points_frontal = sim_pts
            self.total_points = len(sim_pts)


# ------------------------------------------------------------------------------
# 3D ROTACIJA I PROJEKCIJA MODELA LICA NA EKRAN
# ------------------------------------------------------------------------------
def projektuj_3d_lice(pts_3d, yaw, pitch, scale, offset_x, offset_y):
    """
    Rotira 3D tačke lica po yaw/pitch uglovima i projektuje na 2D ekran.
    """
    # Matrica rotacije oko Y ose (Yaw - okretanje glave levo/desno)
    cos_y, sin_y = math.cos(yaw), math.sin(yaw)
    rot_y = np.array([
        [ cos_y, 0, sin_y],
        [     0, 1,     0],
        [-sin_y, 0, cos_y]
    ], dtype=np.float32)

    # Matrica rotacije oko X ose (Pitch - klimanje gore/dole)
    cos_p, sin_p = math.cos(pitch), math.sin(pitch)
    rot_x = np.array([
        [1,      0,       0],
        [0,  cos_p,  -sin_p],
        [0,  sin_p,   cos_p]
    ], dtype=np.float32)

    rot_mat = np.dot(rot_y, rot_x)
    rotated = np.dot(pts_3d, rot_mat.T)

    # Perspektivna projekcija: tačke bliže posmatraču (veći z) su šire
    projected_2d = []
    for x, y, z in rotated:
        persp = 1.0 + (z * 0.28)
        px = int(offset_x + (x * scale * persp))
        py = int(offset_y + (y * scale * persp))
        projected_2d.append((px, py, z))

    return projected_2d


# ------------------------------------------------------------------------------
# ISCRTAVANJE MATRIX HOLOGRAFSKOG LICA I LASERSKIH KONTURA
# ------------------------------------------------------------------------------
def nacrtaj_matrix_hologram(canvas, tracker, theme, rain_active):
    cx = WIN_W // 2
    cy = WIN_H // 2 + 10

    with tracker.lock:
        is_conn = tracker.connected
        detected = tracker.target_detected
        dist_cm = tracker.face_dist_cm
        angle_deg = tracker.face_angle_deg
        yaw = tracker.head_yaw
        port = tracker.port_name
        pts_frontal = list(tracker.scan_points_frontal)
        closest_cm = tracker.closest_dist_cm
        scan_hz = tracker.scan_rate_hz

    # 1. Skaliranje i pozicija lica direktno na osnovu udaljenosti sa LiDAR-a!
    # Bliže senzor -> Veće lice na ekranu!
    # Optimalna udaljenost je 40cm do 150cm
    clamped_dist = np.clip(dist_cm, 35.0, 180.0)
    # Inverse scale (manje cm = veći model)
    scale = (85.0 / clamped_dist) * 220.0
    scale = np.clip(scale, 110.0, 360.0)

    # Horizontalni pomak lica na osnovu ugla detekcije
    offset_x = cx + int(angle_deg * 7.5)
    offset_y = cy

    # Blagi pitch efekat u zavisnosti od udaljenosti
    pitch = (dist_cm - 80.0) * 0.002

    # 2. Deformacija lica laserskim profilom LiDAR-a
    # Modifikujemo z-koordinate lica u realnom vremenu
    deformed_pts = BASE_FACE_POINTS.copy()

    # Ako je detektovan frontalni profil, mapiramo horizontalne izbočine
    if pts_frontal and detected:
        # Pretvori tačke u lasersku mapu reljefa
        for idx in range(len(deformed_pts)):
            pt_x = deformed_pts[idx, 0]
            # Mapiraj x na ugao
            target_deg = angle_deg + (pt_x * 16.0)
            # Nađi najbliže merenje sa LiDAR-a
            matching = [p[1] for p in pts_frontal if abs(p[0] - target_deg) < 4.0]
            if matching:
                measured_cm = min(matching) / 10.0
                depth_diff = (dist_cm - measured_cm) * 0.08
                deformed_pts[idx, 2] += np.clip(depth_diff, -0.25, 0.45)

    # 3. 3D Projekcija
    proj_pts = projektuj_3d_lice(deformed_pts, yaw, pitch, scale, offset_x, offset_y)

    # 4. Laserska linija skeniranja preko lica (Sweeping Cyber Scanline)
    sweep_t = (time.time() * 2.2) % (math.pi * 2)
    scan_y = int(offset_y + math.sin(sweep_t) * (scale * 0.85))
    scan_w = int(scale * 1.1)

    # Zeleni sjaj laserskog snopa
    scan_glow = np.zeros_like(canvas)
    cv2.line(scan_glow, (offset_x - scan_w, scan_y), (offset_x + scan_w, scan_y), theme["primary"], 2, cv2.LINE_AA)
    cv2.line(scan_glow, (offset_x - scan_w, scan_y), (offset_x + scan_w, scan_y), theme["highlight"], 1, cv2.LINE_AA)
    cv2.addWeighted(canvas, 1.0, scan_glow, 0.7, 0, canvas)

    # 5. Iscrtavanje Wireframe mreže lica u Matrix stilu
    for p1_idx, p2_idx in FACE_CONNECTIONS:
        x1, y1, z1 = proj_pts[p1_idx]
        x2, y2, z2 = proj_pts[p2_idx]

        # Boja linije: istureniji delovi lica (nos, brada) svetle jarkije!
        avg_z = (z1 + z2) / 2.0
        if avg_z > 0.15:
            line_col = theme["highlight"]
            line_w = 2
        elif avg_z > -0.10:
            line_col = theme["primary"]
            line_w = 1
        else:
            line_col = theme["secondary"]
            line_w = 1

        cv2.line(canvas, (x1, y1), (x2, y2), line_col, line_w, cv2.LINE_AA)

    # 6. Tačke i čvorovi lica (Cybernetic Nodes)
    for idx, (px, py, z) in enumerate(proj_pts):
        if z > 0.20:
            # Ključne tačke lica (vrh nosa, oči, uglovi usta) imaju pulsirajući sjaj
            cv2.circle(canvas, (px, py), 4, theme["highlight"], -1, cv2.LINE_AA)
            cv2.circle(canvas, (px, py), 7, theme["primary"], 1, cv2.LINE_AA)
        else:
            cv2.circle(canvas, (px, py), 2, theme["primary"], -1, cv2.LINE_AA)

    # 7. Holografski nišanski okvir oko lica (HUD Target Box)
    box_w = int(scale * 1.15)
    box_h = int(scale * 1.35)
    bx1 = offset_x - box_w
    bx2 = offset_x + box_w
    by1 = offset_y - box_h
    by2 = offset_y + box_h

    # Uglovi nišana (Target Brackets)
    c_len = 24
    hud_col = theme["hud"] if detected else (0, 140, 255)

    # Top-Left
    cv2.line(canvas, (bx1, by1), (bx1 + c_len, by1), hud_col, 2, cv2.LINE_AA)
    cv2.line(canvas, (bx1, by1), (bx1, by1 + c_len), hud_col, 2, cv2.LINE_AA)
    # Top-Right
    cv2.line(canvas, (bx2, by1), (bx2 - c_len, by1), hud_col, 2, cv2.LINE_AA)
    cv2.line(canvas, (bx2, by1), (bx2, by1 + c_len), hud_col, 2, cv2.LINE_AA)
    # Bottom-Left
    cv2.line(canvas, (bx1, by2), (bx1 + c_len, by2), hud_col, 2, cv2.LINE_AA)
    cv2.line(canvas, (bx1, by2), (bx1, by2 - c_len), hud_col, 2, cv2.LINE_AA)
    # Bottom-Right
    cv2.line(canvas, (bx2, by2), (bx2 - c_len, by2), hud_col, 2, cv2.LINE_AA)
    cv2.line(canvas, (bx2, by2), (bx2, by2 - c_len), hud_col, 2, cv2.LINE_AA)

    # Oznaka iznad nišana
    status_tag = f"BIO-META LICE [ {dist_cm:.1f} cm ]" if detected else "TRAŽIM PROFIL LICA..."
    cv2.putText(canvas, status_tag, (bx1, by1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, hud_col, 1, cv2.LINE_AA)

    # 8. Mini radarski prikaz laserskog profila u donjem desnom uglu
    renderuj_mini_lidar_profil(canvas, pts_frontal, dist_cm, theme)


def renderuj_mini_lidar_profil(canvas, pts_frontal, center_dist_cm, theme):
    """Prikazuje stvarni horizontalni 2D presek laserskih tačaka sa LiDAR-a."""
    mx, my = WIN_W - 240, WIN_H - 180
    mw, mh = 210, 150

    # Polu-transparentni mini HUD okvir
    cv2.rectangle(canvas, (mx, my), (mx + mw, my + mh), (10, 18, 14), -1)
    cv2.rectangle(canvas, (mx, my), (mx + mw, my + mh), theme["dark"], 1)

    cv2.putText(canvas, "LiDAR LASERSKI PROSEK", (mx + 10, my + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, theme["hud"], 1)

    # Centar senzora u mini mapi
    sm_cx = mx + mw // 2
    sm_cy = my + mh - 15
    cv2.circle(canvas, (sm_cx, sm_cy), 4, (255, 255, 255), -1)

    # Iscrtaj frontalne tačke u mini mapi
    if pts_frontal:
        for ang, d_mm in pts_frontal:
            rad = math.radians(ang)
            # Skaliranje za mini prozor (maksimalno 2 metra)
            d_px = (d_mm / 2000.0) * 110.0
            px = int(sm_cx + d_px * math.sin(rad))
            py = int(sm_cy - d_px * math.cos(rad))
            if mx + 2 < px < mx + mw - 2 and my + 25 < py < my + mh - 2:
                cv2.circle(canvas, (px, py), 2, theme["primary"], -1)

        # Spoji tačke lica linijom da se vidi stvarna kontura nosa i lica!
        near_pts = sorted([p for p in pts_frontal if abs(p[1] - center_dist_cm * 10) < 250], key=lambda x: x[0])
        if len(near_pts) > 2:
            poly = []
            for ang, d_mm in near_pts:
                rad = math.radians(ang)
                d_px = (d_mm / 2000.0) * 110.0
                poly.append((int(sm_cx + d_px * math.sin(rad)), int(sm_cy - d_px * math.cos(rad))))
            for k in range(len(poly) - 1):
                cv2.line(canvas, poly[k], poly[k+1], theme["highlight"], 1, cv2.LINE_AA)


def renderuj_matrix_hud(canvas, tracker, theme, theme_idx):
    """Gornja i bočna telemetrija u Matrix sajber stilu."""
    # Gornja info traka
    cv2.putText(canvas, "SYSTEM: MATRIX LiDAR BIO-FACE SCANNER", (25, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, theme["highlight"], 2, cv2.LINE_AA)

    with tracker.lock:
        port = tracker.port_name
        is_conn = tracker.connected
        dist = tracker.face_dist_cm
        yaw_deg = math.degrees(tracker.head_yaw)
        hz = tracker.scan_rate_hz
        sim = tracker.simulation_mode

    status_str = f"SENZOR: RPLIDAR C1 ({port})  |  BAUDRATE: {DEFAULT_BAUDRATE}  |  RATE: {hz:.1f} Hz"
    cv2.putText(canvas, status_str, (25, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, theme["hud"], 1)

    # Levi blok telemetrije
    y = 110
    telemetry = [
        ("UDALJENOST LICA:", f"{dist:.1f} cm"),
        ("ROTACIJA (YAW):", f"{yaw_deg:+.1f}°"),
        ("STATUS:", "TARGET ACQUIRED" if tracker.target_detected else "SEARCHING..."),
        ("TEMA:", THEMES[theme_idx]["name"][:16]),
        ("REZIM:", "SIMULACIJA (Demo)" if sim else "HARDVER (USB)")
    ]

    for lbl, val in telemetry:
        cv2.putText(canvas, lbl, (25, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, theme["secondary"], 1)
        val_col = theme["highlight"] if lbl.startswith("UDALJ") else theme["hud"]
        cv2.putText(canvas, val, (180, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, val_col, 1)
        y += 28

    # Donja traka sa komandama
    cmds = "Kontrole: [s] Simulacija ON/OFF  |  [c] Promeni Temu  |  [r] Reset Konekcije  |  [q] Izlaz"
    cv2.putText(canvas, cmds, (25, WIN_H - 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 200, 180), 1)


# ------------------------------------------------------------------------------
# GLAVNA PETLJA PROGRAMA
# ------------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("    RPLIDAR C1 — MATRIX FACE CONTOURS & LASER SCANNER (RPi 5)")
    print("=" * 70)
    print("Povezivanje na RPLIDAR C1 preko USB porta...")
    print("Kontrole: [s] Simulacija | [c] Tema | [q] Izlaz\n")

    tracker = LidarFaceTracker()

    # Pokreni prijem podataka
    worker = threading.Thread(target=tracker.worker_loop, daemon=True)
    worker.start()

    rain = MatrixRain(WIN_W, WIN_H, col_width=18)
    theme_idx = 0
    rain_enabled = True

    window_name = "Matrix Face - RPLIDAR C1 (Raspberry Pi 5)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, WIN_W, WIN_H)

    try:
        while tracker.running:
            theme = THEMES[theme_idx]

            # 1. Osnovno tamno platno
            canvas = np.full((WIN_H, WIN_W, 3), theme["bg"], dtype=np.uint8)

            # 2. Digitalna zelena kiša
            if rain_enabled:
                rain.update_and_draw(canvas, theme)

            # 3. Ako je aktivna simulacija, ažuriraj virtuelnu glavu
            if tracker.simulation_mode:
                tracker.update_simulation()

            # 4. Hologram lica i laserske konture
            nacrtaj_matrix_hologram(canvas, tracker, theme, rain_enabled)

            # 5. Matrix HUD i telemetrija
            renderuj_matrix_hud(canvas, tracker, theme, theme_idx)

            cv2.imshow(window_name, canvas)

            # Obrada tastera
            key = cv2.waitKey(20) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('s'):
                tracker.simulation_mode = not tracker.simulation_mode
                print(f"[MOD] Simulacija: {'UKLJUČENA' if tracker.simulation_mode else 'ISKLJUČENA'}")
            elif key == ord('c'):
                theme_idx = (theme_idx + 1) % len(THEMES)
                print(f"[TEMA] Promenjena tema: {THEMES[theme_idx]['name']}")
            elif key == ord('g'):
                rain_enabled = not rain_enabled
                print(f"[EFEKAT] Digitalna kisa: {'UKLJUCENA' if rain_enabled else 'ISKLJUCENA'}")
            elif key == ord('r'):
                print("[INFO] Resetovanje USB konekcije...")

    finally:
        tracker.running = False
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
