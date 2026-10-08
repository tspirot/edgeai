#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
              UVOD 4 — OPENCV: PETLJA SA KAMEROM, FLIP I FPS
================================================================================
Najmanja moguca "igrica": uzmi kadar, okreni ga kao ogledalo, nacrtaj FPS i
prikazi. Svaka igrica iz lekcija je ovo plus vise koda unutar petlje.
Pokretanje:  python opencv_kamera.py          Izlaz: [q] ili [ESC]
Radi i sa USB web kamerom na laptopu; na Pi-ju koristi Camera Module 3.
================================================================================
"""

import os
# Prikaz na lokalni HDMI ekran kada se pokrece preko SSH (kao i ostali primeri)
if "DISPLAY" not in os.environ:
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ:
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

import time
import cv2

# Kamera: Picamera2 na Pi-ju, a ako ga nema (laptop) obican VideoCapture
picam2 = None
cap = None
try:
    from picamera2 import Picamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}))
    picam2.start()
    print("[INFO] Picamera2 pokrenuta")
except Exception as e:
    print(f"[INFO] Picamera2 nije dostupna ({e}), koristim VideoCapture(0)")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[GRESKA] Kamera nije pronadjena!")
        raise SystemExit(1)

prethodno = 0.0
while True:
    if picam2 is not None:
        kadar = picam2.capture_array()
    else:
        ok, kadar = cap.read()
        if not ok:
            print("[UPOZORENJE] Nije moguce procitati kadar")
            break

    kadar = cv2.flip(kadar, 1)                 # 1 = okreni levo-desno (ogledalo)

    sada = time.time()
    fps = 1 / (sada - prethodno) if prethodno else 0.0
    prethodno = sada
    cv2.putText(kadar, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("OpenCV kamera", kadar)
    kljuc = cv2.waitKey(1) & 0xFF
    if kljuc in (ord("q"), 27):
        break

if picam2 is not None:
    picam2.stop()
else:
    cap.release()
cv2.destroyAllWindows()
