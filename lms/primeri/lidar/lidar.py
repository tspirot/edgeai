#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
       RPLIDAR C1 — 360° LASERSKI RADAR & SKENER (Raspberry Pi 5)
================================================================================
Aplikacija za vizuelizaciju i testiranje Slamtec RPLIDAR C1 laserskog senzora.
Povezuje se preko USB porta (460800 baud) i prikazuje tačke u realnom vremenu
na TV/HDMI ekranu sa detekcijom prepreka, merenjem udaljenosti i više tema.
"""

import os
import sys
import time
import math
import threading
import numpy as np
import cv2

# Osiguravanje prikaza na lokalnom TV ekranu kada se pokreće preko SSH
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

# Uvoz biblioteka za serijsku komunikaciju i LiDAR
try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("[GRESKA] 'pyserial' nije instaliran! Pokrenite: pip install pyserial")
    sys.exit(1)

try:
    from rplidar import RPLidar, RPLidarException
    RPLIDAR_LIB_AVAILABLE = True
except ImportError:
    RPLIDAR_LIB_AVAILABLE = False
    print("[UPOZORENJE] 'rplidar-roboticia' biblioteka nije pronađena.")

# ------------------------------------------------------------------------------
# KONFIGURACIJA I PARAMETRI RPLIDAR C1
# ------------------------------------------------------------------------------
DEFAULT_BAUDRATE = 460800   # RPLIDAR C1 fabrički standardni baudrate
FALLBACK_BAUDRATES = [460800, 256000, 115200]
MAX_RANGES_M = [2.0, 4.0, 6.0, 8.0, 12.0]
DEFAULT_RANGE_IDX = 1       # 4.0 metra podrazumevano

# Dimenzije prozora za prikaz
WIN_W = 1020
WIN_H = 720
RADAR_CX = 430
RADAR_CY = 360
RADAR_RADIUS = 310

# Teme prikaza boja
THEMES = [
    {
        "name": "Sajber Neon (Cyan / Plava)",
        "bg": (12, 16, 24),
        "grid": (45, 60, 80),
        "grid_text": (120, 150, 180),
        "sweep": (255, 220, 0),
        "point_near": (0, 70, 255),    # Crvena za preblizu
        "point_mid": (0, 240, 255),    # Žuta za srednje
        "point_far": (255, 230, 0),    # Cijan za daleko
        "accent": (255, 200, 0)
    },
    {
        "name": "Vojni Radar (Zeleni fosfor)",
        "bg": (8, 20, 10),
        "grid": (20, 70, 30),
        "grid_text": (60, 180, 80),
        "sweep": (0, 255, 100),
        "point_near": (0, 0, 255),
        "point_mid": (0, 220, 255),
        "point_far": (50, 255, 50),
        "accent": (50, 255, 50)
    },
    {
        "name": "Termalni Heatmap",
        "bg": (15, 10, 20),
        "grid": (60, 40, 70),
        "grid_text": (160, 130, 180),
        "sweep": (255, 100, 255),
        "point_near": (0, 0, 255),
        "point_mid": (0, 165, 255),
        "point_far": (255, 50, 180),
        "accent": (255, 100, 255)
    }
]

# ------------------------------------------------------------------------------
# GLOBALNO STANJE SKENERA
# ------------------------------------------------------------------------------
class LidarState:
    def __init__(self):
        self.lock = threading.Lock()
        self.connected = False
        self.simulation_mode = False
        self.port_name = "Nije pronađen"
        self.baudrate = DEFAULT_BAUDRATE
        self.device_info = {}
        self.device_health = "Nepoznato"
        self.points = {}            # int(angle) -> (dist_mm, quality, timestamp)
        self.current_sweep_angle = 0.0
        self.scan_rate_hz = 0.0
        self.points_per_sec = 0
        self.min_dist_mm = 0
        self.min_dist_angle = 0
        self.running = True
        self.motor_running = True
        self.active_range_idx = DEFAULT_RANGE_IDX
        self.theme_idx = 0
        self.status_msg = "Inicijalizacija..."
        self.reconnect_requested = False

state = LidarState()


def pronadji_usb_port():
    """Automatski pronalazi ttyUSB ili ttyACM port na kome je povezan RPLIDAR."""
    # 1. Provera standardnih Linux USB serijskih portova
    preferred = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
    for p in preferred:
        if os.path.exists(p):
            return p

    # 2. Pretraga preko serial.tools
    try:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            name = p.device
            desc = p.description.lower()
            if any(k in desc for k in ["cp210", "ch340", "ftdi", "silicon", "rplidar", "usb serial"]):
                return name
            if "ttyusb" in name.lower() or "ttyacm" in name.lower():
                return name
    except Exception:
        pass

    return None


# ------------------------------------------------------------------------------
# RADNA NIT ZA PRIHVAT PODATAKA SA LIDAR-A
# ------------------------------------------------------------------------------
def lidar_worker_thread():
    """Pozadinska nit koja održava vezu sa senzorom i prikuplja merenja."""
    lidar_obj = None

    while state.running:
        if state.simulation_mode:
            time.sleep(0.05)
            continue

        port = pronadji_usb_port()

        if not port:
            with state.lock:
                state.connected = False
                state.port_name = "Čekam USB vezu..."
                state.status_msg = "LiDAR nije pronađen. Povežite USB kabl (ili pritisnite 's' za simulaciju)"
            time.sleep(1.0)
            continue

        with state.lock:
            state.port_name = port
            state.status_msg = f"Povezujem se na {port} ({state.baudrate} baud)..."

        print(f"\n[LIDAR] Pokušavam povezivanje na {port} sa brzinom {state.baudrate}...")

        lidar_obj = None
        # Pokušaj otvaranja porta preko rplidar biblioteke
        for baud in [state.baudrate] + [b for b in FALLBACK_BAUDRATES if b != state.baudrate]:
            try:
                lidar_obj = RPLidar(port, baudrate=baud, timeout=2)
                # Test komande
                info = lidar_obj.get_info()
                health = lidar_obj.get_health()

                with state.lock:
                    state.connected = True
                    state.baudrate = baud
                    state.device_info = info
                    state.device_health = health[0] if isinstance(health, tuple) else str(health)
                    state.status_msg = f"Povezan ({info.get('model', 'C1')}, FW: {info.get('firmware', 'N/A')})"

                print(f"[LIDAR] Uspešno povezan! Model: {info.get('model')}, Zdravlje: {state.device_health}")
                break
            except Exception as e:
                print(f"[LIDAR] Baud {baud} nije uspeo: {e}")
                if lidar_obj:
                    try:
                        lidar_obj.disconnect()
                    except Exception:
                        pass
                lidar_obj = None
                time.sleep(0.5)

        if not lidar_obj:
            with state.lock:
                state.connected = False
                state.status_msg = f"Greška pri otvaranju {port}. Provera drajvera/dozvola..."
            time.sleep(1.5)
            continue

        # Glavna petlja čitanja merenja
        last_scan_time = time.time()
        scans_count = 0
        points_count = 0
        stat_time = time.time()

        try:
            lidar_obj.start_motor()
            time.sleep(0.5)

            for scan in lidar_obj.iter_scans(max_buf_meas=1000):
                if not state.running or state.simulation_mode or state.reconnect_requested:
                    with state.lock:
                        state.reconnect_requested = False
                    break

                now = time.time()
                scans_count += 1
                points_count += len(scan)

                if now - stat_time >= 1.0:
                    with state.lock:
                        state.scan_rate_hz = scans_count / (now - stat_time)
                        state.points_per_sec = int(points_count / (now - stat_time))
                    scans_count = 0
                    points_count = 0
                    stat_time = now

                # Obrada tačaka iz skena
                local_min_dist = 99999
                local_min_angle = 0

                with state.lock:
                    for quality, angle, dist_mm in scan:
                        if dist_mm > 0:
                            deg = int(round(angle)) % 360
                            state.points[deg] = (dist_mm, quality, now)
                            state.current_sweep_angle = angle

                            if dist_mm < local_min_dist and dist_mm > 40:
                                local_min_dist = dist_mm
                                local_min_angle = deg

                    if local_min_dist < 99999:
                        state.min_dist_mm = local_min_dist
                        state.min_dist_angle = local_min_angle

        except Exception as e:
            print(f"[LIDAR] Prekid toka merenja: {e}")
            with state.lock:
                state.connected = False
                state.status_msg = f"Prekid veze: {e}"
        finally:
            if lidar_obj:
                try:
                    lidar_obj.stop()
                    lidar_obj.stop_motor()
                    lidar_obj.disconnect()
                except Exception:
                    pass
            time.sleep(1.0)


# ------------------------------------------------------------------------------
# SIMULATOR ZA TEST BEZ HARDVERA
# ------------------------------------------------------------------------------
def generisi_simulaciju():
    """Generiše virtuelnu sobu sa preprekama za test kada LiDAR nije povezan."""
    now = time.time()
    with state.lock:
        state.connected = True
        state.port_name = "SIMULACIJA (Demo)"
        state.device_health = "Good (Simulated)"
        state.scan_rate_hz = 10.0
        state.points_per_sec = 4200
        state.status_msg = "Aktivna simulacija (pritisnite 's' za USB mod)"

        # Simulirana soba 4x4 metra sa dve prepreke
        room_w = 3200
        room_h = 3200
        t = now * 1.5

        # Rotirajući ugao
        sweep = (now * 360.0 * 2.0) % 360.0
        state.current_sweep_angle = sweep

        local_min_dist = 99999
        local_min_angle = 0

        for a in range(360):
            rad = math.radians(a)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            # Zidovi sobe
            dist_x = (room_w / 2.0) / abs(cos_a) if abs(cos_a) > 0.05 else 9999
            dist_y = (room_h / 2.0) / abs(sin_a) if abs(sin_a) > 0.05 else 9999
            wall_dist = min(dist_x, dist_y)

            # Simulirana prepreka (stub / čovek koji se kreće)
            obs1_angle = (110 + math.sin(t) * 25)
            obs1_dist = 1100 + math.cos(t) * 150
            if abs(a - obs1_angle) < 8:
                wall_dist = min(wall_dist, obs1_dist)

            # Druga fiksna prepreka
            if abs(a - 240) < 12:
                wall_dist = min(wall_dist, 750)

            # Blagi šum senzora
            dist_mm = max(60, wall_dist + (math.sin(a * 5 + t) * 15))
            state.points[a] = (dist_mm, 15, now)

            if dist_mm < local_min_dist:
                local_min_dist = dist_mm
                local_min_angle = a

        state.min_dist_mm = local_min_dist
        state.min_dist_angle = local_min_angle


# ------------------------------------------------------------------------------
# ISCRTAVANJE RADARA I KORISNIČKOG INTERFEJSA
# ------------------------------------------------------------------------------
def renderuj_radar(canvas, theme, max_range_m):
    """Iscrtava kružnu radarsku mrežu, podeoke, liniju skeniranja i oblak tačaka."""
    cx, cy = RADAR_CX, RADAR_CY
    radius = RADAR_RADIUS

    # 1. Pozadinski krug radara
    cv2.circle(canvas, (cx, cy), radius, (theme["bg"][0] + 5, theme["bg"][1] + 5, theme["bg"][2] + 8), -1)

    # 2. Koncentrični krugovi udaljenosti (Podeoci)
    step_m = max_range_m / 4.0
    for i in range(1, 5):
        r_dist = int((i / 4.0) * radius)
        cv2.circle(canvas, (cx, cy), r_dist, theme["grid"], 1, cv2.LINE_AA)
        dist_lbl = f"{i * step_m:.1f}m"
        cv2.putText(canvas, dist_lbl, (cx + 8, cy - r_dist + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.40, theme["grid_text"], 1, cv2.LINE_AA)

    # 3. Zrakasti ugaoni podeoci (svakih 30 i 45 stepeni)
    angles_deg = [0, 45, 90, 135, 180, 225, 270, 315]
    for ad in angles_deg:
        rad = math.radians(ad)
        x2 = int(cx + radius * math.cos(rad))
        y2 = int(cy - radius * math.sin(rad))
        cv2.line(canvas, (cx, cy), (x2, y2), theme["grid"], 1, cv2.LINE_AA)

        # Oznake uglova oko spoljne ivice
        lx = int(cx + (radius + 16) * math.cos(rad)) - 10
        ly = int(cy - (radius + 16) * math.sin(rad)) + 5
        cv2.putText(canvas, f"{ad}°", (lx, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, theme["grid_text"], 1, cv2.LINE_AA)

    # 4. Bezbednosna zona upozorenja (< 50cm = Crveni prsten)
    warn_radius_px = int((0.50 / max_range_m) * radius)
    if warn_radius_px > 5:
        cv2.circle(canvas, (cx, cy), warn_radius_px, (0, 0, 180), 1, cv2.LINE_AA)

    # 5. Iscrtavanje radarske linije skeniranja (Sweep line)
    sweep_rad = math.radians(state.current_sweep_angle)
    sx = int(cx + radius * math.cos(sweep_rad))
    sy = int(cy - radius * math.sin(sweep_rad))
    cv2.line(canvas, (cx, cy), (sx, sy), theme["sweep"], 2, cv2.LINE_AA)

    # 6. Iscrtavanje tačaka sa LiDAR senzora
    now = time.time()
    max_dist_mm = max_range_m * 1000.0

    with state.lock:
        pts_snapshot = list(state.points.items())

    for deg, (dist_mm, quality, t_point) in pts_snapshot:
        # Tačke starije od 1.5 sekunde blede/ignorišu se
        age = now - t_point
        if age > 1.2 or dist_mm <= 0:
            continue

        if dist_mm > max_dist_mm:
            continue

        # Polarna u Dekartove koordinate
        # 0 stepeni je pravo napred (vrh ekrana u robotici)
        rad = math.radians(deg)
        dist_px = (dist_mm / max_dist_mm) * radius
        px = int(cx + dist_px * math.sin(rad))
        py = int(cy - dist_px * math.cos(rad))

        # Boja tačke u zavisnosti od udaljenosti
        ratio = dist_mm / max_dist_mm
        if ratio < 0.20:
            p_color = theme["point_near"]   # Veoma blizu
            pt_size = 3
        elif ratio < 0.60:
            p_color = theme["point_mid"]    # Srednja udaljenost
            pt_size = 2
        else:
            p_color = theme["point_far"]    # Daleko
            pt_size = 2

        cv2.circle(canvas, (px, py), pt_size, p_color, -1, cv2.LINE_AA)

    # 7. Centar (Mesto samog LiDAR senzora)
    cv2.circle(canvas, (cx, cy), 7, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(canvas, (cx, cy), 9, theme["accent"], 1, cv2.LINE_AA)
    cv2.putText(canvas, "RPLIDAR", (cx - 28, cy + 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.40, (200, 200, 200), 1, cv2.LINE_AA)


def renderuj_panel(canvas, theme, max_range_m):
    """Iscrtava desni informativni HUD panel sa statusom, telemetrijom i kontrolama."""
    px = 750
    py = 25
    pw = WIN_W - px - 20
    ph = WIN_H - 45

    # Panel pozadina
    cv2.rectangle(canvas, (px, py), (px + pw, py + ph), (18, 24, 38), -1)
    cv2.rectangle(canvas, (px, py), (px + pw, py + ph), (45, 60, 85), 1)

    # Zaglavlje panela
    cv2.rectangle(canvas, (px, py), (px + pw, py + 50), (25, 34, 52), -1)
    cv2.putText(canvas, "RPLIDAR C1 HUD", (px + 16, py + 34),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

    # Status konekcije
    with state.lock:
        is_conn = state.connected
        port = state.port_name
        baud = state.baudrate
        health = state.device_health
        rate_hz = state.scan_rate_hz
        pts_sec = state.points_per_sec
        pts_count = len(state.points)
        min_d = state.min_dist_mm
        min_a = state.min_dist_angle
        status_msg = state.status_msg

    status_col = (0, 220, 0) if is_conn else (0, 165, 255)
    status_txt = "POVEZAN (ONLINE)" if is_conn else "SKENIRAM PORTOVE..."
    cv2.circle(canvas, (px + 20, py + 80), 6, status_col, -1, cv2.LINE_AA)
    cv2.putText(canvas, status_txt, (px + 36, py + 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_col, 2, cv2.LINE_AA)

    # Kartica parametara
    y = py + 120
    items = [
        ("Port uređaja:", str(port)),
        ("Brzina (Baud):", f"{baud} bps"),
        ("Zdravlje senzora:", str(health)),
        ("Frekvencija skena:", f"{rate_hz:.1f} Hz"),
        ("Tačaka u sekundi:", f"{pts_sec:,} pts/s"),
        ("Aktivne tačke (360°):", f"{pts_count} uglova"),
        ("Domet prikaza (Zoom):", f"{max_range_m:.1f} m"),
        ("Tema ekrana:", theme["name"][:16])
    ]

    for label, val in items:
        cv2.putText(canvas, label, (px + 16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (140, 160, 180), 1)
        cv2.putText(canvas, val, (px + 140, y), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (255, 255, 255), 1)
        y += 28

    # Kartica najbliže prepreke (Radar Warning)
    y += 10
    cv2.rectangle(canvas, (px + 12, y), (px + pw - 12, y + 80), (28, 20, 24), -1)
    is_alert = (min_d > 0 and min_d < 500)
    border_col = (0, 0, 255) if is_alert else (60, 80, 100)
    cv2.rectangle(canvas, (px + 12, y), (px + pw - 12, y + 80), border_col, 2 if is_alert else 1)

    warn_title = "⚠️ UPOZORENJE NA PREPREKU!" if is_alert else "NAJBLIŽA PREPREKA"
    warn_col = (0, 0, 255) if is_alert else (255, 200, 0)
    cv2.putText(canvas, warn_title, (px + 22, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, warn_col, 2, cv2.LINE_AA)

    if min_d > 0:
        cv2.putText(canvas, f"Udaljenost: {min_d / 10.0:.1f} cm", (px + 22, y + 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1)
        cv2.putText(canvas, f"Ugao: {min_a}°", (px + 22, y + 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, (200, 220, 255), 1)
    else:
        cv2.putText(canvas, "Nema prepreka u dometu", (px + 22, y + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 160, 160), 1)

    # Donji kontrolni tasteri
    y += 105
    cv2.putText(canvas, "KONTROLE & TASTERI:", (px + 16, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 200, 0), 1)
    y += 24

    controls = [
        ("[+]/[-]", "Povećaj / Smanji domet (Zoom)"),
        ("[s]", "Uključi / Isključi SIMULACIJU"),
        ("[c]", "Promeni temu boja ekrana"),
        ("[r]", "Osveži vezu / Ponovo pretraži USB"),
        ("[m]", "Pali / Gasi motor skenera"),
        ("[q] / [ESC]", "Izlaz iz programa")
    ]

    for key_name, desc in controls:
        cv2.putText(canvas, key_name, (px + 16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 220, 255), 1)
        cv2.putText(canvas, desc, (px + 76, y), cv2.FONT_HERSHEY_SIMPLEX, 0.40, (190, 200, 215), 1)
        y += 22

    # Donja statusna poruka
    cv2.putText(canvas, status_msg[:38], (20, WIN_H - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 180, 200), 1)


# ------------------------------------------------------------------------------
# GLAVNA PETLJA PROGRAMA
# ------------------------------------------------------------------------------
def main():
    print("=" * 70)
    print("      RPLIDAR C1 — 360° LASERSKI SKENER & RADAR (RPi 5)")
    print("=" * 70)
    print(f"Fabrički baudrate: {DEFAULT_BAUDRATE}")
    print("Tražim povezane USB adaptere (/dev/ttyUSB* ili /dev/ttyACM*)...")
    print("Kontrole: [s] Simulacija | [+/-] Zoom | [c] Tema | [q] Izlaz\n")

    # Pokretanje pozadinske niti za LiDAR komunikaciju
    worker = threading.Thread(target=lidar_worker_thread, daemon=True)
    worker.start()

    window_name = "RPLIDAR C1 - 360 Radar & Skener (Raspberry Pi 5)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, WIN_W, WIN_H)

    try:
        while state.running:
            # 1. Priprema platna sa bojom teme
            theme = THEMES[state.theme_idx]
            canvas = np.full((WIN_H, WIN_W, 3), theme["bg"], dtype=np.uint8)

            max_range_m = MAX_RANGES_M[state.active_range_idx]

            # 2. Ako je aktivna simulacija, generiši virtuelne podatke
            if state.simulation_mode:
                generisi_simulaciju()

            # 3. Iscrtavanje radara i HUD-a
            renderuj_radar(canvas, theme, max_range_m)
            renderuj_panel(canvas, theme, max_range_m)

            cv2.imshow(window_name, canvas)

            # 4. Obrada tastature
            key = cv2.waitKey(25) & 0xFF
            if key == ord('q') or key == 27:
                print("\n[INFO] Gašenje aplikacije...")
                break
            elif key == ord('+') or key == ord('='):
                state.active_range_idx = min(len(MAX_RANGES_M) - 1, state.active_range_idx + 1)
                print(f"[ZOOM] Domet postavljen na: {MAX_RANGES_M[state.active_range_idx]} m")
            elif key == ord('-') or key == ord('_'):
                state.active_range_idx = max(0, state.active_range_idx - 1)
                print(f"[ZOOM] Domet postavljen na: {MAX_RANGES_M[state.active_range_idx]} m")
            elif key == ord('c'):
                state.theme_idx = (state.theme_idx + 1) % len(THEMES)
                print(f"[TEMA] Izabrana tema: {THEMES[state.theme_idx]['name']}")
            elif key == ord('s'):
                state.simulation_mode = not state.simulation_mode
                print(f"[MOD] Simulacija: {'UKLJUČENA' if state.simulation_mode else 'ISKLJUČENA'}")
                if not state.simulation_mode:
                    state.points.clear()
            elif key == ord('r'):
                print("[INFO] Zatraženo ponovno povezivanje na senzor...")
                with state.lock:
                    state.reconnect_requested = True

    finally:
        state.running = False
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
