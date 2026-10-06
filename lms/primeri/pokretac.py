#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
          RASPBERRY PI 5 — POKRETAČ SVIH PROJEKATA (JEDAN KLIK)
================================================================================
Grafički (GUI) i konzolni (CLI) centar za brzo pokretanje svih AI projekata.
Automatski oslobađa kameru, postavlja radni direktorijum i prati rad procesa.
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path

# Osiguravanje promenljivih za grafički prikaz na TV/ekranu
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

BASE_DIR = Path("/home/pi/primeri").resolve()
PYTHON_ENV = str(BASE_DIR / "env" / "bin" / "python")

# Provera postojanja virtuelnog okruženja, fallback na sistemski python3
if not os.path.exists(PYTHON_ENV):
    PYTHON_ENV = sys.executable

# Definicija svih projekata
PROJECTS = [
    {
        "id": "klon",
        "num": "1",
        "name": "KLON (Matrix, Avatar & Tesla)",
        "badge": "MOCAP & AI LICE",
        "color": "#8b5cf6",
        "icon": "🤖",
        "dir": str(BASE_DIR / "klon"),
        "cmd": [PYTHON_ENV, "klon.py"],
        "desc": "Split-screen mocap celog tela i lica: Matrix digitalni klon (podrazumevano), Cyber Avatar i foto-klon Nikole Tesle.",
        "controls": "[s] Prebaci model (Matrix/Avatar/Tesla)  |  [q] Izlaz"
    },
    {
        "id": "vozibezbedno",
        "num": "2",
        "name": "VOZIBEZBEDNO (Nadzor Vozača)",
        "badge": "BEZBEDNOST & DMS",
        "color": "#ef4444",
        "icon": "🚗",
        "dir": str(BASE_DIR / "vozibezbedno"),
        "cmd": [PYTHON_ENV, "vozibezbedno.py"],
        "desc": "Detekcija umora, treptaja oka (EAR), zevanja (MAR) i nagiba glave uz telemetriju na TV-u.",
        "controls": "[n] NoIR filter  |  [q] Izlaz"
    },
    {
        "id": "mesec",
        "num": "3",
        "name": "MESEC (Mesečeva Kugla)",
        "badge": "3D SVETLO & DLAN",
        "color": "#f59e0b",
        "icon": "🌕",
        "dir": str(BASE_DIR / "mesec"),
        "cmd": [PYTHON_ENV, "mesec.py"],
        "desc": "Mesečeva kugla lebdi u šaci, prati dlan i stvara realistično radijalno osvetljenje u sobi.",
        "controls": "[m] Teme boja  |  [+/-] Veličina  |  [q] Izlaz"
    },
    {
        "id": "pucketanje",
        "num": "4",
        "name": "PUCKETANJE (Nevidljivost)",
        "badge": "SNAP NEVIDLJIVOST",
        "color": "#06b6d4",
        "icon": "💥",
        "dir": str(BASE_DIR / "pucketanje"),
        "cmd": [PYTHON_ENV, "pucketanje.py"],
        "desc": "Pucketanjem prstima (palac + srednji prst) ili pritiskom na Space postajete nevidljivi na ekranu.",
        "controls": "[Pucketanje] / [Space] Nevidljivost  |  [r] Nova pozadina  |  [q] Izlaz"
    },
    {
        "id": "proba",
        "num": "5",
        "name": "PROBA (Ruke & Hologram)",
        "badge": "GESTOVI & HUD",
        "color": "#10b981",
        "icon": "🖐️",
        "dir": str(BASE_DIR / "proba"),
        "cmd": [PYTHON_ENV, "proba.py"],
        "desc": "Brojanje prstiju obe šake i interaktivni hologramski pravougaonik između palca i kažiprsta.",
        "controls": "[n] NoIR filter  |  [+/-] Zasićenost  |  [q] Izlaz"
    },
    {
        "id": "igrice",
        "num": "6",
        "name": "DEČIJE IGRICE (Kutak za Predškolce)",
        "badge": "6 IGRICA ZA DECU",
        "color": "#ec4899",
        "icon": "🎈",
        "dir": str(BASE_DIR / "igrice"),
        "cmd": [PYTHON_ENV, "pokretac_igrice.py"],
        "desc": "Čarobni mehurići, Nahrani životinje, Čarobni štapić, Korpica, Smešno ogledalo i Spajanje sličica!",
        "controls": "[1-6] Izbor igrice  |  [Miš] Klik na karticu  |  [q] Izlaz"
    },
    {
        "id": "vremenskamasina",
        "num": "7",
        "name": "VREMENSKA MAŠINA",
        "badge": "TIME TRAVEL SNAP",
        "color": "#ec4899",
        "icon": "⏳",
        "dir": str(BASE_DIR / "vremenskamasina"),
        "cmd": [PYTHON_ENV, "time_travel_snap.py"],
        "desc": "Pucketanjem prstima putujete kroz epohe: 15. vek, barok, 1920-te i cyberpunk budućnost.",
        "controls": "[Pucketanje] / [Space] Promena epohe  |  [q] Izlaz"
    },
    {
        "id": "kvo-te",
        "num": "8",
        "name": "KVO-TE (Pirotski AI Mudrac)",
        "badge": "TORLAČKI AI & GLAS",
        "color": "#d97706",
        "icon": "🧣",
        "dir": "/home/pi/projekti/kvo-te" if os.path.exists("/home/pi/projekti/kvo-te") else str(BASE_DIR / "kvo-te"),
        "cmd": [PYTHON_ENV, "kvo_te.py"],
        "desc": "Pirotski AI mudrac koji savetuje, priča viceve i govori naglas na izvornom pirotskom govoru.",
        "controls": "[ENTER] Upis pitanja  |  [1-6] Brze teme  |  [m] Mute  |  [q] Izlaz"
    },
    {
        "id": "titlovi-uzivo",
        "num": "9",
        "name": "TITLOVI-UŽIVO (Govor u Tekst)",
        "badge": "WHISPER AI TITLOVI",
        "color": "#14b8a6",
        "icon": "🎙️",
        "dir": str(BASE_DIR / "titlovi-uzivo"),
        "cmd": ["/home/pi/primeri/titlovi-uzivo/.venv/bin/titlovi", "run"] if os.path.exists("/home/pi/primeri/titlovi-uzivo/.venv/bin/titlovi") else ["titlovi", "run"],
        "desc": "100% lokalno AI prepoznavanje govora na srpskom jeziku u realnom vremenu bez interneta.",
        "controls": "[f] Ceo ekran  |  [q] / [ESC] Izlaz"
    },
    {
        "id": "lidar",
        "num": "10",
        "name": "RPLIDAR C1 (360° Radar & Skener)",
        "badge": "LASERSKI DTOF RADAR",
        "color": "#06b6d4",
        "icon": "📡",
        "dir": str(BASE_DIR / "lidar"),
        "cmd": [PYTHON_ENV, "lidar.py"],
        "desc": "360-stepeni laserski radar za RPLIDAR C1 sa detekcijom prepreka u realnom vremenu, zumom i više tema.",
        "controls": "[s] Simulacija  |  [+/-] Zoom  |  [c] Teme  |  [q] Izlaz"
    },
    {
        "id": "lidar-alarm",
        "num": "11",
        "name": "LIDAR ALARM (Sigurnosna Barijera 1m)",
        "badge": "PERIMETAR & ALARM",
        "color": "#ef4444",
        "icon": "🚨",
        "dir": str(BASE_DIR / "lidar"),
        "cmd": [PYTHON_ENV, "lidar_alarm_barijera.py"],
        "desc": "Laserski perimetar na 1m sa pametnim filterima (ignoriše male objekte i pomeraje) i alarmom za novog uljeza.",
        "controls": "[k] Kalibracija sobe  |  [+] / [-] Domet  |  [b] Oblik  |  [m] Mute  |  [q] Izlaz"
    },
    {
        "id": "hemija",
        "num": "12",
        "name": "AR HEMIJA (Cepanje i Spajanje Atoma)",
        "badge": "AR ATOMI & MOLEKULI",
        "color": "#38bdf8",
        "icon": "🧪",
        "dir": str(BASE_DIR / "hemija"),
        "cmd": [PYTHON_ENV, "hemija.py"],
        "desc": "Proširena stvarnost: biranje elemenata iz Periodnog sistema na srpskom, cepanje veza rukama i sinteza molekula (H2O, CO2, NaCl, CH4, NH3, HCl).",
        "controls": "[Pinch 2 ruke] Cepanje veze  |  [Prinos] Spajanje atoma  |  [1-6] Eksperimenti  |  [p] Periodni sistem  |  [q] Izlaz"
    }
]

