#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
        UVOD 3 — NUMPY: KADAR KAO NIZ BROJEVA (radi bez kamere i bez ekrana)
================================================================================
Pravimo "kadar" od nule, citamo mu oblik, secemo oblast, pravimo masku i menjamo
piksele pomocu np.where — iste operacije koje koriste igrice i "pucketanje".
Pokretanje:  python numpy_kadar.py
================================================================================
"""

import numpy as np

# 1. Prazan (crn) kadar 640x480 sa tri kanala: oblik je (visina, sirina, kanali)
kadar = np.zeros((480, 640, 3), dtype=np.uint8)
print("Oblik kadra:", kadar.shape)       # (480, 640, 3)
print("Tip brojeva:", kadar.dtype)       # uint8 -> 0..255

# 2. Jedan piksel i jedan kanal
kadar[240, 320] = (255, 255, 255)        # [red, kolona] -> beo piksel u sredini
print("Piksel (240, 320):", kadar[240, 320])
print("Plavi kanal (0), maksimum:", kadar[:, :, 0].max())

# 3. Secenje oblasti: kadar[y1:y2, x1:x2]
kadar[100:200, 300:500] = (0, 165, 255)  # narandzast pravougaonik (BGR redosled)
isecak = kadar[120:180, 320:480]
print("Oblik isecka:", isecak.shape)     # (60, 160, 3)
print("Prosek isecka po kanalima:", isecak.mean(axis=(0, 1)))

# 4. Maska: gde je crveni kanal (indeks 2) veci od 128?
maska = kadar[:, :, 2] > 128
print("Piksela u maski:", int(maska.sum()))

# 5. np.where: tamo gde je maska uzmi sivu boju, inace ostavi kadar
siva = np.full_like(kadar, 90)
maska_3d = np.dstack((maska, maska, maska))   # maska mora imati isti oblik kao kadar
rezultat = np.where(maska_3d, siva, kadar)
print("Prosek rezultata:", round(float(rezultat.mean()), 3))
