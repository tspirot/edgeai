import pytest

from cilim import motivi as mot


def test_ucitava_katalog_uz_paket():
    katalog = mot.ucitaj()
    assert len(katalog) > 0
    assert "kornjaca" in katalog


def test_kornjaca_ima_znacenje_i_izvor():
    m = mot.ucitaj().nadji("kornjaca")
    assert "Пирот" in m.znacenje          # корњача је на грбу града
    assert m.izvor


def test_nepoznata_sara_puca_sa_spiskom():
    with pytest.raises(KeyError, match="kornjaca"):
        mot.ucitaj().nadji("zmaj")


def test_nepotvrdjeno_znacenje_nosi_ogradu():
    m = mot.ucitaj().nadji("kondiceva")
    assert not m.potvrdila_radionica
    assert "НЕПОТВРЂЕНО" in m.opis()


def test_potvrdjeno_znacenje_je_bez_ograde():
    m = mot.Motiv(
        id="x", naziv="проба", znacenje="значење", deo="поље",
        izvor=("radionica",), potvrdila_radionica=True,
    )
    assert "НЕПОТВРЂЕНО" not in m.opis()
    assert m.opis() == "проба: значење"


def test_katalog_upozorava_dok_ima_nepotvrdjenih():
    katalog = mot.ucitaj()
    assert katalog.potvrdjenih < len(katalog)
    assert "није потврдила радионица" in katalog.upozorenje()


def test_katalog_bez_upozorenja_kad_je_sve_potvrdjeno():
    m = mot.Motiv("x", "проба", "значење", "поље", (), True)
    assert mot.Katalog([m]).upozorenje() is None


def test_dupli_id_puca():
    m = mot.Motiv("x", "а", "з", "поље", (), False)
    with pytest.raises(ValueError, match="исти"):
        mot.Katalog([m, m])


def test_nepoznat_deo_cilima_puca():
    with pytest.raises(ValueError, match="непознат део"):
        mot._motiv_iz({"id": "x", "naziv": "а", "znacenje": "з", "deo": "таван"}, 1)


def test_odrednica_bez_naziva_puca():
    with pytest.raises(ValueError, match="naziv"):
        mot._motiv_iz({"id": "x", "znacenje": "з"}, 3)


def test_izvor_kao_niz_postaje_torka():
    m = mot._motiv_iz({"id": "x", "naziv": "а", "znacenje": "з", "izvor": "nkns"}, 1)
    assert m.izvor == ("nkns",)


def test_nepostojeci_katalog_puca(tmp_path):
    with pytest.raises(FileNotFoundError):
        mot.ucitaj(tmp_path / "nema.yaml")


def test_prazan_katalog_puca(tmp_path):
    p = tmp_path / "prazan.yaml"
    p.write_text("verzija: 1\nmotivi: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="ниједну одредницу"):
        mot.ucitaj(p)


def test_svaka_odrednica_ima_izvor():
    """Назив без извора је измишљен назив — то овај пројекат не сме да ради."""
    for m in mot.ucitaj():
        assert m.izvor, f"шара '{m.id}' нема наведен извор"
