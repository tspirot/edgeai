import numpy as np
import pytest

from dvojnik import siluete as sil


def _kvadrat(n=40, a=10, b=30, vrednost=60, pozadina=200):
    slika = np.full((n, n, 3), pozadina, dtype=np.uint8)
    slika[a:b, a:b] = vrednost
    return slika, np.full((n, n, 3), pozadina, dtype=np.uint8)


def test_silueta_nalazi_predmet():
    slika, pozadina = _kvadrat()
    m = sil.silueta(slika, pozadina)
    assert m[20, 20]
    assert not m[2, 2]


def test_silueta_ima_pravu_povrsinu():
    slika, pozadina = _kvadrat(a=10, b=30)
    m = sil.silueta(slika, pozadina, zatvaranje=0)
    assert m.sum() == 20 * 20


def test_previsok_prag_ne_vidi_nista():
    slika, pozadina = _kvadrat(vrednost=190, pozadina=200)
    assert not sil.silueta(slika, pozadina, prag=50, samo_najveca=False).any()


def test_nizak_prag_vidi_slabu_razliku():
    slika, pozadina = _kvadrat(vrednost=190, pozadina=200)
    assert sil.silueta(slika, pozadina, prag=5, zatvaranje=0).sum() == 400


def test_razlicite_velicine_pucaju():
    slika, _ = _kvadrat(n=40)
    with pytest.raises(ValueError, match="нису исте величине"):
        sil.silueta(slika, np.zeros((30, 30, 3), dtype=np.uint8))


def test_negativan_prag_puca():
    slika, pozadina = _kvadrat()
    with pytest.raises(ValueError):
        sil.silueta(slika, pozadina, prag=-1)


# --- морфологија ----------------------------------------------------------

def test_dilatacija_siri_erozija_skuplja():
    m = np.zeros((9, 9), bool)
    m[4, 4] = True
    assert sil.dilatiraj(m).sum() == 5          # тачка плус четири суседа
    assert not sil.erodiraj(sil.dilatiraj(m)).sum() == 0  # врати се на тачку
    assert sil.erodiraj(sil.dilatiraj(m)).sum() == 1


def test_zatvaranje_lepi_sitan_prekid():
    m = np.zeros((9, 12), bool)
    m[3:6, 2:5] = True
    m[3:6, 6:9] = True                           # прекид од једног пиксела на 5
    assert sil.zatvori(m, 1)[4, 5]


def test_zatvaranje_ne_spasava_liniju_debelu_jedan_piksel():
    """Крстасти елемент не може да премости прекид у линији од једног пиксела.

    Ерозија тражи сва четири суседа, а изнад и испод танке линије нема ничега.
    Зато силуета мора бити мало дебља од шума — не рачунај да ће затварање
    спасти обрис дебео један пиксел.
    """
    m = np.zeros((9, 12), bool)
    m[4, 2:5] = True
    m[4, 6:9] = True
    assert not sil.zatvori(m, 1)[4, 5]


def test_popunjavanje_rupa_zatvara_supljinu():
    m = np.zeros((11, 11), bool)
    m[2:9, 2:9] = True
    m[5, 5] = False                              # рупа унутар предмета
    assert sil.popuni_rupe(m)[5, 5]


def test_popunjavanje_ne_dira_pozadinu():
    m = np.zeros((11, 11), bool)
    m[2:9, 2:9] = True
    assert not sil.popuni_rupe(m)[0, 0]


def test_popunjavanje_odbija_trodimenzionalno():
    with pytest.raises(ValueError):
        sil.popuni_rupe(np.zeros((4, 4, 4), bool))


def test_najveca_celina_odbacuje_mrvu():
    m = np.zeros((12, 12), bool)
    m[2:8, 2:8] = True                           # предмет
    m[10, 10] = True                             # мрва поред њега
    izlaz = sil.najveca_celina(m)
    assert izlaz.sum() == 36
    assert not izlaz[10, 10]


# --- упозорења ------------------------------------------------------------

def test_dodirivanje_ivice_se_primeti():
    m = np.zeros((10, 10), bool)
    m[0, 5] = True
    assert sil.dodiruje_ivicu(m)


def test_predmet_u_sredini_ne_dodiruje_ivicu():
    m = np.zeros((10, 10), bool)
    m[4:6, 4:6] = True
    assert not sil.dodiruje_ivicu(m)


def test_udeo_kadra():
    m = np.zeros((10, 10), bool)
    m[:5] = True
    assert sil.udeo_kadra(m) == pytest.approx(0.5)