# Globalna referenca na pokrenuti podproces
current_process = None
active_project_id = None


def ocitaj_temperaturu():
    """Vraća temperaturu RPi procesora u °C."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read().strip()) / 1000.0
            return f"{temp:.1f}°C"
    except Exception:
        return "N/A"


def zaustavi_trenutni_proces():
    """Zaustavlja trenutno pokrenuti projekat i oslobađa kameru."""
    global current_process, active_project_id
    if current_process is not None:
        try:
            print(f"[POKRETAČ] Zaustavljam proces PID: {current_process.pid}...")
            # Šaljemo SIGTERM, pa ako ne reaguje SIGKILL
            current_process.terminate()
            try:
                current_process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                current_process.kill()
        except Exception as e:
            print(f"[POKRETAČ] Greška pri zaustavljanju: {e}")
        current_process = None
        active_project_id = None

    # Dodatno osiguravamo da nema zalutalih procesa koji drže kameru
    try:
        subprocess.run(
            ["pkill", "-f", "(klon|vozibezbedno|mesec|pucketanje|proba|sortiranje|time_travel_snap)\\.py"],
            capture_output=True
        )
    except Exception:
        pass


def pokreni_projekat(proj_id, on_status_change=None):
    """Pokreće izabrani projekat po ID-u."""
    global current_process, active_project_id

    # 1. Prvo ugasi bilo šta što je prethodno radilo
    zaustavi_trenutni_proces()

    proj = next((p for p in PROJECTS if p["id"] == proj_id), None)
    if not proj:
        print(f"[GRESKA] Projekat '{proj_id}' nije pronađen!")
        return False

    project_dir = proj["dir"]
    if not os.path.exists(project_dir):
        print(f"[GRESKA] Direktorijum ne postoji: {project_dir}")
        return False

    print("=" * 65)
    print(f"🚀 POKREĆEM: {proj['name']}")
    print(f"📂 Direktorijum: {project_dir}")
    print(f"⚙️ Komanda: {' '.join(proj['cmd'])}")
    print(f"🎮 Kontrole: {proj['controls']}")
    print("=" * 65)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["DISPLAY"] = os.environ.get("DISPLAY", ":0")
    env["WAYLAND_DISPLAY"] = os.environ.get("WAYLAND_DISPLAY", "wayland-0")

    try:
        current_process = subprocess.Popen(
            proj["cmd"],
            cwd=project_dir,
            env=env
        )
        active_project_id = proj["id"]

        if on_status_change:
            on_status_change(proj["id"], "running")

        # Pozadinska nit koja prati kada se proces završi (npr. korisnik stisne 'q')
        def monitor_process():
            global current_process, active_project_id
            proc = current_process
            if proc:
                proc.wait()
                if current_process == proc:
                    current_process = None
                    active_project_id = None
                    print(f"\n[INFO] Projekat '{proj['name']}' je završen.")
                    if on_status_change:
                        on_status_change(proj["id"], "stopped")

        threading.Thread(target=monitor_process, daemon=True).start()
        return True

    except Exception as e:
        print(f"[GRESKA] Nije uspelo pokretanje: {e}")
        active_project_id = None
        current_process = None
        if on_status_change:
            on_status_change(proj["id"], "error")
        return False


# ==============================================================================
#                      GRAFIČKI INTERFEJS (TKINTER GUI)
# ==============================================================================
def pokreni_gui():
    import tkinter as tk
    from tkinter import ttk, messagebox

    root = tk.Tk()
    root.title("Raspberry Pi 5 — AI Projekti (Pokretač)")
    root.geometry("1120x760")
    root.minsize(880, 600)

    # Tamna obsidian tema
    BG_DARK = "#0b0f19"
    BG_CARD = "#141c2b"
    BG_CARD_HOVER = "#1c273c"
    BG_ACTIVE = "#1e293b"
    BORDER_COL = "#27354a"
    TEXT_MAIN = "#f8fafc"
    TEXT_MUTED = "#94a3b8"
    ACCENT_GREEN = "#10b981"
    ACCENT_RED = "#ef4444"

    root.configure(bg=BG_DARK)

    # Mapiranje tastera projekata za ažuriranje izgleda
    project_cards = {}

    def update_card_status(p_id, status):
        root.after(0, lambda: _do_update_card_status(p_id, status))

    def _do_update_card_status(p_id, status):
        lbl_status_bar.config(
            text=f"Aktivno: {active_project_id.upper() if active_project_id else 'Nijedan projekat nije pokrenut'}"
        )
        for pid, widgets in project_cards.items():
            btn = widgets["btn_launch"]
            badge = widgets["lbl_status"]
            card_frame = widgets["frame"]

            if pid == active_project_id and status == "running":
                btn.config(text="⏹ ZAUSTAVI", bg=ACCENT_RED, activebackground="#dc2626")
                badge.config(text="● U RADU", fg=ACCENT_GREEN)
                card_frame.config(highlightbackground=ACCENT_GREEN, highlightthickness=2)
            else:
                btn.config(text="▶ POKRENI", bg=widgets["color"], activebackground="#1d4ed8")
                badge.config(text="○ SPREMAN", fg=TEXT_MUTED)
                card_frame.config(highlightbackground=BORDER_COL, highlightthickness=1)

    # ------------------ GORNJA TRAKA (HEADER) ------------------
    header_frame = tk.Frame(root, bg=BG_DARK)
    header_frame.pack(fill="x", padx=24, pady=(16, 10))

    title_box = tk.Frame(header_frame, bg=BG_DARK)
    title_box.pack(side="left")

    lbl_title = tk.Label(
        title_box,
        text="🚀 RASPBERRY PI 5 — AI CENTAR PROJEKATA",
        font=("Helvetica", 18, "bold"),
        fg=TEXT_MAIN,
        bg=BG_DARK
    )
    lbl_title.pack(anchor="w")

    lbl_subtitle = tk.Label(
        title_box,
        text="Izaberi projekat jednim klikom • Kamera i resursi se automatski oslobađaju",
        font=("Helvetica", 10),
        fg=TEXT_MUTED,
        bg=BG_DARK
    )
    lbl_subtitle.pack(anchor="w", pady=(2, 0))

    # Desni kontrolni blok u zaglavlju
    actions_box = tk.Frame(header_frame, bg=BG_DARK)
    actions_box.pack(side="right")

    btn_stop_all = tk.Button(
        actions_box,
        text="⏹ Zaustavi sve",
        font=("Helvetica", 11, "bold"),
        fg="#ffffff",
        bg=ACCENT_RED,
        activebackground="#dc2626",
        relief="flat",
        padx=14,
        pady=6,
        cursor="hand2",
        command=lambda: (zaustavi_trenutni_proces(), _do_update_card_status(None, "stopped"))
    )
    btn_stop_all.pack(side="right", padx=(8, 0))

    def otvori_uputstvo():
        txt_path = BASE_DIR / "pokretanje.txt"
        if os.path.exists(txt_path):
            try:
                subprocess.Popen(["xdg-open", str(txt_path)])
            except Exception:
                # Fallback u novom prozoru
                viewer = tk.Toplevel(root)
                viewer.title("Uputstvo za pokretanje")
                viewer.geometry("800x600")
                txt_widget = tk.Text(viewer, bg="#0f172a", fg="#e2e8f0", font=("Courier", 10))
                txt_widget.pack(fill="both", expand=True)
                with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                    txt_widget.insert("1.0", f.read())

    btn_manual = tk.Button(
        actions_box,
        text="📖 Uputstvo",
        font=("Helvetica", 11),
        fg=TEXT_MAIN,
        bg=BORDER_COL,
        activebackground=BG_CARD_HOVER,
        relief="flat",
        padx=12,
        pady=6,
        cursor="hand2",
        command=otvori_uputstvo
    )
    btn_manual.pack(side="right", padx=6)

    # ------------------ SKROLUJUĆI SADRŽAJ SA KARTICAMA ------------------
    canvas_container = tk.Frame(root, bg=BG_DARK)
    canvas_container.pack(fill="both", expand=True, padx=20, pady=10)

    canvas = tk.Canvas(canvas_container, bg=BG_DARK, highlightthickness=0)
    scrollbar = tk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG_DARK)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def configure_canvas_width(event):
        canvas.itemconfig(canvas_window, width=event.width)

    canvas.bind("<Configure>", configure_canvas_width)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Miš skrolovanje
    def on_mousewheel(event):
        if event.num == 4 or event.delta > 0:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            canvas.yview_scroll(1, "units")

    canvas.bind_all("<MouseWheel>", on_mousewheel)
    canvas.bind_all("<Button-4>", on_mousewheel)
    canvas.bind_all("<Button-5>", on_mousewheel)

    # ------------------ KREIRANJE KARTICA PROJEKATA ------------------
    GRID_COLS = 2
    scrollable_frame.columnconfigure(0, weight=1)
    scrollable_frame.columnconfigure(1, weight=1)

    for idx, proj in enumerate(PROJECTS):
        row = idx // GRID_COLS
        col = idx % GRID_COLS

        card = tk.Frame(
            scrollable_frame,
            bg=BG_CARD,
            highlightbackground=BORDER_COL,
            highlightthickness=1,
            padx=16,
            pady=14
        )
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        # Gornji red kartice (Ikona, Naziv, Oznaka)
        top_row = tk.Frame(card, bg=BG_CARD)
        top_row.pack(fill="x")

        lbl_icon = tk.Label(
            top_row,
            text=proj["icon"],
            font=("Helvetica", 20),
            bg=BG_CARD
        )
        lbl_icon.pack(side="left", padx=(0, 10))

        title_col = tk.Frame(top_row, bg=BG_CARD)
        title_col.pack(side="left", fill="x", expand=True)

        lbl_pname = tk.Label(
            title_col,
            text=proj["name"],
            font=("Helvetica", 12, "bold"),
            fg=TEXT_MAIN,
            bg=BG_CARD
        )
        lbl_pname.pack(anchor="w")

        lbl_badge = tk.Label(
            title_col,
            text=proj["badge"],
            font=("Helvetica", 8, "bold"),
            fg=proj["color"],
            bg=BG_CARD
        )
        lbl_badge.pack(anchor="w")

        lbl_status = tk.Label(
            top_row,
            text="○ SPREMAN",
            font=("Helvetica", 9, "bold"),
            fg=TEXT_MUTED,
            bg=BG_CARD
        )
        lbl_status.pack(side="right")

        # Opis
        lbl_desc = tk.Label(
            card,
            text=proj["desc"],
            font=("Helvetica", 9),
            fg="#cbd5e1",
            bg=BG_CARD,
            wraplength=460,
            justify="left"
        )
        lbl_desc.pack(anchor="w", pady=(10, 8))

        # Kontrole
        ctrl_frame = tk.Frame(card, bg="#0d1522", padx=8, pady=4)
        ctrl_frame.pack(fill="x", pady=(0, 12))

        lbl_ctrl = tk.Label(
            ctrl_frame,
            text=f"Tasteri: {proj['controls']}",
            font=("Helvetica", 8),
            fg="#38bdf8",
            bg="#0d1522",
            anchor="w"
        )
        lbl_ctrl.pack(fill="x")

        # Dugme za pokretanje
        btn_run = tk.Button(
            card,
            text="▶ POKRENI",
            font=("Helvetica", 11, "bold"),
            fg="#ffffff",
            bg=proj["color"],
            activebackground="#2563eb",
            relief="flat",
            pady=7,
            cursor="hand2"
        )
        btn_run.pack(fill="x")

        # Klik handler
        def make_launch_cmd(pid):
            def handler():
                if active_project_id == pid:
                    zaustavi_trenutni_proces()
                    _do_update_card_status(pid, "stopped")
                else:
                    pokreni_projekat(pid, on_status_change=update_card_status)
            return handler

        btn_run.config(command=make_launch_cmd(proj["id"]))

        # Čuvanje referenci
        project_cards[proj["id"]] = {
            "frame": card,
            "btn_launch": btn_run,
            "lbl_status": lbl_status,
            "color": proj["color"]
        }

    # ------------------ STATUSNA TRAKA NA DNU ------------------
    footer_bar = tk.Frame(root, bg="#090d16", padx=20, pady=8)
    footer_bar.pack(fill="x", side="bottom")

    lbl_status_bar = tk.Label(
        footer_bar,
        text="Aktivno: Nijedan projekat nije pokrenut",
        font=("Helvetica", 10),
        fg=TEXT_MUTED,
        bg="#090d16"
    )
    lbl_status_bar.pack(side="left")

    lbl_sys_info = tk.Label(
        footer_bar,
        text="RPi 5 CPU: --°C",
        font=("Helvetica", 10),
        fg=ACCENT_GREEN,
        bg="#090d16"
    )
    lbl_sys_info.pack(side="right")

    def osvezi_info():
        lbl_sys_info.config(text=f"RPi 5 CPU: {ocitaj_temperaturu()}")
        root.after(3000, osvezi_info)

    osvezi_info()

    # Prečice na tastaturi (F11 = Fullscreen, Esc = Izlaz)
    is_fullscreen = False

    def toggle_fullscreen(event=None):
        nonlocal is_fullscreen
        is_fullscreen = not is_fullscreen
        root.attributes("-fullscreen", is_fullscreen)

    root.bind("<F11>", toggle_fullscreen)

    def on_closing():
        zaustavi_trenutni_proces()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


# ==============================================================================
#                      INTERAKTIVNI KONZOLNI MENI (CLI)
# ==============================================================================
def pokreni_cli():
    """Konzolni meni kada se pokreće preko SSH ili bez grafičkog okruženja."""
    while True:
        os.system("clear")
        print("=" * 70)
        print("     🚀  RASPBERRY PI 5 — POKRETAČ SVIH PROJEKATA  (CLI)     ")
        print("=" * 70)
        print(f"Temperatura procesora: {ocitaj_temperaturu()}")
        print("-" * 70)

        for p in PROJECTS:
            status = " [AKTIVAN]" if p["id"] == active_project_id else ""
            print(f"  [{p['num']}]  {p['icon']}  {p['name']}{status}")
            print(f"       -> {p['desc']}")
            print(f"       Kontrole: {p['controls']}")
            print()

        print("-" * 70)
        print("  [s]  ⏹  Zaustavi trenutno pokrenuti projekat")
        print("  [u]  📖  Prikaži uputstvo (pokretanje.txt)")
        print("  [q]  ❌  Izlaz iz pokretača")
        print("=" * 70)

        izbor = input("Unesite broj projekta ili opciju: ").strip().lower()

        if izbor == "q":
            zaustavi_trenutni_proces()
            print("Doviđenja!")
            break
        elif izbor == "s":
            zaustavi_trenutni_proces()
            input("\nProces je zaustavljen. Pritisni ENTER za nastavak...")
        elif izbor == "u":
            txt_path = BASE_DIR / "pokretanje.txt"
            if os.path.exists(txt_path):
                os.system(f"less '{txt_path}'")
        else:
            proj = next((p for p in PROJECTS if p["num"] == izbor), None)
            if proj:
                print(f"\nPokrećem {proj['name']}...")
                pokreni_projekat(proj["id"])
                input("\nProjekat je pokrenut u pozadini na TV/ekranu. Pritisni ENTER za meni...")
            else:
                input("\nNepoznata opcija! Pritisni ENTER...")


# ==============================================================================
#                              GLAVNA TAČKA ULASA
# ==============================================================================
if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda sig, frame: (zaustavi_trenutni_proces(), sys.exit(0)))

    # Ako je zatražen --cli ili nema grafičkog prikaza, koristi CLI
    has_display = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    force_cli = "--cli" in sys.argv or "-c" in sys.argv

    if force_cli or not has_display:
        pokreni_cli()
    else:
        try:
            pokreni_gui()
        except Exception as err:
            print(f"[UPOZORENJE] Nije moguće otvoriti GUI ({err}). Prelazim na CLI meni...")
            pokreni_cli()
