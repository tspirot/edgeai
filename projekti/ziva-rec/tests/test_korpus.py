import numpy as np
import pytest

from govor.korpus import Govornik, Korpus, Unos, ucitaj_wav, upisi_wav


def _zvuk(sekundi=2.0, sr=16000):
    t = np.linspace(0, sekundi, int(sr * sekundi), endpoint=False)
    return (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)


def _unos(korpus, gid="g1", **kw):
    baza = dict(
        id=korpus._sledeci_id(), govornik_id=gid,
        tekst_asr="хлеб", tekst_ispravljen="лебац",
        pocetak=0.0, kraj=2.0, samplerate=16000,
    )
    baza.update(kw)
    return Unos(**baza)


# --- WAV ----------------------------------------------------------------

def test_wav_krug_upis_citanje(tmp_path):
    zvuk = _zvuk()
    p = upisi_wav(tmp_path / "a.wav", zvuk, 16000)
    vraceno, sr = ucitaj_wav(p)
    assert sr == 16000
    assert vraceno.shape == zvuk.shape
    assert np.max(np.abs(vraceno - zvuk)) < 1e-3


def test_wav_stereo_se_svede_na_mono(tmp_path):
    stereo = np.zeros((1000, 2), dtype=np.float32)
    p = upisi_wav(tmp_path / "s.wav", stereo, 16000)
    vraceno, _ = ucitaj_wav(p)
    assert vraceno.ndim == 1


# --- говорници --------------------------------------------------------

def test_govornik_bez_inicijala_puca():
    with pytest.raises(ValueError):
        Govornik(id="g1", inicijali="")


def test_govornik_se_upise_i_ucita(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("g1", "М. Ј.", selo="Крупац", saglasnost=True))
    assert Korpus(tmp_path / "korpus").govornici["g1"].selo == "Крупац"


# --- уноси ------------------------------------------------------------

def test_unos_bez_poznatog_govornika_puca(tmp_path):
    k = Korpus(tmp_path / "korpus")
    with pytest.raises(ValueError, match="није у корпусу"):
        k.dodaj_unos(_unos(k), _zvuk())


def test_dodaj_i_procitaj_unos(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("g1", "М. Ј."))
    k.dodaj_unos(_unos(k), _zvuk())
    unosi = k.unosi()
    assert len(unosi) == 1
    assert unosi[0].tekst_ispravljen == "лебац"
    assert unosi[0].ispravljan          # хлеб != лебац


def test_id_raste(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("g1", "М. Ј."))
    k.dodaj_unos(_unos(k), _zvuk())
    k.dodaj_unos(_unos(k), _zvuk())
    assert [u.id for u in k.unosi()] == ["000000", "000001"]


def test_isecak_zvuka_se_upise(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("g1", "М. Ј."))
    k.dodaj_unos(_unos(k), _zvuk())
    assert (k.isecci_dir / "000000.wav").exists()


# --- одобравање и извоз ---------------------------------------------

def test_odobravanje(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("g1", "М. Ј.", saglasnost=True))
    k.dodaj_unos(_unos(k), _zvuk())
    assert not k.unosi()[0].odobreno
    k.odobri("000000")
    assert k.unosi()[0].odobreno


def test_izvoz_samo_odobreno_i_sa_saglasnoscu(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("saglasan", "А. А.", saglasnost=True))
    k.dodaj_govornika(Govornik("bez", "Б. Б.", saglasnost=False))

    k.dodaj_unos(_unos(k, gid="saglasan"), _zvuk())       # одобрићемо
    k.dodaj_unos(_unos(k, gid="saglasan"), _zvuk())       # неодобрено
    k.dodaj_unos(_unos(k, gid="bez", odobreno=True), _zvuk())  # одобрено али без сагласности
    k.odobri("000000")

    izvoz = k.za_doobuku()
    assert len(izvoz) == 1
    assert izvoz[0][1] == "лебац"


def test_izvoz_prazan_kad_nista_nije_spremno(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("g1", "М. Ј.", saglasnost=True))
    k.dodaj_unos(_unos(k), _zvuk())
    assert k.za_doobuku() == []


def test_odobri_nepostojeci_unos_puca(tmp_path):
    k = Korpus(tmp_path / "korpus")
    with pytest.raises(KeyError):
        k.odobri("999999")


# --- резиме ----------------------------------------------------------

def test_rezime_broji_sve(tmp_path):
    k = Korpus(tmp_path / "korpus")
    k.dodaj_govornika(Govornik("g1", "М. Ј.", saglasnost=True))
    k.dodaj_unos(_unos(k), _zvuk())
    k.odobri("000000")
    r = k.rezime()
    assert r["unosa"] == 1
    assert r["odobrenih"] == 1
    assert r["ispravljanih"] == 1
    assert r["sa_saglasnoscu"] == 1
    assert r["sati_zvuka"] >= 0.0     # два секунда се заокруже на 0.0 h — то је ок
