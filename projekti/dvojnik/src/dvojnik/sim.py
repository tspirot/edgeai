"""Синтетички предмет и његове силуете — цео ланац без камере и стола.

Тело је задато формулом (кугла, коцка, ваљак, шоља), а силуета се добија тако
што се густо узоркује његова запремина и пројектује кроз исту ону камеру коју
користи и стварно снимање. Пошто се тачна димензија тела зна унапред,
реконструкција се може **измерити**, а не само погледати — на томе стоје
тестови.
"""

from __future__ import annotations

import numpy as np

from dvojnik.geometrija import Kamera, resetka, rotacija_z
from dvojnik.siluete import popuni_rupe, zatvori


# --- тела (враћају булову маску за тачке (N, 3) у mm) ---------------------

def kugla(precnik: float, visina_centra: float = None):
    r = float(precnik) / 2.0
    zc = r if visina_centra is None else float(visina_centra)

    def telo(P):
        P = np.asarray(P, dtype=np.float64)
        d = P - np.array([0.0, 0.0, zc])
        return (d * d).sum(axis=-1) <= r * r

    return telo


def kocka(stranica: float):
    a = float(stranica) / 2.0

    def telo(P):
        P = np.asarray(P, dtype=np.float64)
        return (
            (np.abs(P[..., 0]) <= a)
            & (np.abs(P[..., 1]) <= a)
            & (P[..., 2] >= 0) & (P[..., 2] <= 2 * a)
        )

    return telo


def valjak(precnik: float, visina: float):
    r = float(precnik) / 2.0
    h = float(visina)

    def telo(P):
        P = np.asarray(P, dtype=np.float64)
        return (
            (P[..., 0] ** 2 + P[..., 1] ** 2 <= r * r)
            & (P[..., 2] >= 0) & (P[..., 2] <= h)
        )

    return telo


def solja(precnik: float, visina: float, debljina: float):
    """Ваљак са удубљењем одозго — предмет на ком метод показује своју границу."""
    r = float(precnik) / 2.0
    h, d = float(visina), float(debljina)
    if d <= 0 or d >= r:
        raise ValueError("Дебљина зида мора бити између нуле и полупречника")
    ru = r - d

    def telo(P):
        P = np.asarray(P, dtype=np.float64)
        rr = P[..., 0] ** 2 + P[..., 1] ** 2
        pun = (rr <= r * r) & (P[..., 2] >= 0) & (P[..., 2] <= h)
        supljina = (rr <= ru * ru) & (P[..., 2] > d) & (P[..., 2] <= h)
        return pun & ~supljina

    return telo


# --- силуете ---------------------------------------------------------------

def uglovi_punog_kruga(broj: int) -> list:
    if broj < 1:
        raise ValueError("Треба бар један угао")
    return [360.0 * i / broj for i in range(int(broj))]


def zapremina(telo, granice, podela) -> np.ndarray:
    centri, _ = resetka(granice, podela)
    return telo(centri)


def siluete(telo, kamera: Kamera, uglovi, granice, gustina: int = 130) -> list:
    """Пројектуј густо узорковано тело у сваки кадар и добиј маске.

    Узорци су тачке, па пројекција оставља ситне рупице између њих; зато иде
    затварање и попуњавање. Ако је `gustina` премала у односу на резолуцију
    слике, маска испадне решеткаста и реконструкција буде мања од стварне.
    """
    centri, _ = resetka(granice, (gustina, gustina, gustina))
    tacke = centri[telo(centri)]
    if tacke.size == 0:
        raise ValueError("Тело је празно у задатим границама — провери димензије")

    izlaz = []
    for ugao in uglovi:
        u, v, dubina = kamera.projektuj(tacke @ rotacija_z(ugao).T)
        vidi_se = kamera.u_kadru(u, v, dubina)
        m = np.zeros((kamera.visina, kamera.sirina), dtype=bool)
        if vidi_se.any():
            m[v[vidi_se].astype(np.int32), u[vidi_se].astype(np.int32)] = True
        izlaz.append(popuni_rupe(zatvori(m, 2)))
    return izlaz


def kadrovi(telo, kamera: Kamera, uglovi, granice, gustina: int = 130,
            pozadina_siva: int = 200, predmet_sivi: int = 60) -> tuple:
    """Исте силуете, али као „снимци“ — за пробу целог ланца укључујући праг.

    Враћа (листа кадрова, празна позадина), све као (H, W, 3) uint8.
    """
    prazna = np.full((kamera.visina, kamera.sirina, 3), pozadina_siva, dtype=np.uint8)
    out = []
    for m in siluete(telo, kamera, uglovi, granice, gustina):
        kadar = prazna.copy()
        kadar[m] = predmet_sivi
        out.append(kadar)
    return out, prazna
