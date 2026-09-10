import numpy as np
import pytest

from cilim import paleta as pal
from cilim.karton import Karton


def _sahovnica(n=32, polje=8):
    i = np.arange(n)[:, None] // polje
    j = np.arange(n)[None, :] // polje
    return ((i + j) % 2).astype(np.int16)


def test_sazimanje_na_manju_mrezu():
    k = Karton.iz_indeksa(_sahovnica(32, 8), redova=4, kolona=4)
    assert k.mreza.shape == (4, 4)
    assert k.redova == 4 and k.kolona == 4


def test_sazimanje_cuva_krupnu_saru():
    k = Karton.iz_indeksa(_sahovnica(32, 16), redova=2, kolona=2)
    assert k.mreza.tolist() == [[0, 1], [1, 0]]


def test_gusci_karton_od_sare_puca():
    with pytest.raises(ValueError, match="гушћи"):
        Karton.iz_indeksa(np.zeros((8, 8), dtype=np.int16), redova=16, kolona=16)


def test_nula_redova_puca():
    with pytest.raises(ValueError):
        Karton.iz_indeksa(np.zeros((8, 8), dtype=np.int16), redova=0, kolona=4)


def test_jednodimenzionalan_ulaz_puca():
    with pytest.raises(ValueError):
        Karton.iz_indeksa(np.zeros(8, dtype=np.int16), redova=2, kolona=2)


def test_legenda_ima_samo_upotrebljene_boje():
    k = Karton.iz_indeksa(_sahovnica(), redova=4, kolona=4)
    upotrebljene = {s["indeks"] for s in k.legenda()}
    assert upotrebljene == {0, 1}
    assert len(upotrebljene) < len(pal.PALETA)


def test_legenda_broji_celije():
    k = Karton(mreza=np.array([[0, 0, 1]], dtype=np.int16))
    po_indeksu = {s["indeks"]: s["celija"] for s in k.legenda()}
    assert po_indeksu == {0: 2, 1: 1}


def test_promene_po_redu():
    k = Karton(mreza=np.array([[0, 0, 1, 1], [0, 1, 0, 1]], dtype=np.int16))
    assert k.promene_po_redu().tolist() == [1, 3]


def test_rezime_navodi_dimenzije_i_niti():
    k = Karton(mreza=np.zeros((10, 5), dtype=np.int16), niti_po_celiji=2)
    r = k.rezime()
    assert "10 редова × 5 колона" in r
    assert "20 нити потке" in r


def test_csv_sadrzi_legendu_i_mrezu(tmp_path):
    k = Karton(mreza=np.array([[0, 1], [1, 0]], dtype=np.int16))
    p = k.u_csv(tmp_path / "a" / "karton.csv")
    tekst = p.read_text(encoding="utf-8")
    assert tekst.startswith("# картон за ткање")
    assert pal.PALETA[0].naziv in tekst
    assert "0,1" in tekst


def test_png_ima_ocekivanu_velicinu(tmp_path):
    from PIL import Image

    k = Karton(mreza=np.zeros((4, 6), dtype=np.int16))
    p = k.u_png(tmp_path / "karton.png", piksela_po_celiji=10)
    with Image.open(p) as im:
        assert im.size == (60, 40)   # (ширина, висина)
