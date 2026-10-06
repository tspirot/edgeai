#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
     RPLIDAR C1 — SIGURNOSNA BARIJERA (1M) SA INICIJALNOM KALIBRACIJOM
               I PAMETNIM FILTERIMA ZA MALE OBJEKTE I POMERAJE
================================================================================
Aplikacija koja pretvara Slamtec RPLIDAR C1 u laserski sigurnosni perimetar:
- Prilikom starta vrši INICIJALNO SKENIRANJE (3.5 sekunde) i uči statički prostor
- Sve postojeće objekte (nameštaj, zidove, noge stola unutar 1m) automatski IGNORIŠE
- FILTER MALIH POMERAJA: Zahteva pomak od najmanje 20 cm od memorisane pozadine
  (ignoriše podrhtavanja, lepršanje zavesa, blaga pomeranja stolica ili šum)
- FILTER MALIH OBJEKATA: Klasterizuje tačke i zahteva fizičku širinu od bar 14 cm
  i bar 4 povezane tačke (ignoriše kablove, insekte, olovke i usamljeni šum)
- VREMENSKI DEBOUNCER: Zahteva potvrdu u 3 uzastopna ciklusa pre aktivacije alarma
- Taster [k] omogućava ponovnu kalibraciju (ponovno učenje prostora u bilo kom trenutku)
- 3 oblika barijere: 360° kružni perimetar, frontalni luk (120° zavesa), koridor
- Vizuelni (pulsirajuće crveno sa vektorom praćenja) i zvučni alarm (sirena)
"""

import os
import sys
import time
import math
import struct
import wave
import subprocess
import threading
from collections import deque
import numpy as np
import cv2

# Osiguravanje prikaza na lokalnom TV ekranu kada se pokreće preko SSH
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

# Serijska komunikacija i RPLiDAR
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    from rplidar import RPLidar
    LIDAR_LIB_AVAILABLE = True
except ImportError:
    LIDAR_LIB_AVAILABLE = False

# ------------------------------------------------------------------------------
# PODEŠAVANJA PRIKAZA I RADARA
# ------------------------------------------------------------------------------
WIN_W = 1040
WIN_H = 720

RADAR_CX = 370
RADAR_CY = 360
RADAR_RADIUS = 300
MAX_DISPLAY_DIST_M = 2.5       # Maksimalna prikazana razdaljina na radaru (2.5 metra)
SCALE_PX_PER_M = RADAR_RADIUS / MAX_DISPLAY_DIST_M

DEFAULT_BAUDRATE = 460800
FALLBACK_BAUDRATES = [460800, 256000, 115200]

# Audio alarm datoteka
BEEP_WAV_PATH = "/tmp/lidar_alarm_beep.wav" if os.name != "nt" else os.path.join(os.environ.get("TEMP", "C:\\Temp"), "lidar_alarm_beep.wav")


def generate_beep_wav(path=BEEP_WAV_PATH, duration=0.22, freq1=900, freq2=1400):
    """Kreira zvučni fajl upozoravajuće sirene (dva naizmenična tona)."""
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        with wave.open(path, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                t = i / float(sample_rate)
                f = freq1 if (int(t * 18) % 2 == 0) else freq2
                val = int(22000 * math.sin(2 * math.pi * f * t))
                frames.extend(struct.pack('<h', val))
            wf.writeframes(frames)
    except Exception:
        pass


generate_beep_wav()


# ------------------------------------------------------------------------------
# ZVUČNI ALARM KONTROLER (NE-BLOKIRAJUĆI)
# ------------------------------------------------------------------------------
class SoundAlarmController:
    def __init__(self):
        self.muted = False
        self.last_beep_time = 0

    def trigger(self):
        if self.muted:
            return
        now = time.time()
        if now - self.last_beep_time < 0.35:
            return
        self.last_beep_time = now

        def _play():
            try:
                if os.name != "nt":
                    subprocess.run(["aplay", "-q", BEEP_WAV_PATH],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=0.6)
                else:
                    import winsound
                    winsound.Beep(1200, 180)
            except Exception:
                pass

        threading.Thread(target=_play, daemon=True).start()


sound_controller = SoundAlarmController()


# ------------------------------------------------------------------------------
# STANJE SIGURNOSNOG SISTEMA
# ------------------------------------------------------------------------------
BARRIER_TYPES = ["360_KRUG", "FRONTALNI_LUK", "KORIDOR"]
BARRIER_NAMES = {
    "360_KRUG": "360° Kružni Perimetar",
    "FRONTALNI_LUK": "Frontalni Luk (120° Zavesa)",
    "KORIDOR": "Sigurnosni Koridor / Prolaz"
}


class SecuritySystemState:
    def __init__(self):
        self.lock = threading.Lock()
        self.running = True
        self.connected = False
        self.port_name = "Nije pronađen"
        self.baudrate = DEFAULT_BAUDRATE
        self.status_msg = "Tražim USB port za RPLIDAR C1..."
        self.last_data_time = 0.0
        self.points_per_sec = 0
        self.scan_rate_hz = 0.0
        self.reconnect_requested = False

        # Parametri barijere
        self.barrier_dist_m = 1.0       # Podrazumevano 1.0 m (100 cm)
        self.barrier_type_idx = 0       # 0: 360°, 1: Frontalno, 2: Koridor

        # Inicijalna kalibracija statičkih prepreka
        self.calibrating = True
        self.calibrated = False
        self.calib_start_time = None
        self.calib_duration = 3.5       # Trajanje inicijalnog skeniranja u sekundama
        self.calib_samples = {ang: [] for ang in range(360)}
        self.baseline_map = {}          # ang -> dist_m statičkog objekta
        self.ignored_static_count = 0

        # Pametni filteri za eliminaciju lažnih alarma
        self.min_displacement_m = 0.20        # Minimalan pomak ka senzoru u odnosu na memorisanu pozadinu (20 cm)
        self.min_cluster_width_m = 0.14       # Minimalna širina objekta u prostoru (14 cm)
        self.min_cluster_points = 4           # Minimalan broj povezanih tačaka u klasteru
        self.consecutive_breach_frames = 0    # Brojač uzastopnih frejmova detekcije (debounce)
        self.required_confirm_frames = 3      # Potrebno 3 uzastopna ciklusa za potvrdu uljeza (~250-300ms)

        # Očitane tačke: ugao (stepeni) -> (dist_m, timestamp)
        self.points = {}
        self.current_sweep_angle = 0.0

        # Stanje alarma
        self.alarm_active = False
        self.alarm_hold_until = 0.0
        self.breach_points = []               # Tačke potvrđenog pravog uljeza
        self.ignored_points = []              # Tačke statičkih objekata iz pozadine
        self.filtered_small_points = []       # Tačke filtriranih malih objekata (<14cm / <4 tačke)
        self.closest_breach_dist_m = 99.0
        self.closest_breach_angle = 0.0
        self.closest_breach_sector = ""
        self.closest_breach_width_cm = 0.0
        self.total_incidents = 0
        self.security_log = deque(maxlen=8)

    def start_calibration(self):
        """Ponovo pokreće kalibraciju i učenje statičkog okruženja."""
        self.calibrating = True
        self.calibrated = False
        self.calib_start_time = None
        self.calib_samples = {ang: [] for ang in range(360)}
        self.baseline_map = {}
        self.ignored_static_count = 0
        self.alarm_active = False
        self.breach_points = []
        self.ignored_points = []
        self.filtered_small_points = []
        self.consecutive_breach_frames = 0
        print("[BARIJERA] Pokrenuta ponovna kalibracija prostora...")

    def is_point_in_barrier(self, dist_m, angle_deg):
        """Proverava da li je tačka unutar definisane sigurnosne zone."""
        if dist_m <= 0.08 or dist_m > self.barrier_dist_m:
            return False

        b_type = BARRIER_TYPES[self.barrier_type_idx]

        if b_type == "360_KRUG":
            return True

        norm_angle = (angle_deg + 360) % 360
        rel_angle = norm_angle if norm_angle <= 180 else norm_angle - 360

        if b_type == "FRONTALNI_LUK":
            # Sektor od -60° do +60° (ukupno 120° ispred senzora)
            return abs(rel_angle) <= 60.0

        elif b_type == "KORIDOR":
            # Koridor: napred do barrier_dist_m, širina +/- 0.55m
            rad = math.radians(rel_angle)
            x_m = dist_m * math.sin(rad)
            y_m = dist_m * math.cos(rad)
            return (y_m > 0) and (y_m <= self.barrier_dist_m) and (abs(x_m) <= 0.55)

        return False

    def get_sector_name(self, angle_deg):
        angle = (angle_deg + 360) % 360
        if 337.5 <= angle or angle < 22.5:
            return "NAPRED (0°)"
        elif 22.5 <= angle < 67.5:
            return "NAPRED-DESNO (45°)"
        elif 67.5 <= angle < 112.5:
            return "DESNO (90°)"
        elif 112.5 <= angle < 157.5:
            return "NAZAD-DESNO (135°)"
        elif 157.5 <= angle < 202.5:
            return "NAZAD (180°)"
        elif 202.5 <= angle < 247.5:
            return "NAZAD-LEVO (225°)"
        elif 247.5 <= angle < 292.5:
            return "LEVO (270°)"
        else:
            return "NAPRED-LEVO (315°)"


sec_state = SecuritySystemState()


# ------------------------------------------------------------------------------
# AUTOMATSKA PRETRAGA USB PORTA
# ------------------------------------------------------------------------------
def pronadji_usb_port():
    preferred = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyACM0", "/dev/ttyACM1"]
    for p in preferred:
        if os.path.exists(p):
            return p
    if SERIAL_AVAILABLE:
        try:
            for p in serial.tools.list_ports.comports():
                desc = p.description.lower()
                name = p.device
                if any(k in desc for k in ["cp210", "ch340", "ftdi", "silicon", "rplidar", "usb serial"]):
                    return name
                if "ttyusb" in name.lower() or "ttyacm" in name.lower():
                    return name
        except Exception:
            pass
    return None


# ------------------------------------------------------------------------------
# RADNA NIT ZA ŽIVI RPLIDAR C1 (BEZ SIMULACIJE)
# ------------------------------------------------------------------------------
def lidar_thread_loop():
    """Pozadinska nit isključivo za pravi RPLIDAR C1 senzor."""
    while sec_state.running:
        port = pronadji_usb_port()

        if not port:
            with sec_state.lock:
                sec_state.connected = False
                sec_state.port_name = "Nije pronađen"
                sec_state.status_msg = "USB port nije pronađen (/dev/ttyUSB*). Povežite RPLIDAR C1 u USB port."
            time.sleep(1.0)
            continue

        if not LIDAR_LIB_AVAILABLE:
            with sec_state.lock:
                sec_state.connected = False
                sec_state.status_msg = "Greška: Biblioteka 'rplidar' nije instalirana u okruženju."
            time.sleep(2.0)
            continue

        with sec_state.lock:
            sec_state.port_name = port
            sec_state.status_msg = f"Pronađen port {port}. Povezujem se..."

        lidar = None
        for baud in [sec_state.baudrate] + [b for b in FALLBACK_BAUDRATES if b != sec_state.baudrate]:
            if not sec_state.running:
                break
            try:
                print(f"[BARIJERA] Otvaram {port} na {baud} baud...")
                lidar = RPLidar(port, baudrate=baud, timeout=3)
                lidar.clean_input()
                info = lidar.get_info()
                health = lidar.get_health()

                with sec_state.lock:
                    sec_state.connected = True
                    sec_state.baudrate = baud
                    sec_state.status_msg = f"LiDAR povezan ({info.get('model', 'C1')}). Pokrećem motor skenera..."
                print(f"[BARIJERA] Povezan na {port} ({baud})! Model: {info.get('model', 'C1')}")
                break
            except Exception as e:
                print(f"[BARIJERA] Neuspešno na {baud} baud: {e}")
                if lidar:
                    try:
                        lidar.disconnect()
                    except Exception:
                        pass
                lidar = None
                time.sleep(0.4)

        if not lidar:
            with sec_state.lock:
                sec_state.connected = False
                sec_state.status_msg = f"Greška pri otvaranju {port}. Proverite USB kabl/dozvole."
            time.sleep(1.5)
            continue

        try:
            lidar.start_motor()
            time.sleep(0.5)

            scans_count = 0
            points_count = 0
            stat_time = time.time()

            with sec_state.lock:
                sec_state.status_msg = "Skener aktivan — prijem merenja sa senzora..."

            for scan in lidar.iter_scans(max_buf_meas=1000):
                if not sec_state.running or sec_state.reconnect_requested:
                    with sec_state.lock:
                        sec_state.reconnect_requested = False
                    break

                now = time.time()
                scans_count += 1
                points_count += len(scan)

                if now - stat_time >= 1.0:
                    with sec_state.lock:
                        sec_state.scan_rate_hz = scans_count / (now - stat_time)
                        sec_state.points_per_sec = int(points_count / (now - stat_time))
                    scans_count = 0
                    points_count = 0
                    stat_time = now

                with sec_state.lock:
                    sec_state.last_data_time = now
                    for item in scan:
                        if len(item) == 3:
                            qual, angle, dist_mm = item
                        else:
                            angle, dist_mm = item[1], item[2]

                        if dist_mm > 0:
                            dist_m = dist_mm / 1000.0
                            int_angle = int(round(angle)) % 360
                            sec_state.points[int_angle] = (dist_m, now)
                            sec_state.current_sweep_angle = angle

        except Exception as e:
            print(f"[BARIJERA] Prekid toka merenja: {e}")
            with sec_state.lock:
                sec_state.connected = False
                sec_state.status_msg = f"Prekid merenja ({e}). Pokušavam ponovno povezivanje..."
        finally:
            if lidar:
                try:
                    lidar.stop()
                    lidar.stop_motor()
                    lidar.disconnect()
                except Exception:
                    pass
            with sec_state.lock:
                sec_state.connected = False
            time.sleep(1.0)


# ------------------------------------------------------------------------------
# ISCRTAVANJE RADARA I KONTROLNOG PANELA
# ------------------------------------------------------------------------------
def draw_radar_and_dashboard(canvas):
    now = time.time()

    with sec_state.lock:
        b_dist_m = sec_state.barrier_dist_m
        b_type = BARRIER_TYPES[sec_state.barrier_type_idx]
        is_connected = sec_state.connected
        last_t = sec_state.last_data_time
        status_txt = sec_state.status_msg
        port_txt = sec_state.port_name
        baud_val = sec_state.baudrate
        pps_val = sec_state.points_per_sec
        current_pts = dict(sec_state.points)
        sweep_ang = sec_state.current_sweep_angle
        is_calibrating = sec_state.calibrating
        calib_start = sec_state.calib_start_time
        calib_dur = sec_state.calib_duration
        calibrated = sec_state.calibrated
        baseline = dict(sec_state.baseline_map)
        ignored_count = sec_state.ignored_static_count
        min_disp = sec_state.min_displacement_m
        min_w = sec_state.min_cluster_width_m
        min_pts = sec_state.min_cluster_points

    # Provera da li imamo sveže žive podatke sa LiDAR-a (unutar poslednje 2 sekunde)
    has_live_data = is_connected and (now - last_t < 2.0) and (len(current_pts) > 0)

    # 1. OBRADA KALIBRACIJE (INICIJALNO SKENIRANJE STATIČKIH OBJEKATA)
    calib_progress = 0.0
    elapsed_calib = 0.0
    if has_live_data and is_calibrating:
        if calib_start is None:
            with sec_state.lock:
                sec_state.calib_start_time = now
                calib_start = now

        elapsed_calib = now - calib_start
        calib_progress = min(1.0, elapsed_calib / calib_dur)

        # Sakupljanje uzoraka za svaki ugao
        with sec_state.lock:
            for ang, (d_m, t_stamp) in current_pts.items():
                if now - t_stamp < 0.3:
                    sec_state.calib_samples[ang].append(d_m)

        # Da li je kalibracija završena?
        if elapsed_calib >= calib_dur:
            num_static = 0
            with sec_state.lock:
                for a in range(360):
                    samps = sec_state.calib_samples[a]
                    if len(samps) >= 2:
                        med_d = float(np.median(samps))
                        sec_state.baseline_map[a] = med_d
                        if med_d <= sec_state.barrier_dist_m:
                            num_static += 1
                    else:
                        sec_state.baseline_map[a] = 99.0

                sec_state.calibrating = False
                sec_state.calibrated = True
                sec_state.ignored_static_count = num_static
                print(f"[BARIJERA] Inicijalno skeniranje završeno! Memorisano {len(sec_state.baseline_map)} uglova, ignorisano {num_static} statičkih prepreka unutar {sec_state.barrier_dist_m}m.")

    # 2. ANALIZA TAČAKA: STATIČKI FILTER, KLASTERIZACIJA I FILTERI ZA MALE OBJEKTE I POMERAJE
    raw_breach_points = []
    ignored_list = []

    if has_live_data and calibrated and not is_calibrating:
        cutoff_time = now - 0.7
        for ang, (d_m, t_stamp) in current_pts.items():
            if now - t_stamp < 0.7:
                if sec_state.is_point_in_barrier(d_m, ang):
                    base_d = baseline.get(ang, 99.0)

                    # A. FILTER MALIH POMERAJA:
                    # Ako je objekat već bio tu na distanci base_d, ignorišemo sve tačke
                    # koje se nisu približile bar za min_disp (20 cm) bliže senzoru!
                    # Ovo eliminiše podrhtavanja, šum, blaga pomeranja stolice ili zavese.
                    if base_d <= sec_state.barrier_dist_m and (d_m >= base_d - min_disp):
                        ignored_list.append((ang, d_m))
                    else:
                        # Kandidat za novog uljeza
                        raw_breach_points.append((ang, d_m))

    # B. KLASTERIZACIJA I FILTER MALIH OBJEKATA (OBJEKAT MORA IMATI ŠIRINU BAR 14 CM):
    pts_xy = []
    for ang, d_m in raw_breach_points:
        rad = math.radians(ang)
        x = d_m * math.sin(rad)
        y = -d_m * math.cos(rad)
        pts_xy.append((x, y, ang, d_m))

    # Povezivanje tačaka u prostorne klastere (tačke na rastojanju do 18 cm)
    clusters = []
    visited = set()
    for i in range(len(pts_xy)):
        if i in visited:
            continue
        cluster = [pts_xy[i]]
        visited.add(i)
        queue = [pts_xy[i]]

        while queue:
            curr = queue.pop(0)
            cx, cy = curr[0], curr[1]
            for j in range(len(pts_xy)):
                if j not in visited:
                    jx, jy = pts_xy[j][0], pts_xy[j][1]
                    if math.hypot(cx - jx, cy - jy) <= 0.18:
                        visited.add(j)
                        cluster.append(pts_xy[j])
                        queue.append(pts_xy[j])
        clusters.append(cluster)

    # Razvrstavanje klastera na validne uljeze i filtrirane male objekte
    valid_breach_list = []
    small_objects_list = []
    closest_cluster_dist = 99.0
    closest_cluster_ang = 0.0
    closest_cluster_w_cm = 0.0

    for cl in clusters:
        # Fizička širina klastera
        c_max_d = 0.0
        for p1 in cl:
            for p2 in cl:
                dist_p = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                if dist_p > c_max_d:
                    c_max_d = dist_p

        # Kriterijum: Bar min_pts (4) tačaka i širina bar min_w (14 cm)
        if len(cl) >= min_pts and c_max_d >= min_w:
            # VALIDAN ULJEZ (osoba, telo, noga, veći objekat)
            for _, _, a, d in cl:
                valid_breach_list.append((a, d))
                if d < closest_cluster_dist:
                    closest_cluster_dist = d
                    closest_cluster_ang = a
                    closest_cluster_w_cm = c_max_d * 100.0
        else:
            # MALI OBJEKAT (kabl, insekt, olovka, izolovani šum) -> IGNORIŠI OD ALARMA!
            for _, _, a, d in cl:
                small_objects_list.append((a, d))

    # C. VREMENSKI FILTER (DEBOUNCE):
    # Zahteva potvrdu u bar 3 uzastopna ciklusa (~250ms)
    if len(valid_breach_list) > 0:
        sec_state.consecutive_breach_frames += 1
    else:
        sec_state.consecutive_breach_frames = max(0, sec_state.consecutive_breach_frames - 1)

    confirmed_intrusion = sec_state.consecutive_breach_frames >= sec_state.required_confirm_frames

    with sec_state.lock:
        sec_state.ignored_points = ignored_list
        sec_state.filtered_small_points = small_objects_list
        sec_state.breach_points = valid_breach_list

        if has_live_data and calibrated and not is_calibrating and confirmed_intrusion:
            sec_state.alarm_active = True
            sec_state.alarm_hold_until = now + 2.0
            sec_state.closest_breach_dist_m = closest_cluster_dist
            sec_state.closest_breach_angle = closest_cluster_ang
            sec_state.closest_breach_width_cm = closest_cluster_w_cm
            sec_state.closest_breach_sector = sec_state.get_sector_name(closest_cluster_ang)

            # Evidentiraj u bezbednosni log
            if len(sec_state.security_log) == 0 or (now - sec_state.security_log[-1]["time_raw"] > 2.5):
                sec_state.total_incidents += 1
                vreme_str = time.strftime("%H:%M:%S")
                sec_state.security_log.append({
                    "time_raw": now,
                    "time_str": vreme_str,
                    "dist_cm": int(closest_cluster_dist * 100),
                    "angle": int(closest_cluster_ang),
                    "width_cm": int(closest_cluster_w_cm),
                    "sector": sec_state.closest_breach_sector
                })
        else:
            if (not has_live_data) or is_calibrating or (now > sec_state.alarm_hold_until):
                sec_state.alarm_active = False

        alarm_on = sec_state.alarm_active

    # Aktiviraj zvučnu sirenu ako je upad u toku
    if alarm_on:
        sound_controller.trigger()

    # 3. Pozadina i atmosfera
    pulse = (math.sin(now * 12.0) + 1.0) / 2.0
    if alarm_on:
        bg_col = (int(16 + pulse * 14), int(14 * (1.0 - pulse)), int(14 * (1.0 - pulse)))
    else:
        bg_col = (14, 18, 24)

    canvas[:] = bg_col

    # 4. Radarski krug i mreža
    cv2.circle(canvas, (RADAR_CX, RADAR_CY), RADAR_RADIUS, (30, 42, 56), -1)

    range_steps = [0.5, 1.0, 1.5, 2.0, 2.5]
    for r_m in range_steps:
        r_px = int(r_m * SCALE_PX_PER_M)
        if r_px <= RADAR_RADIUS:
            is_b_ring = abs(r_m - b_dist_m) < 0.04
            ring_col = (45, 65, 85) if not is_b_ring else (60, 80, 100)
            cv2.circle(canvas, (RADAR_CX, RADAR_CY), r_px, ring_col, 1)

            cv2.putText(canvas, f"{r_m:.1f}m", (RADAR_CX + 6, RADAR_CY - r_px + 14),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (120, 150, 180), 1, cv2.LINE_AA)

    # Glavni krst
    cv2.line(canvas, (RADAR_CX - RADAR_RADIUS, RADAR_CY), (RADAR_CX + RADAR_RADIUS, RADAR_CY), (40, 58, 78), 1)
    cv2.line(canvas, (RADAR_CX, RADAR_CY - RADAR_RADIUS), (RADAR_CX, RADAR_CY + RADAR_RADIUS), (40, 58, 78), 1)

    # Dijagonale
    d_off = int(RADAR_RADIUS * 0.7071)
    cv2.line(canvas, (RADAR_CX - d_off, RADAR_CY - d_off), (RADAR_CX + d_off, RADAR_CY + d_off), (28, 42, 58), 1)
    cv2.line(canvas, (RADAR_CX - d_off, RADAR_CY + d_off), (RADAR_CX + d_off, RADAR_CY - d_off), (28, 42, 58), 1)

    # 5. ISCRTAVANJE SIGURNOSNE BARIJERE (1M ILI PODEŠENA DISTANCA)
    b_px = int(b_dist_m * SCALE_PX_PER_M)

    if alarm_on:
        barrier_col = (0, 0, int(200 + pulse * 55))
        barrier_glow = (20, 30, int(160 + pulse * 70))
        barrier_thickness = 3
    elif is_calibrating:
        barrier_col = (0, 220, 255)
        barrier_glow = (0, 140, 180)
        barrier_thickness = 2
    else:
        barrier_col = (255, 230, 0)
        barrier_glow = (180, 140, 0)
        barrier_thickness = 2

    if b_type == "360_KRUG":
        cv2.circle(canvas, (RADAR_CX, RADAR_CY), b_px, barrier_glow, barrier_thickness + 2)
        cv2.circle(canvas, (RADAR_CX, RADAR_CY), b_px, barrier_col, barrier_thickness)

        if alarm_on:
            overlay_zone = canvas.copy()
            cv2.circle(overlay_zone, (RADAR_CX, RADAR_CY), b_px, (0, 0, 70), -1)
            cv2.addWeighted(overlay_zone, 0.35, canvas, 0.65, 0, canvas)

    elif b_type == "FRONTALNI_LUK":
        start_cv_angle = 270 - 60
        end_cv_angle = 270 + 60
        cv2.ellipse(canvas, (RADAR_CX, RADAR_CY), (b_px, b_px), 0, start_cv_angle, end_cv_angle, barrier_glow, barrier_thickness + 2)
        cv2.ellipse(canvas, (RADAR_CX, RADAR_CY), (b_px, b_px), 0, start_cv_angle, end_cv_angle, barrier_col, barrier_thickness)

        r1 = math.radians(-60)
        r2 = math.radians(60)
        p1 = (RADAR_CX + int(b_px * math.sin(r1)), RADAR_CY - int(b_px * math.cos(r1)))
        p2 = (RADAR_CX + int(b_px * math.sin(r2)), RADAR_CY - int(b_px * math.cos(r2)))
        cv2.line(canvas, (RADAR_CX, RADAR_CY), p1, barrier_col, 1, cv2.LINE_AA)
        cv2.line(canvas, (RADAR_CX, RADAR_CY), p2, barrier_col, 1, cv2.LINE_AA)

    elif b_type == "KORIDOR":
        w_half_px = int(0.55 * SCALE_PX_PER_M)
        pt_tl = (RADAR_CX - w_half_px, RADAR_CY - b_px)
        pt_br = (RADAR_CX + w_half_px, RADAR_CY)
        cv2.rectangle(canvas, pt_tl, pt_br, barrier_glow, barrier_thickness + 2)
        cv2.rectangle(canvas, pt_tl, pt_br, barrier_col, barrier_thickness)

    # Oznaka barijere
    b_label = f"BARIJERA: {b_dist_m:.1f}m"
    cv2.putText(canvas, b_label, (RADAR_CX - 60, RADAR_CY - b_px - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, barrier_col, 1, cv2.LINE_AA)

    # 6. Rotirajući radarski snop
    display_sweep_ang = sweep_ang if has_live_data else (now * 120) % 360
    sw_rad = math.radians(display_sweep_ang)
    sw_x = RADAR_CX + int(RADAR_RADIUS * math.sin(sw_rad))
    sw_y = RADAR_CY - int(RADAR_RADIUS * math.cos(sw_rad))
    sweep_col = (0, 160, 255) if not alarm_on else (50, 80, 255)
    cv2.line(canvas, (RADAR_CX, RADAR_CY), (sw_x, sw_y), sweep_col, 1, cv2.LINE_AA)

    # 7. ISCRTAVANJE TAČAKA NA RADARU
    if has_live_data:
        for ang, (d_m, t_stamp) in current_pts.items():
            if now - t_stamp > 0.8:
                continue
            rad = math.radians(ang)
            px_dist = d_m * SCALE_PX_PER_M
            if px_dist > RADAR_RADIUS:
                continue

            pt_x = RADAR_CX + int(px_dist * math.sin(rad))
            pt_y = RADAR_CY - int(px_dist * math.cos(rad))

            # Klasifikacija tačke
            is_valid_breach = any(b_ang == ang for b_ang, _ in valid_breach_list)
            is_small = any(s_ang == ang for s_ang, _ in small_objects_list)
            is_ignored_static = any(i_ang == ang for i_ang, _ in ignored_list)

            if is_valid_breach:
                # POTVRĐEN ULJEZ: Jarka crvena sa belim centrom
                cv2.circle(canvas, (pt_x, pt_y), 5, (0, 0, 255), -1)
                cv2.circle(canvas, (pt_x, pt_y), 7, (200, 200, 255), 1)
            elif is_small:
                # MALI OBJEKAT (<14cm / <4 tačke): Narandžasti romb/kružić (filtriran)
                cv2.circle(canvas, (pt_x, pt_y), 3, (0, 165, 255), -1)
            elif is_ignored_static:
                # STATIČKI OBJEKAT (pozadina): Prigušena žućkasto-siva (kružić)
                cv2.circle(canvas, (pt_x, pt_y), 3, (160, 140, 80), -1)
                cv2.circle(canvas, (pt_x, pt_y), 5, (220, 180, 100), 1)
            else:
                # Normalna tačka van zone: Neon zelena
                cv2.circle(canvas, (pt_x, pt_y), 2, (0, 220, 120), -1)

        # Označavanje najkritičnije tačke upada (vektor praćenja)
        if alarm_on and len(valid_breach_list) > 0:
            c_dist = sec_state.closest_breach_dist_m
            c_ang = sec_state.closest_breach_angle
            c_w = sec_state.closest_breach_width_cm
            c_rad = math.radians(c_ang)
            c_px_dist = c_dist * SCALE_PX_PER_M
            c_x = RADAR_CX + int(c_px_dist * math.sin(c_rad))
            c_y = RADAR_CY - int(c_px_dist * math.cos(c_rad))

            cv2.line(canvas, (RADAR_CX, RADAR_CY), (c_x, c_y), (0, 0, 255), 2, cv2.LINE_AA)

            target_r = int(12 + pulse * 8)
            cv2.circle(canvas, (c_x, c_y), target_r, (0, 0, 255), 2)
            cv2.circle(canvas, (c_x, c_y), target_r + 5, (0, 160, 255), 1)

            tag_text = f"ULJEZ: {int(c_dist * 100)}cm (sirina {int(c_w)}cm) @ {int(c_ang)}deg"
            cv2.putText(canvas, tag_text, (c_x + 14, c_y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(canvas, tag_text, (c_x + 14, c_y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (255, 255, 255), 1, cv2.LINE_AA)

    # 8. GRAFIČKI EKRAN ZA INICIJALNO SKENIRANJE I KALIBRACIJU
    if has_live_data and is_calibrating:
        msg_w, msg_h = 560, 175
        x1 = RADAR_CX - msg_w // 2
        y1 = RADAR_CY - msg_h // 2
        x2 = x1 + msg_w
        y2 = y1 + msg_h

        overlay = canvas.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (16, 26, 38), -1)
        cv2.addWeighted(overlay, 0.90, canvas, 0.10, 0, canvas)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (255, 200, 0), 2)

        cv2.putText(canvas, "[ ! ] INICIJALNO SKENIRANJE PROSTORA", (x1 + 35, y1 + 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 220, 0), 2, cv2.LINE_AA)
        cv2.putText(canvas, "Snimam staticke objekte (zidove, namestaj unutar 1m)...", (x1 + 25, y1 + 68),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (220, 240, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "Molimo da niko ne prelazi barijeru dok traje ucenje!", (x1 + 25, y1 + 94),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 210, 240), 1, cv2.LINE_AA)

        # Progress bar
        bar_w = 510
        bar_h = 16
        bx1 = x1 + 25
        by1 = y1 + 112
        cv2.rectangle(canvas, (bx1, by1), (bx1 + bar_w, by1 + bar_h), (35, 45, 60), -1)
        filled_w = int(bar_w * calib_progress)
        cv2.rectangle(canvas, (bx1, by1), (bx1 + filled_w, by1 + bar_h), (0, 220, 120), -1)
        cv2.rectangle(canvas, (bx1, by1), (bx1 + bar_w, by1 + bar_h), (120, 160, 200), 1)

        pct_txt = f"{int(calib_progress * 100)}% ({elapsed_calib:.1f}s / {calib_dur:.1f}s)"
        cv2.putText(canvas, pct_txt, (bx1 + bar_w // 2 - 50, by1 + 13),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.putText(canvas, "Nakon ovoga, sistem ignorise sve memorisane objekte.", (x1 + 25, y1 + 152),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (140, 255, 180), 1, cv2.LINE_AA)

    # 9. PORUKA UPOZORENJA KADA NEMA PODATAKA SA LIDARA
    elif not has_live_data:
        msg_w, msg_h = 560, 175
        x1 = RADAR_CX - msg_w // 2
        y1 = RADAR_CY - msg_h // 2
        x2 = x1 + msg_w
        y2 = y1 + msg_h

        overlay = canvas.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (12, 16, 26), -1)
        cv2.addWeighted(overlay, 0.90, canvas, 0.10, 0, canvas)
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 180, 255), 2)

        warn_pulse = (math.sin(now * 6.0) + 1.0) / 2.0
        title_col = (0, int(180 + warn_pulse * 75), 255)
        cv2.putText(canvas, "[ ! ] CEKAM PODATKE SA LIDAR SENZORA", (x1 + 35, y1 + 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.62, title_col, 2, cv2.LINE_AA)

        cv2.putText(canvas, f"Status: {status_txt}", (x1 + 25, y1 + 72),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (230, 240, 255), 1, cv2.LINE_AA)
        cv2.putText(canvas, "1. Proverite da li je RPLIDAR C1 USB adapter ukljucen u RPi 5.", (x1 + 25, y1 + 102),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 205, 230), 1, cv2.LINE_AA)
        cv2.putText(canvas, "2. Aplikacija se automatski aktivira cim prepozna senzor!", (x1 + 25, y1 + 128),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (120, 255, 160), 1, cv2.LINE_AA)
        cv2.putText(canvas, "Pritisnite [r] za ponovnu pretragu portova  |  [q] Izlaz", (x1 + 25, y1 + 154),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (140, 160, 190), 1, cv2.LINE_AA)

    # Ikonica senzora u centru radara
    sensor_col = (0, 255, 100) if has_live_data else (0, 165, 255)
    cv2.circle(canvas, (RADAR_CX, RADAR_CY), 7, sensor_col, -1)
    cv2.circle(canvas, (RADAR_CX, RADAR_CY), 9, (255, 255, 255), 1)

    # Oznake strana sveta na radaru
    cv2.putText(canvas, "NAPRED (0 deg)", (RADAR_CX - 42, RADAR_CY - RADAR_RADIUS - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 190, 220), 1, cv2.LINE_AA)
    cv2.putText(canvas, "DESNO (90 deg)", (RADAR_CX + RADAR_RADIUS + 8, RADAR_CY + 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 190, 220), 1, cv2.LINE_AA)
    cv2.putText(canvas, "NAZAD (180 deg)", (RADAR_CX - 45, RADAR_CY + RADAR_RADIUS + 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 190, 220), 1, cv2.LINE_AA)
    cv2.putText(canvas, "LEVO (270 deg)", (RADAR_CX - RADAR_RADIUS - 95, RADAR_CY + 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (160, 190, 220), 1, cv2.LINE_AA)

    # --------------------------------------------------------------------------
    # DESNI KOMANDNI PANEL (TELEMETRIJA, STATUS I LOG)
    # --------------------------------------------------------------------------
    panel_x = 730
    panel_w = WIN_W - panel_x - 15

    cv2.rectangle(canvas, (panel_x, 15), (panel_x + panel_w, WIN_H - 15), (20, 26, 36), -1)
    cv2.rectangle(canvas, (panel_x, 15), (panel_x + panel_w, WIN_H - 15), (45, 60, 80), 1)

    # 1. Glavni naslov
    cv2.putText(canvas, "RPLIDAR C1 PERIMETAR", (panel_x + 15, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(canvas, "SIGURNOSNA BARIJERA & ALARM", (panel_x + 15, 68),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 220, 255), 1, cv2.LINE_AA)
    cv2.line(canvas, (panel_x + 15, 80), (panel_x + panel_w - 15, 80), (50, 70, 95), 1)

    # 2. STATUS BADGE
    badge_y = 95
    badge_h = 55
    if not has_live_data:
        badge_bg = (18, 55, 95)
        badge_border = (0, 180, 255)
        badge_txt1 = "[ CEKAM SENZOR ]"
        badge_txt2 = "Nema podataka sa LiDAR-a"
        text_col = (200, 240, 255)
    elif is_calibrating:
        badge_bg = (20, 50, 80)
        badge_border = (255, 200, 0)
        badge_txt1 = "[ KALIBRACIJA PROSTORA ]"
        badge_txt2 = f"Ucenje okruzenja... {int(calib_progress * 100)}%"
        text_col = (255, 230, 100)
    elif alarm_on:
        badge_bg = (0, 0, int(180 + pulse * 75))
        badge_border = (255, 255, 255)
        badge_txt1 = "!! ALARM !! UPAD DETEKTOVAN"
        badge_txt2 = f"ULJEZ ({int(sec_state.closest_breach_width_cm)}cm) NA {int(sec_state.closest_breach_dist_m * 100)} cm!"
        text_col = (255, 255, 255)
    else:
        badge_bg = (24, 70, 35)
        badge_border = (50, 160, 80)
        badge_txt1 = "[ OK ] PERIMETAR AKTIVAN"
        badge_txt2 = f"Filteri aktivni: Mali objekti eliminisani"
        text_col = (180, 255, 200)

    cv2.rectangle(canvas, (panel_x + 15, badge_y), (panel_x + panel_w - 15, badge_y + badge_h), badge_bg, -1)
    cv2.rectangle(canvas, (panel_x + 15, badge_y), (panel_x + panel_w - 15, badge_y + badge_h), badge_border, 2)
    cv2.putText(canvas, badge_txt1, (panel_x + 25, badge_y + 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.50, text_col, 2, cv2.LINE_AA)
    cv2.putText(canvas, badge_txt2, (panel_x + 25, badge_y + 44),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, text_col, 1, cv2.LINE_AA)

    # 3. Parametri barijere
    py = 175
    cv2.putText(canvas, "PODEŠAVANJA BARIJERE:", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 200, 255), 1, cv2.LINE_AA)
    py += 22
    cv2.putText(canvas, f"Domet barijere:    {b_dist_m:.1f} m ({int(b_dist_m * 100)} cm)  [+/-]", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (230, 230, 230), 1, cv2.LINE_AA)
    py += 20
    cv2.putText(canvas, f"Oblik zone:        {BARRIER_NAMES[b_type]}  [b]", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (230, 230, 230), 1, cv2.LINE_AA)
    py += 20
    sound_status = "ISKLJUČEN (MUTED)" if sound_controller.muted else "UKLJUČEN (SIRENA)"
    cv2.putText(canvas, f"Zvučni alarm:      {sound_status}  [m]", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 180, 255) if not sound_controller.muted else (120, 120, 140), 1, cv2.LINE_AA)

    cv2.line(canvas, (panel_x + 15, py + 12), (panel_x + panel_w - 15, py + 12), (40, 55, 75), 1)

    # 4. Pametni filteri (Eliminacija malih objekata i pomaka)
    py += 30
    cv2.putText(canvas, "PAMETNI FILTERI LAŽNIH ALARMA:", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 200, 255), 1, cv2.LINE_AA)
    py += 20
    cv2.putText(canvas, f"Filter veličine:   > {int(min_w * 100)} cm (klaster >= {min_pts} tačke)", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)
    py += 18
    cv2.putText(canvas, f"Filter pomaka:     > {int(min_disp * 100)} cm od pozadine", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)
    py += 18
    cv2.putText(canvas, "Debouncer:         3 ciklusa (~250ms potvrda)", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 220, 220), 1, cv2.LINE_AA)

    cv2.line(canvas, (panel_x + 15, py + 10), (panel_x + panel_w - 15, py + 10), (40, 55, 75), 1)

    # 5. Telemetrija detekcije u realnom vremenu
    py += 28
    cv2.putText(canvas, "TELEMETRIJA DETEKCIJE:", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 200, 255), 1, cv2.LINE_AA)
    py += 20
    if is_calibrating:
        cv2.putText(canvas, f"Kalibracija:       SNIMANJE ({int(calib_progress * 100)}%)", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 220, 255), 1, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, "Statički objekti:  Obrada u toku...", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, "Uljez:             Čekam kalibraciju", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 180, 180), 1, cv2.LINE_AA)
    elif not has_live_data:
        cv2.putText(canvas, "Status veze:       ČEKAM PODATKE...", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 180, 255), 1, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, "Uljez:             --", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 160, 180), 1, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, "Sektor ulaska:     Nema signala", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (140, 160, 180), 1, cv2.LINE_AA)
    elif alarm_on:
        cv2.putText(canvas, f"POTVRĐEN ULJEZ:    {int(sec_state.closest_breach_dist_m * 100)} cm @ {int(sec_state.closest_breach_angle)}deg", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (0, 100, 255), 2, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, f"Širina tela:       {int(sec_state.closest_breach_width_cm)} cm (Validan objekat)", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (240, 240, 240), 1, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, f"Sektor ulaska:     {sec_state.closest_breach_sector}", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 220, 255), 1, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, f"Ignorisano:        {len(sec_state.ignored_points)} pozadina | {len(sec_state.filtered_small_points)} malih", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 200, 120), 1, cv2.LINE_AA)
    else:
        cv2.putText(canvas, "Uljez:             NEMA (ZONA ČISTA)", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, (140, 220, 140), 1, cv2.LINE_AA)
        py += 18
        cv2.putText(canvas, f"Statički objekti:  {ignored_count} memorisano (ignorisano)", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (220, 200, 120), 1, cv2.LINE_AA)
        py += 18
        small_cnt = len(sec_state.filtered_small_points)
        small_col = (0, 180, 255) if small_cnt > 0 else (160, 180, 200)
        cv2.putText(canvas, f"Mali objekti (<14cm): {small_cnt} filtrirano (nema alarma)", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, small_col, 1, cv2.LINE_AA)

    cv2.line(canvas, (panel_x + 15, py + 10), (panel_x + panel_w - 15, py + 10), (40, 55, 75), 1)

    # 6. Dnevnik incidenata (Security Event Log)
    py += 26
    cv2.putText(canvas, f"DNEVNIK UPADA (Ukupno: {sec_state.total_incidents}):", (panel_x + 15, py),
                cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 200, 255), 1, cv2.LINE_AA)
    py += 18

    if len(sec_state.security_log) == 0:
        cv2.putText(canvas, "Nema zabeleženih incidenata.", (panel_x + 15, py),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (120, 140, 160), 1, cv2.LINE_AA)
        py += 16
    else:
        for ev in list(sec_state.security_log)[-4:]:
            w_txt = f"{ev.get('width_cm', 0)}cm" if ev.get('width_cm', 0) > 0 else ""
            log_line = f"[{ev['time_str']}] {ev['dist_cm']}cm ({w_txt}) @ {ev['angle']}deg - {ev['sector'].split(' ')[0]}"
            cv2.putText(canvas, log_line, (panel_x + 15, py),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 120, 120), 1, cv2.LINE_AA)
            py += 16

    # 7. Hardverski status i kontrole na dnu panela
    bot_y = WIN_H - 110
    cv2.line(canvas, (panel_x + 15, bot_y), (panel_x + panel_w - 15, bot_y), (40, 55, 75), 1)
    bot_y += 18

    if has_live_data:
        hw_txt = f"LiDAR: AKTIVAN ({port_txt} @ {baud_val})"
        hw_col = (0, 255, 100)
    elif is_connected:
        hw_txt = f"LiDAR: POVEZAN ({port_txt}) - Čekam sken..."
        hw_col = (0, 200, 255)
    else:
        hw_txt = f"LiDAR: NIJE PRONAĐEN (Tražim USB...)"
        hw_col = (0, 165, 255)

    cv2.putText(canvas, hw_txt, (panel_x + 15, bot_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, hw_col, 1, cv2.LINE_AA)

    bot_y += 18
    cv2.putText(canvas, f"Brzina skena: {pps_val} tačaka/s", (panel_x + 15, bot_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 180, 200), 1, cv2.LINE_AA)
    bot_y += 16
    cv2.putText(canvas, "[k] Nova kalibracija  |  [+] / [-] Domet", (panel_x + 15, bot_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 230, 255), 1, cv2.LINE_AA)
    bot_y += 16
    cv2.putText(canvas, "[b] Oblik zone  |  [m] Mute  |  [r] Reset  |  [q] Izlaz", (panel_x + 15, bot_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (160, 180, 200), 1, cv2.LINE_AA)


# ------------------------------------------------------------------------------
# GLAVNA PETLJA PROGRAMA
# ------------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("  RPLIDAR C1 — SIGURNOSNA BARIJERA SA FILTERIMA MALIH OBJEKATA I POMERAJA")
    print("=" * 70)
    print("1. Inicijalno skeniranje (3.5s) uči statički prostor i nameštaj.")
    print("2. Filter malih pomeraja: Zahteva pomak od bar 20 cm od pozadine.")
    print("3. Filter malih objekata: Ignoriše objekte uže od 14 cm i ispod 4 tačke.")
    print("4. Debouncer: Zahteva potvrdu u 3 uzastopna ciklusa pre alarma.")
    print("Kontrole:")
    print("  [k]        - Ponovna kalibracija (novo skeniranje prostora)")
    print("  [+] / [-]  - Povećaj / smanji distancu barijere (0.4m - 2.4m)")
    print("  [b]        - Promeni oblik barijere (360° Krug <-> Frontalno 120° <-> Koridor)")
    print("  [m]        - Uključi / isključi zvučni alarm (Mute)")
    print("  [r]        - Ponovo skeniraj USB portove / Resetuj vezu sa LiDAR-om")
    print("  [q] / ESC  - Izlaz")
    print("=" * 70)

    # Pokretanje radne niti za pravi LiDAR
    t_lidar = threading.Thread(target=lidar_thread_loop, daemon=True)
    t_lidar.start()

    win_name = "RPLIDAR C1 - Sigurnosna Barijera i Alarm (RPi 5)"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win_name, WIN_W, WIN_H)

    canvas = np.zeros((WIN_H, WIN_W, 3), dtype=np.uint8)

    while True:
        draw_radar_and_dashboard(canvas)
        cv2.imshow(win_name, canvas)

        key = cv2.waitKey(25) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('k') or key == ord('K'):
            with sec_state.lock:
                sec_state.start_calibration()
        elif key == ord('+') or key == ord('='):
            with sec_state.lock:
                sec_state.barrier_dist_m = min(2.4, round(sec_state.barrier_dist_m + 0.1, 2))
                print(f"[BARIJERA] Distanca povećana na: {sec_state.barrier_dist_m:.1f} m")
        elif key == ord('-') or key == ord('_'):
            with sec_state.lock:
                sec_state.barrier_dist_m = max(0.4, round(sec_state.barrier_dist_m - 0.1, 2))
                print(f"[BARIJERA] Distanca smanjena na: {sec_state.barrier_dist_m:.1f} m")
        elif key == ord('b'):
            with sec_state.lock:
                sec_state.barrier_type_idx = (sec_state.barrier_type_idx + 1) % len(BARRIER_TYPES)
                b_name = BARRIER_NAMES[BARRIER_TYPES[sec_state.barrier_type_idx]]
                print(f"[BARIJERA] Promenjen oblik zone: {b_name}")
        elif key == ord('m'):
            sound_controller.muted = not sound_controller.muted
            status_str = "MUTIRAN" if sound_controller.muted else "UKLJUČEN"
            print(f"[ZVUK] Zvučni alarm: {status_str}")
        elif key == ord('r'):
            with sec_state.lock:
                sec_state.total_incidents = 0
                sec_state.security_log.clear()
                sec_state.alarm_active = False
                sec_state.reconnect_requested = True
                print("[BARIJERA] Zahtev za ponovno povezivanje sa senzorom...")

    sec_state.running = False
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
