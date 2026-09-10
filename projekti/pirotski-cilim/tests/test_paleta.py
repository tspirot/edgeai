import numpy as np
import pytest

from cilim import paleta as pal


def test_kvantizacija_pogadja_tacnu_boju():
    ciljana = pal.PALETA[0]
    slika = np.full((4, 4, 3), ciljana.rgb, dtype=np.uint8)
    idx = pal.kvantizuj(slika)
    assert (idx == 0).all()


def test_kvantizacija_bira_najblizu_a_ne_prvu():
    bela = pal.indeks_boje("bela")
    slika = np.full((2, 2, 3), (250, 245, 235), dtype=np.uint8)
    assert (pal.kvantizuj(slika) == bela).all()


def test_povratak_u_sliku_je_obrnuto_od_kvantizacije():
    slika = np.array([[b.rgb for b in pal.PALETA]], dtype=np.uint8)
    assert (pal.u_sliku(pal.kvantizuj(slika)) == slika).all()


def test_kvantizacija_odbija_pogresan_oblik():
    with pytest.raises(ValueError):
        pal.kvantizuj(np.zeros((4, 4), dtype=np.uint8))


def test_indeks_nepoznate_boje_puca():
    with pytest.raises(KeyError):
        pal.indeks_boje("nepostojeca")


def test_udeo_se_sabira_u_jedan():
    idx = np.array([[0, 1], [1, 2]])
    u = pal.udeo(idx)
    assert pytest.approx(sum(u.values()), abs=1e-9) == 1.0
    assert u[pal.PALETA[1].id] == 0.5


def test_crvena_preovladjuje_prepoznaje_crveni_cilim():
    rujna = pal.indeks_boje("rujna")
    crna = pal.indeks_boje("crna")
    idx = np.full((10, 10), rujna)
    idx[:3] = crna
    assert pal.crvena_preovladjuje(idx)


def test_crvena_ne_preovladjuje_na_crnom():
    idx = np.full((10, 10), pal.indeks_boje("crna"))
    assert not pal.crvena_preovladjuje(idx)
