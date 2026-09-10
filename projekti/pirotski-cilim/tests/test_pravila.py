import numpy as np
import pytest

from cilim import paleta as pal
from cilim import pravila as prv
from cilim.config import PravilaConfig


# --- појасеви -------------------------------------------------------------

def test_pojasevi_idu_spolja_ka_unutra():
    mapa = prv.pojasevi(100, 100)
    assert mapa[0, 50] == prv.SPOLJASNJI_CENAR
    assert mapa[50, 50] == prv.POLJE
    # између њих се мора појавити и бордура и унутрашњи ћенар
    presek = list(mapa[:50, 50])
    assert prv.BORDURA in presek
    assert prv.UNUTRASNJI_CENAR in presek


def test_pojasevi_su_simetricni():
    mapa = prv.pojasevi(80, 120)
    assert (mapa == np.flip(mapa, axis=0)).all()
    assert (mapa == np.flip(mapa, axis=1)).all()


def test_pojasevi_koji_pojedu_polje_pucaju():
    cfg = PravilaConfig(spoljasnji_cenar=0.4, bordura=0.4, unutrasnji_cenar=0.3)
    with pytest.raises(ValueError, match="не остаје поље"):
        prv.pojasevi(50, 50, cfg)


def test_negativna_debljina_puca():
    with pytest.raises(ValueError):
        prv.pojasevi(50, 50, PravilaConfig(bordura=-0.1))


# --- огледање -------------------------------------------------------------

def test_ogledanje_daje_simetricnu_sliku():
    a = np.arange(24).reshape(4, 6)
    o = prv.ogledaj(a)
    assert (o == np.flip(o, axis=1)).all()
    assert (o == np.flip(o, axis=0)).all()


def test_ogledanje_cuva_dimenzije_i_za_neparne():
    for oblik in [(5, 7), (4, 6), (5, 6), (4, 7)]:
        assert prv.ogledaj(np.zeros(oblik)).shape == oblik


def test_ogledanje_cuva_levu_polovinu():
    a = np.arange(20).reshape(4, 5)
    o = prv.ogledaj(a, vodoravno=False)
    assert (o[:, :3] == a[:, :3]).all()


def test_ogledanje_odbija_jednodimenzionalno():
    with pytest.raises(ValueError):
        prv.ogledaj(np.arange(5))


# --- потези ---------------------------------------------------------------

def test_duzine_poteza_broji_uzastopne():
    assert list(prv.duzine_poteza([1, 1, 1, 2, 2, 3])) == [3, 2, 1]


def test_duzine_poteza_prazan_red():
    assert prv.duzine_poteza([]).size == 0


def test_ujednacavanje_uklanja_kratke_poteze():
    red = np.array([[0, 0, 0, 0, 1, 0, 0, 0, 0]])
    out = prv.ujednaci_poteze(red, min_niti=3)
    assert prv.duzine_poteza(out[0]).min() >= 3
    assert (out == 0).all()


def test_ujednacavanje_ne_dira_dovoljno_duge():
    red = np.array([[0, 0, 0, 1, 1, 1]])
    assert (prv.ujednaci_poteze(red, min_niti=3) == red).all()


def test_ujednacavanje_bira_duzeg_suseda():
    # кратак потез (једно поље, боја 2) између дугог 0 и краћег 1
    red = np.array([[0, 0, 0, 0, 0, 2, 1, 1, 1]])
    out = prv.ujednaci_poteze(red, min_niti=2)[0]
    assert out[5] == 0


def test_ujednacavanje_ne_ulazi_u_beskonacnu_petlju():
    rng = np.random.default_rng(0)
    slucajno = rng.integers(0, 4, size=(6, 40))
    out = prv.ujednaci_poteze(slucajno, min_niti=4)
    for red in out:
        assert prv.duzine_poteza(red).min() >= 4 or len(prv.duzine_poteza(red)) == 1


def test_ujednacavanje_odbija_jednodimenzionalno():
    with pytest.raises(ValueError):
        prv.ujednaci_poteze(np.zeros(5))


# --- извештај -------------------------------------------------------------

def test_izvestaj_prepoznaje_izvodljivo():
    mreza = np.repeat(np.array([[0, 1, 0, 1]]), 5, axis=0).repeat(5, axis=1)
    iz = prv.proveri(mreza, min_niti=3)
    assert iz.kratkih == 0
    assert iz.izvodljivo()


def test_izvestaj_prepoznaje_neizvodljivo():
    mreza = np.tile(np.array([0, 1]), (4, 8))   # свака ћелија друга боја
    iz = prv.proveri(mreza, min_niti=3)
    assert iz.udeo_kratkih == 1.0
    assert not iz.izvodljivo()


def test_izvestaj_broji_promene_po_redu():
    mreza = np.array([[0, 0, 1, 1, 2, 2]])
    assert prv.proveri(mreza, min_niti=1).promena_po_redu == 2


def test_izvestaj_ima_citljiv_ispis():
    mreza = np.zeros((4, 8), dtype=int)
    assert "изводљиво" in str(prv.proveri(mreza))


def test_provera_odbija_pogresan_oblik():
    with pytest.raises(ValueError):
        prv.proveri(np.zeros(8))


# --- цео пут --------------------------------------------------------------

def test_primeni_daje_simetricno_i_izvodljivo():
    rng = np.random.default_rng(7)
    sum_slika = rng.integers(0, 255, size=(64, 64, 3), dtype=np.uint8)
    idx = prv.primeni(sum_slika, PravilaConfig(min_niti=4))

    assert (idx == np.flip(idx, axis=1)).all(), "симетрија мора преживети поравнање потеза"
    assert (idx == np.flip(idx, axis=0)).all()
    for red in idx:
        duzine = prv.duzine_poteza(red)
        assert duzine.min() >= 4 or duzine.size == 1


def test_primeni_koristi_samo_boje_palete():
    rng = np.random.default_rng(1)
    idx = prv.primeni(rng.integers(0, 255, size=(48, 48, 3), dtype=np.uint8))
    assert idx.min() >= 0 and idx.max() < len(pal.PALETA)
