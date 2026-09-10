"""Тестови резбарења мере реконструкцију, не гледају је.

Тело је задато формулом, па се тачна димензија зна унапред — реконструкција се
пореди са бројем. Толеранције су у величини воксела: мрежа од 64 поделе преко
160 mm даје воксел од 2.5 mm, па је грешка од пар милиметара очекивана.
"""

import numpy as np
import pytest

from dvojnik import sim
from dvojnik.geometrija import Kamera
from dvojnik.karving import granice_oko_stola, izrezbari

PRECNIK_PROSTORA = 160.0
VISINA_PROSTORA = 200.0
PODELA = (64, 64, 64)


def _kamera():
    return Kamera(sirina=200, visina=200, vfov=44.0,
                  rastojanje=420.0, visina_kamere=180.0, cilj=45.0)


def _granice():
    return granice_oko_stola(PRECNIK_PROSTORA, VISINA_PROSTORA)


def _izrezbari(telo, kadrova=24, podela=PODELA):
    kamera, granice = _kamera(), _granice()
    uglovi = sim.uglovi_punog_kruga(kadrova)
    maske = sim.siluete(telo, kamera, uglovi, granice, gustina=110)
    return izrezbari(maske, uglovi, kamera, granice, podela)


# --- основне провере ------------------------------------------------------

def test_kugla_ima_pravi_gabarit():
    rez = _izrezbari(sim.kugla(60.0))
    dx, dy, dz = rez.gabarit_mm()
    for d in (dx, dy, dz):
        assert d == pytest.approx(60.0, abs=6.0)


def test_kugla_ima_priblizno_pravu_zapreminu():
    rez = _izrezbari(sim.kugla(60.0))
    tacna = 4.0 / 3.0 * np.pi * 30.0 ** 3
    assert rez.zapremina_mm3 == pytest.approx(tacna, rel=0.15)


def test_kocka_ima_pravu_stranicu():
    """Водоравне мере су тесне — сто их обиђе у круг."""
    rez = _izrezbari(sim.kocka(50.0))
    dx, dy, _ = rez.gabarit_mm()
    assert dx == pytest.approx(50.0, abs=6.0)
    assert dy == pytest.approx(50.0, abs=6.0)


def test_visina_se_precenjuje_jer_su_svi_uglovi_sa_iste_visine():
    """Друга граница методе, поред удубљења — и она се мери, не претпоставља.

    Сто обрће предмет око усправне осе, па је водоравни обрис ограничен из свих
    страна. Висина није: сви кадрови су снимљени са ИСТЕ висине камере. Воксел
    изнад предмета, са супротне стране, пројектује се у исти део слике као и
    његов врх, па га ниједна силуета не одсече.

    Отуда правило за поставку: што је камера ближе висини предмета, то мање
    прецењивања. Ко хоће тесну висину, снима два круга са две висине камере.
    """
    rez = _izrezbari(sim.kocka(50.0))
    _, _, dz = rez.gabarit_mm()
    korak_z = rez.korak[2]
    assert dz >= 50.0 - korak_z, "висина никад не сме бити мања од стварне"
    assert dz <= 50.0 + 4 * korak_z, "прецењивање мора остати у пар воксела"


def test_valjak_je_visi_nego_siri():
    rez = _izrezbari(sim.valjak(40.0, 90.0))
    dx, _, dz = rez.gabarit_mm()
    assert dz > dx
    assert dz == pytest.approx(90.0, abs=8.0)


def test_visina_stoji_na_stolu():
    """Предмет лежи на столу, па реконструкција мора почети од z ≈ 0."""
    rez = _izrezbari(sim.kocka(50.0))
    ima = rez.zauzeto.any(axis=(0, 1))
    prvi = int(np.flatnonzero(ima)[0])
    assert prvi * rez.korak[2] < 5.0


# --- граница методе -------------------------------------------------------

def test_solja_ostaje_puna():
    """Ово НИЈЕ грешка него математичка граница визуелног омотача.

    Удубљење одозго се ни из једног бочног угла не види као рупа, па се не може
    ни одрезати. Реконструкција шоље испадне пун ваљак. Ако овај тест икад
    почне да пада, неко је додао процену дубине — и то треба да буде намерно.
    """
    solja = sim.solja(60.0, 72.0, 9.0)
    rez = _izrezbari(solja)

    granice, podela = _granice(), PODELA
    prava = sim.zapremina(solja, granice, podela)
    pun_valjak = sim.zapremina(sim.valjak(60.0, 72.0), granice, podela)

    # реконструкција је знатно већа од стварног тела…
    assert rez.voksela > prava.sum() * 1.25
    # …и практично једнака пуном ваљку
    assert rez.voksela == pytest.approx(int(pun_valjak.sum()), rel=0.1)


def test_omotac_sadrzi_pravo_telo():
    """Визуелни омотач је ГОРЊА граница облика — никад не поједе прави предмет."""
    telo = sim.kocka(50.0)
    rez = _izrezbari(telo)
    prava = sim.zapremina(telo, _granice(), PODELA)
    # допуштамо танак слој грешке од дискретизације на самој ивици
    promasaj = int((prava & ~rez.zauzeto).sum())
    assert promasaj < prava.sum() * 0.05


# --- утицај броја углова --------------------------------------------------

def test_vise_uglova_daje_tesnji_omotac():
    kugla = sim.kugla(60.0)
    malo = _izrezbari(kugla, kadrova=4)
    mnogo = _izrezbari(kugla, kadrova=36)
    assert mnogo.voksela < malo.voksela


def test_tri_ugla_jos_uvek_rade():
    rez = _izrezbari(sim.kugla(60.0), kadrova=3)
    assert rez.voksela > 0


# --- грешке ---------------------------------------------------------------

def test_bez_silueta_puca():
    with pytest.raises(ValueError, match="Нема ниједне силуете"):
        izrezbari([], [], _kamera(), _granice(), PODELA)


def test_nesaglasan_broj_uglova_puca():
    maska = np.ones((200, 200), bool)
    with pytest.raises(ValueError, match="мора исто"):
        izrezbari([maska, maska], [0.0], _kamera(), _granice(), PODELA)


def test_pogresna_velicina_siluete_puca():
    maska = np.ones((50, 50), bool)
    with pytest.raises(ValueError, match="а камера даје"):
        izrezbari([maska], [0.0], _kamera(), _granice(), PODELA)


def test_prazne_siluete_ne_ostave_nista():
    prazna = np.zeros((200, 200), bool)
    rez = izrezbari([prazna] * 3, [0.0, 120.0, 240.0], _kamera(), _granice(), (16, 16, 16))
    assert rez.voksela == 0
    assert rez.gabarit_mm() == (0.0, 0.0, 0.0)


def test_besmislen_radni_prostor_puca():
    with pytest.raises(ValueError):
        granice_oko_stola(-10, 100)


def test_ne_rezi_van_kadra_cuva_nevidjeno():
    """Са `van_kadra_rezi=False` невиђени воксели преживе — зато их буде више."""
    kamera, granice = _kamera(), _granice()
    uglovi = sim.uglovi_punog_kruga(8)
    maske = sim.siluete(sim.kugla(60.0), kamera, uglovi, granice, gustina=110)
    strogo = izrezbari(maske, uglovi, kamera, granice, PODELA, van_kadra_rezi=True)
    blago = izrezbari(maske, uglovi, kamera, granice, PODELA, van_kadra_rezi=False)
    assert blago.voksela >= strogo.voksela
