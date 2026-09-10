import struct

import numpy as np
import pytest

from dvojnik.mreza import blokovska_mreza, gabarit, skaliraj, u_stl


def _jedan_voksel():
    z = np.zeros((3, 3, 3), bool)
    z[1, 1, 1] = True
    return z, (0.0, 3.0, 0.0, 3.0, 0.0, 3.0), (1.0, 1.0, 1.0)


def test_jedan_voksel_daje_dvanaest_trouglova():
    """Шест страница коцке, свака два троугла."""
    assert len(blokovska_mreza(*_jedan_voksel())) == 12


def test_dva_spojena_voksela_nemaju_zid_izmedju():
    z = np.zeros((4, 3, 3), bool)
    z[1, 1, 1] = z[2, 1, 1] = True
    t = blokovska_mreza(z, (0.0, 4.0, 0.0, 3.0, 0.0, 3.0), (1.0, 1.0, 1.0))
    # 12 страница квадра уместо 2×6 — додирне странице нема
    assert len(t) == 20


def test_prazna_mreza_nema_trouglova():
    z = np.zeros((3, 3, 3), bool)
    assert len(blokovska_mreza(z, (0.0, 3.0, 0.0, 3.0, 0.0, 3.0), (1, 1, 1))) == 0


def test_voksel_je_na_pravom_mestu():
    t = blokovska_mreza(*_jedan_voksel())
    tacke = t.reshape(-1, 3)
    assert tacke.min() == pytest.approx(1.0)
    assert tacke.max() == pytest.approx(2.0)


def test_gabarit_jednog_voksela():
    assert gabarit(blokovska_mreza(*_jedan_voksel())) == pytest.approx((1.0, 1.0, 1.0))


def test_gabarit_prazne_mreze():
    assert gabarit(np.zeros((0, 3, 3))) == (0.0, 0.0, 0.0)


def test_neispravan_oblik_puca():
    with pytest.raises(ValueError):
        blokovska_mreza(np.zeros((3, 3), bool), (0, 1, 0, 1, 0, 1), (1, 1, 1))


# --- размера --------------------------------------------------------------

def test_skaliranje_menja_gabarit():
    t = blokovska_mreza(*_jedan_voksel())
    assert gabarit(skaliraj(t, 2.5)) == pytest.approx((2.5, 2.5, 2.5))


def test_negativna_razmera_puca():
    with pytest.raises(ValueError):
        skaliraj(blokovska_mreza(*_jedan_voksel()), -1)


# --- STL ------------------------------------------------------------------

def test_stl_ima_ispravno_zaglavlje_i_broj(tmp_path):
    t = blokovska_mreza(*_jedan_voksel())
    p = u_stl(t, tmp_path / "a" / "model.stl", "проба")
    podaci = p.read_bytes()
    assert len(podaci) == 84 + 50 * 12
    assert struct.unpack("<I", podaci[80:84])[0] == 12


def test_stl_normale_su_jedinicne(tmp_path):
    t = blokovska_mreza(*_jedan_voksel())
    p = u_stl(t, tmp_path / "model.stl")
    podaci = p.read_bytes()
    for i in range(12):
        pocetak = 84 + i * 50
        n = np.frombuffer(podaci[pocetak:pocetak + 12], dtype="<f4")
        assert np.linalg.norm(n) == pytest.approx(1.0, abs=1e-5)


def test_stl_odbija_pogresan_oblik(tmp_path):
    with pytest.raises(ValueError):
        u_stl(np.zeros((5, 3)), tmp_path / "model.stl")


def test_stl_naziv_bez_ascii_ne_ruši_fajl(tmp_path):
    """Ћирилични назив мора да прође — заглавље је ASCII, па се замењује."""
    t = blokovska_mreza(*_jedan_voksel())
    p = u_stl(t, tmp_path / "model.stl", "Двојник")
    assert p.read_bytes()[:80].__len__() == 80
