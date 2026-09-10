import pytest

from govor import recnik as recnik_mod


def test_ucitava_recnik_uz_paket():
    r = recnik_mod.ucitaj()
    assert len(r) > 0
    assert "лебац" in r
    assert "съга" in r


def test_nadji_vraca_odrednicu():
    o = recnik_mod.ucitaj().nadji("работим")
    assert o is not None
    assert "радим" in o.znaci


def test_nepoznata_rec_vraca_none():
    assert recnik_mod.ucitaj().nadji("аутомобил") is None


def test_nepotvrdjeno_znacenje_nosi_ogradu():
    o = recnik_mod.ucitaj().nadji("лебац")
    assert not o.potvrdio_govornik
    assert "НЕПОТВРЂЕНО" in o.opis()


def test_potvrdjena_odrednica_bez_ograde():
    o = recnik_mod.Odrednica("x", "значење", "", ("govornik",), True)
    assert "НЕПОТВРЂЕНО" not in o.opis()


def test_recnik_upozorava_dok_ima_nepotvrdjenih():
    r = recnik_mod.ucitaj()
    assert r.potvrdjenih < len(r)
    assert "још није потврдио говорник" in r.upozorenje()


def test_svaka_odrednica_ima_izvor():
    for o in recnik_mod.ucitaj():
        assert o.izvor, f"'{o.rec}' нема извор"


def test_odrednica_bez_izvora_puca():
    with pytest.raises(ValueError, match="нема извор"):
        recnik_mod._odrednica_iz({"rec": "x", "znaci": "y"}, 1)


def test_duplirana_rec_puca():
    o = recnik_mod.Odrednica("реч", "а", "", ("z",), False)
    with pytest.raises(ValueError, match="истом речи"):
        recnik_mod.Recnik([o, o])


def test_pretraga_ne_zavisi_od_pisma():
    r = recnik_mod.ucitaj()
    assert "rabotim" in r          # латиница се пресловљава при упиту


def test_nepostojeci_recnik_puca(tmp_path):
    with pytest.raises(FileNotFoundError):
        recnik_mod.ucitaj(tmp_path / "nema.yaml")
