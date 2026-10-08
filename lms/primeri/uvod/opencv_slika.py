#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
          UVOD 4 — OPENCV NA JEDNOJ SLICI (bez kamere; radi i na laptopu)
================================================================================
Ucitava logo.png, crta po njemu, pretvara boje (BGR -> sivo, HSV) i prikazuje.
Pokretanje:  python opencv_slika.py             (prozor; zatvori sa [q] ili [ESC])
             python opencv_slika.py --snimi      (upise rezultat u izlaz.png, bez prozora)
================================================================================
"""

import os
# Prikaz na lokalni HDMI ekran kada se pokrece preko SSH (kao i ostali primeri)
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

import sys
from pathlib import Path
import cv2
import numpy as np

putanja = Path(__file__).resolve().parent.parent / "logo.png"
# cv2.imread ne otvara putanje sa slovima kao c, s, z (Windows); np.fromfile + imdecode radi svuda
bajtovi = np.fromfile(str(putanja), dtype=np.uint8)
slika = cv2.imdecode(bajtovi, cv2.IMREAD_COLOR)   # BGR, oblik (visina, sirina, 3)
if slika is None:
    print("[GRESKA] Ne mogu da otvorim logo.png")
    sys.exit(1)

# Uvecamo da se lakse vidi: 167x167 -> 501x501
slika = cv2.resize(slika, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST)
h, w = slika.shape[:2]
print("Oblik slike:", slika.shape)

# Crtanje (boje su u BGR redosledu: (plava, zelena, crvena))
cv2.rectangle(slika, (10, 10), (w - 10, h - 10), (0, 255, 255), 2)
cv2.line(slika, (10, 10), (w - 10, h - 10), (0, 0, 255), 2)
cv2.circle(slika, (w // 2, h // 2), 60, (0, 255, 0), 3)
cv2.putText(slika, "OpenCV", (20, h - 24), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

# Pretvaranje boja
siva = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)      # jedan kanal -> oblik (h, w)
hsv = cv2.cvtColor(slika, cv2.COLOR_BGR2HSV)        # nijansa, zasicenost, vrednost
print("Siva slika:", siva.shape, "| HSV:", hsv.shape)

# Poredimo sve tri jedna pored druge
siva_3k = cv2.cvtColor(siva, cv2.COLOR_GRAY2BGR)
spojeno = np.hstack((slika, siva_3k, hsv))

if "--snimi" in sys.argv:
    cv2.imencode(".png", spojeno)[1].tofile("izlaz.png")
    print("Upisano u izlaz.png")
    sys.exit(0)

cv2.imshow("Original | sivo | HSV (prikazano kao BGR)", spojeno)
while True:
    kljuc = cv2.waitKey(30) & 0xFF
    if kljuc in (ord("q"), 27):
        break
cv2.destroyAllWindows()
