import numpy as np
import pytest

from dvojnik.geometrija import Kamera, resetka, rotacija_z


def _kamera():
    return Kamera(sirina=320, visina=240, vfov=40.0,
                  rastojanje=300.0, visina_kamere=200.0, cilj=50.0)


# --- ротација -------------------------------------------------------------

def test_rotacija_za_nula_ne_menja_nista():
    assert np.allclose(rotacija_z(0), np.eye(3))


def test_rotacija_za_360_je_identitet():
    assert np.allclose(rotacija_z(360), np.eye(3), atol=1e-12)


def test_rotacija_cuva_visinu_i_rastojanje_od_ose():
    P = np.array([30.0, 40.0, 12.0])
    Q = rotacija_z(73) @ P
    assert Q[2] == pytest.approx(P[2])
    assert np.hypot(*Q[:2]) == pytest.approx(np.hypot(*P[:2]))


def test_rotacija_za_90_salje_x_u_y():
    assert np.allclose(rotacija_z(90) @ np.array([1.0, 0, 0]), [0, 1, 0], atol=1e-12)


# --- камера ---------------------------------------------------------------

def test_ciljna_tacka_pada_u_srediste_slike():
    k = _kamera()
    u, v, d = k.projektuj([[0.0, 0.0, k.cilj]])
    assert u[0] == pytest.approx(k.cx)
    assert v[0] == pytest.approx(k.cy)
    assert d[0] > 0


def test_vise_tacke_padaju_vise_u_slici():
    """y у камери иде НАНИЖЕ — виша тачка мора имати мање v."""
    k = _kamera()
    _, v, _ = k.projektuj([[0.0, 0.0, k.cilj], [0.0, 0.0, k.cilj + 40]])
    assert v[1] < v[0]


def test_ose_kamere_su_ortonormirane():
    R = _kamera().rotacija
    assert np.allclose(R @ R.T, np.eye(3), atol=1e-12)
    assert np.linalg.det(R) == pytest.approx(1.0)


def test_tacka_iza_kamere_ima_negativnu_dubinu():
    k = _kamera()
    _, _, d = k.projektuj([[2 * k.rastojanje, 0.0, k.cilj]])
    assert d[0] < 0


def test_u_kadru_odbacuje_tacke_iza_kamere():
    k = _kamera()
    u, v, d = k.projektuj([[2 * k.rastojanje, 0.0, k.cilj]])
    assert not k.u_kadru(u, v, d)[0]


def test_dalja_tacka_je_bliza_sredistu():
    """Перспектива: исти помак у страну се на већој даљини мање види."""
    k = _kamera()
    u_blizu, _, _ = k.projektuj([[0.0, 20.0, k.cilj]])
    dalja = Kamera(sirina=320, visina=240, vfov=40.0,
                   rastojanje=900.0, visina_kamere=200.0, cilj=50.0)
    u_daleko, _, _ = dalja.projektuj([[0.0, 20.0, dalja.cilj]])
    assert abs(u_daleko[0] - dalja.cx) < abs(u_blizu[0] - k.cx)


def test_projekcija_odbija_pogresan_oblik():
    with pytest.raises(ValueError):
        _kamera().projektuj(np.zeros((4, 2)))


def test_besmislena_kamera_puca():
    with pytest.raises(ValueError):
        Kamera(vfov=0.0)
    with pytest.raises(ValueError):
        Kamera(rastojanje=-10)
    with pytest.raises(ValueError):
        Kamera(sirina=1)


# --- решетка --------------------------------------------------------------

def test_resetka_ima_trazeni_oblik_i_korak():
    centri, korak = resetka((-10, 10, -10, 10, 0, 20), (4, 4, 8))
    assert centri.shape == (4, 4, 8, 3)
    assert korak == pytest.approx((5.0, 5.0, 2.5))


def test_resetka_je_centrirana_u_celijama():
    centri, _ = resetka((0, 10, 0, 10, 0, 10), (2, 2, 2))
    assert centri[0, 0, 0].tolist() == pytest.approx([2.5, 2.5, 2.5])
    assert centri[1, 1, 1].tolist() == pytest.approx([7.5, 7.5, 7.5])


def test_resetka_odbija_neispravne_granice():
    with pytest.raises(ValueError):
        resetka((10, -10, 0, 1, 0, 1), (2, 2, 2))
    with pytest.raises(ValueError):
        resetka((0, 1, 0, 1, 0, 1), (0, 2, 2))
