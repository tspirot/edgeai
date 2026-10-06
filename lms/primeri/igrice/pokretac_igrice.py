#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
       🎈 DEČIJE CARSTVO — POKRETAČ SVIH IGRICA ZA PREDŠKOLCE (RPi 5)
================================================================================
Opis:
  Glavni grafički centar za sve dečije igrice na Raspberry Pi 5.
  Pokretač ostaje stalno otvoren u velikom prozoru prilagođenom TV ekranu!
  Kada pokrenete novu igricu, prethodno pokrenuta se automatski zaustavlja
  i oslobađa kameru, tako da možete birati i menjati igrice bez gašenja menija.

Kontrole:
  - [Klik mišem] na karticu za pokretanje ili zaustavljanje igrice
  - [1 - 6] Direktno pokretanje odabrane igrice
  - [s] ili [Space] Zaustavi trenutno aktivnu igricu
  - [f] Prebaci ceo ekran (Fullscreen)
  - [q] ili [ESC] Izlaz iz pokretača
================================================================================
"""

import os
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

import sys
import time
import subprocess
import threading
from pathlib import Path
import cv2
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
PYTHON_EXE = sys.executable

rpi_venv = Path("/home/pi/primeri/env/bin/python")
if rpi_venv.exists():
    PYTHON_EXE = str(rpi_venv)

# Velike Full HD dimenzije prilagođene TV ekranima
CANVAS_W = 1920
CANVAS_H = 1080
WINDOW_NAME = "Decije Carstvo - Igrice za Predskolce (RPi 5)"

# Pronađi putanju do sortiranja (bilo u primeri/sortiranje ili lokalno)
sortiranje_path = Path("/home/pi/primeri/sortiranje/sortiranje.py")
if not sortiranje_path.exists():
    sortiranje_path = BASE_DIR.parent / "sortiranje" / "sortiranje.py"

GAMES = [
    {
        "id": "baloni",
        "num": "1",
        "title": "CAROBNI MEHURICI",
        "icon": "🎈",
        "badge": "PUCKANJE BALONA",
        "desc": "Mahite rukom u vazduhu i busite balone uz zvuk POP i zvezdice!",
        "script": str(BASE_DIR / "baloni" / "baloni.py"),
        "color": (40, 50, 235),
        "border": (100, 160, 255)
    },
    {
        "id": "nahrani",
        "num": "2",
        "title": "NAHRANI ZIVOTINJE",
        "icon": "🥕",
        "badge": "ZEKA, KUCA, MACA",
        "desc": "Prinesite zeki sargarepu, kuci koscicu, a maci ribicu!",
        "script": str(BASE_DIR / "nahrani" / "nahrani.py"),
        "color": (20, 140, 60),
        "border": (80, 245, 140)
    },
    {
        "id": "crtanje",
        "num": "3",
        "title": "CAROBNI STAPIC",
        "icon": "✨",
        "badge": "SVETLECI TRAG",
        "desc": "Kažiprst postaje čarobni štapić koji crta duginim svetlom!",
        "script": str(BASE_DIR / "crtanje" / "crtanje.py"),
        "color": (160, 50, 150),
        "border": (240, 120, 230)
    },
    {
        "id": "korpica",
        "num": "4",
        "title": "UHVATI ZVEZDICE",
        "icon": "🧺",
        "badge": "KORPICA U RUCI",
        "desc": "Pomerajte ruku levo-desno i pecajte zvezdice sa neba!",
        "script": str(BASE_DIR / "korpica" / "korpica.py"),
        "color": (210, 110, 30),
        "border": (250, 190, 100)
    },
    {
        "id": "ogledalo",
        "num": "5",
        "title": "SMESNO OGLEDALO",
        "icon": "🐱",
        "badge": "MASKE I MIMIKA",
        "desc": "Stavite uši mace, kuce ili krunu! Otvorite usta za čaroliju!",
        "script": str(BASE_DIR / "ogledalo" / "ogledalo.py"),
        "color": (30, 150, 240),
        "border": (100, 220, 255)
    },
    {
        "id": "sortiranje",
        "num": "6",
        "title": "SPAJANJE SLICICA",
        "icon": "🧩",
        "badge": "SLAGALICA OBLIKA",
        "desc": "Uhvatite sličicu prstićima i spojite je sa njenom kućicom!",
        "script": str(sortiranje_path),
        "color": (140, 70, 40),
        "border": (220, 160, 120)
    }
]

# Pozicije kartica na 1920x1080 ekranu
CARD_W = 540
CARD_H = 360
ROW1_Y = 220
ROW2_Y = 620
COLS_X = [90, 690, 1290]

card_rects = []
for idx in range(len(GAMES)):
    col = idx % 3
    row = idx // 3
    x = COLS_X[col]
    y = ROW1_Y if row == 0 else ROW2_Y
    card_rects.append((x, y, CARD_W, CARD_H))

# Upravljanje procesima igara (non-blocking)
current_game_process = None
active_game_id = None
active_game_title = None

def zaustavi_trenutnu_igru():
    """Zaustavlja aktivnu igricu i oslobađa kameru."""
    global current_game_process, active_game_id, active_game_title
    if current_game_process is not None:
        print(f"[POKRETAČ] Zaustavljam igricu PID {current_game_process.pid}...")
        try:
            current_game_process.terminate()
            try:
                current_game_process.wait(timeout=1.5)
            except subprocess.TimeoutExpired:
                current_game_process.kill()
        except Exception as e:
            print(f"[UPOZORENJE] Greška pri zaustavljanju: {e}")
        current_game_process = None

    active_game_id = None
    active_game_title = None

    # Sigurnosno gašenje procesa koji drže kameru
    try:
        subprocess.run(["pkill", "-f", "(baloni|nahrani|crtanje|korpica|ogledalo|sortiranje)\\.py"], capture_output=True)
    except Exception:
        pass
    time.sleep(0.35)

def monitor_game_process(proc, g_id):
    """Prati kada se igrica završi samostalno (npr. korisnik pritisne 'q')."""
    global current_game_process, active_game_id, active_game_title
    proc.wait()
    if active_game_id == g_id:
        active_game_id = None
        active_game_title = None
        current_game_process = None
        print(f"[POKRETAČ] Igrica '{g_id}' je završena.")

def pokreni_igru(idx):
    """Zaustavlja staru igru i pokreće novu bez gašenja menija."""
    global current_game_process, active_game_id, active_game_title
    g = GAMES[idx]

    # Ako je ista igra već pokrenuta, zaustavi je (toggle)
    if active_game_id == g["id"]:
        zaustavi_trenutnu_igru()
        return

    # Zaustavi prethodnu igru
    zaustavi_trenutnu_igru()

    script_path = g["script"]
    if not os.path.exists(script_path):
        print(f"[GREŠKA] Fajl ne postoji: {script_path}")
        return

    print("=" * 60)
    print(f"🚀 POKREĆEM IGRU: {g['title']}")
    print(f"📂 Putanja: {script_path}")
    print("=" * 60)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["DISPLAY"] = os.environ.get("DISPLAY", ":0")
    env["WAYLAND_DISPLAY"] = os.environ.get("WAYLAND_DISPLAY", "wayland-0")

    try:
        proc = subprocess.Popen(
            [PYTHON_EXE, script_path],
            cwd=str(Path(script_path).parent),
            env=env
        )
        current_game_process = proc
        active_game_id = g["id"]
        active_game_title = g["title"]

        t = threading.Thread(target=monitor_game_process, args=(proc, g["id"]), daemon=True)
        t.start()
    except Exception as e:
        print(f"[GREŠKA] Nije uspelo pokretanje: {e}")

mouse_x, mouse_y = -1, -1
clicked_idx = None
stop_btn_rect = (CANVAS_W - 380, 45, 300, 75)

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y, clicked_idx
    mouse_x, mouse_y = x, y
    if event == cv2.EVENT_LBUTTONDOWN:
        # Provera da li je kliknuto na crveno dugme "ZAUSTAVI IGRU"
        bx, by, bw, bh = stop_btn_rect
        if active_game_id is not None and bx <= x <= bx + bw and by <= y <= by + bh:
            zaustavi_trenutnu_igru()
            return

        for i, (rx, ry, rw, rh) in enumerate(card_rects):
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                clicked_idx = i
                break

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, CANVAS_W, CANVAS_H)
cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

is_fullscreen = False

print("=" * 65)
print("DEČIJE CARSTVO — POKRETAČ IGRICA POKRENUT (FULL-SIZE)")
print("Izaberite igru klikom mišem ili tasterima [1 - 6]")
print("Pokretač ostaje aktivan — prelazak sa jedne igre na drugu je automatski!")
print("Kontrole: [1-6] Izbor igre  |  [s] Zaustavi igru  |  [f] Fullscreen  |  [q] Izlaz")
print("=" * 65)

while True:
    # 1. Pozadina
    canvas = np.zeros((CANVAS_H, CANVAS_W, 3), dtype=np.uint8)
    canvas[:] = (32, 18, 26)

    # Nežni sjajni centri
    cv2.circle(canvas, (CANVAS_W // 2, CANVAS_H // 2), 700, (48, 28, 38), -1)
    cv2.circle(canvas, (CANVAS_W // 2, CANVAS_H // 2), 380, (68, 38, 52), -1)

    # 2. Gornje zaglavlje (HUD)
    cv2.rectangle(canvas, (50, 30), (CANVAS_W - 50, 160), (22, 14, 18), -1)
    cv2.rectangle(canvas, (50, 30), (CANVAS_W - 50, 160), (0, 215, 255), 3)

    cv2.putText(canvas, "🎈 DECIJE CARSTVO — IGRICE ZA PREDSKOLCE", (85, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 1.45, (255, 255, 255), 3, cv2.LINE_AA)

    if active_game_id is not None:
        status_txt = f"AKTIVNA IGRA: {active_game_title} (KLIKNITE DRUGU IGRU DA PREBACITE)"
        cv2.putText(canvas, status_txt, (88, 138), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 150), 2, cv2.LINE_AA)

        # Dugme ZAUSTAVI IGRU u gornjem desnom uglu
        bx, by, bw, bh = stop_btn_rect
        is_hover_stop = (bx <= mouse_x <= bx + bw and by <= mouse_y <= by + bh)
        s_col = (40, 40, 235) if is_hover_stop else (30, 30, 180)
        cv2.rectangle(canvas, (bx, by), (bx + bw, by + bh), s_col, -1)
        cv2.rectangle(canvas, (bx, by), (bx + bw, by + bh), (120, 120, 255), 2)
        cv2.putText(canvas, "⏹ ZAUSTAVI IGRU", (bx + 35, by + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        cv2.putText(canvas, "KLIKNITE MISEM ILI PRITISNITE BROJ [1 - 6] DA POKRENETE IGRU", (88, 138),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 230, 255), 2, cv2.LINE_AA)

    # 3. Iscrtavanje velikih kartica igara
    for i, (rx, ry, rw, rh) in enumerate(card_rects):
        g = GAMES[i]
        is_active = (active_game_id == g["id"])
        is_hover = (rx <= mouse_x <= rx + rw and ry <= mouse_y <= ry + rh)

        if is_active:
            border_col = (0, 255, 120)
            border_th = 6
            bg_col = (40, 75, 50)
        elif is_hover:
            border_col = g["border"]
            border_th = 5
            bg_col = (75, 48, 62)
        else:
            border_col = (110, 75, 88)
            border_th = 3
            bg_col = (50, 32, 42)

        # Senka kartice
        cv2.rectangle(canvas, (rx + 6, ry + 8), (rx + rw + 6, ry + rh + 8), (12, 6, 8), -1)
        # Glavno telo kartice
        cv2.rectangle(canvas, (rx, ry), (rx + rw, ry + rh), bg_col, -1)
        cv2.rectangle(canvas, (rx, ry), (rx + rw, ry + rh), border_col, border_th)

        # Obojena traka na vrhu kartice
        top_bar_col = (0, 180, 80) if is_active else g["color"]
        cv2.rectangle(canvas, (rx, ry), (rx + rw, ry + 68), top_bar_col, -1)

        # Broj i bedž
        num_str = f"[{g['num']}]"
        cv2.putText(canvas, num_str, (rx + 20, ry + 48),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.15, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(canvas, g["badge"], (rx + 95, ry + 46),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 255, 255), 2, cv2.LINE_AA)

        # Naziv igrice
        title_col = (0, 255, 180) if is_active else ((0, 240, 255) if is_hover else (255, 255, 255))
        cv2.putText(canvas, g["title"], (rx + 25, ry + 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.95, title_col, 3, cv2.LINE_AA)

        # Opis na 2-3 linije
        words = g["desc"].split(" ")
        l1 = " ".join(words[:6])
        l2 = " ".join(words[6:12])
        l3 = " ".join(words[12:])
        cv2.putText(canvas, l1, (rx + 25, ry + 175), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (225, 225, 225), 1, cv2.LINE_AA)
        if l2:
            cv2.putText(canvas, l2, (rx + 25, ry + 210), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (225, 225, 225), 1, cv2.LINE_AA)
        if l3:
            cv2.putText(canvas, l3, (rx + 25, ry + 245), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (225, 225, 225), 1, cv2.LINE_AA)

        # Veliko dugme na dnu kartice
        btn_y = ry + rh - 68
        if is_active:
            btn_bg = (30, 150, 60)
            btn_lbl = "▶ TRENUTNO AKTIVNA (KLIKNI ZA STOP)"
            lbl_col = (255, 255, 255)
        elif is_hover:
            btn_bg = (0, 215, 255)
            btn_lbl = f"POKRENI IGRU [{g['num']}] ▶"
            lbl_col = (20, 20, 20)
        else:
            btn_bg = (65, 45, 55)
            btn_lbl = f"POKRENI IGRU [{g['num']}] ▶"
            lbl_col = (200, 200, 200)

        cv2.rectangle(canvas, (rx + 25, btn_y), (rx + rw - 25, btn_y + 48), btn_bg, -1)
        cv2.putText(canvas, btn_lbl, (rx + 45, btn_y + 32),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, lbl_col, 2, cv2.LINE_AA)

    # 4. Donja traka sa prečicama
    footer = "Prečice: [1-6] Izbor igre  |  [s] / [Space] Zaustavi aktivnu  |  [f] Fullscreen  |  [q] Izlaz iz menija"
    cv2.putText(canvas, footer, (CANVAS_W // 2 - 580, 1035),
                cv2.FONT_HERSHEY_SIMPLEX, 0.68, (190, 190, 190), 1, cv2.LINE_AA)

    cv2.imshow(WINDOW_NAME, canvas)

    key = cv2.waitKey(25) & 0xFF

    if clicked_idx is not None:
        idx = clicked_idx
        clicked_idx = None
        pokreni_igru(idx)
        continue

    if key == ord('q') or key == 27:
        zaustavi_trenutnu_igru()
        break
    elif ord('1') <= key <= ord('6'):
        idx = key - ord('1')
        pokreni_igru(idx)
    elif key == ord('s') or key == ord(' '):
        zaustavi_trenutnu_igru()
    elif key == ord('f'):
        is_fullscreen = not is_fullscreen
        if is_fullscreen:
            cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(WINDOW_NAME, CANVAS_W, CANVAS_H)

zaustavi_trenutnu_igru()
cv2.destroyAllWindows()
