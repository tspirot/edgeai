import numpy as np
import pytest

from govor.asr import build_asr
from govor.asr.base import Segment, Transkript
from govor.config import Config, load_config
from govor.korpus import Govornik, Korpus
from govor.pipeline import Stanica


def _cfg():
    cfg = Config()
    cfg.asr.backend = "dummy"
    return cfg


def _zvuk(sekundi=6.0, sr=16000):
    t = np.linspace(0, sekundi, int(sr * sekundi), endpoint=False)
    return (0.3 * np.sin(2 * np.pi * 180 * t)).astype(np.float32)


# --- конфигурација --------------------------------------------------------

def test_podrazumevana_konfiguracija():
    cfg = load_config()
    assert cfg.asr.backend == "faster-whisper"
    assert cfg.audio.samplerate == 16000


def test_konfiguracija_iz_fajla(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("asr:\n  backend: dummy\nkorpus:\n  koren: /tmp/k\n", encoding="utf-8")
    cfg = load_config(p)
    assert cfg.asr.backend == "dummy"
    assert cfg.korpus.koren == "/tmp/k"
    assert cfg.audio.samplerate == 16000        # нетакнуто


def test_nepoznata_opcija_puca(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("asr:\n  cudo: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Непозната опција"):
        load_config(p)


# --- ASR dummy ----------------------------------------------------------

def test_dummy_asr_je_deterministican():
    a = build_asr(_cfg().asr)
    z = _zvuk()
    assert a.transkribuj(z, 16000).tekst == a.transkribuj(z, 16000).tekst


def test_dummy_asr_prazan_zvuk():
    t = build_asr(_cfg().asr).transkribuj(np.zeros(0, dtype=np.float32), 16000)
    assert t.segmenti == []


def test_nepoznat_asr_puca():
    cfg = _cfg().asr
    cfg.backend = "cudo"
    with pytest.raises(ValueError, match="Непознат ASR"):
        build_asr(cfg)


def test_transkript_deli_recenice():
    t = Transkript(segmenti=[Segment(0, 2, "Прва реченица. Друга реченица!")])
    assert t.recenice() == ["Прва реченица.", "Друга реченица!"]


def test_segment_obrnut_puca():
    with pytest.raises(ValueError):
        Segment(pocetak=5.0, kraj=2.0, tekst="x")


# --- обрада -----------------------------------------------------------

def test_obrada_daje_stavke_sa_ocenom():
    sesija = Stanica(_cfg()).obradi(_zvuk(), 16000, "g1")
    assert sesija.stavke
    # dummy реченице су пиротске — бар једна мора бити јако дијалекатска
    assert any(s.skor > 0.2 for s in sesija.stavke)


def test_obrada_dodaje_recnicke_beleske():
    sesija = Stanica(_cfg()).obradi(_zvuk(), 16000, "g1")
    assert any(s.recnik_beleske for s in sesija.stavke)


# --- упис исправке у корпус -----------------------------------------

def test_sacuvaj_ispravku_upise_par_i_isecak(tmp_path):
    cfg = _cfg()
    cfg.korpus.koren = str(tmp_path / "korpus")
    stanica = Stanica(cfg)
    audio = _zvuk()
    sesija = stanica.obradi(audio, 16000, "g1")

    korpus = Korpus(cfg.korpus.koren)
    korpus.dodaj_govornika(Govornik("g1", "М. Ј.", saglasnost=True))
    unos = stanica.sacuvaj_ispravku(korpus, sesija, audio, 0, "Съга че идем.")

    assert unos.tekst_ispravljen == "Съга че идем."
    assert unos.skor_torlacnosti > 0.3
    assert unos.crte                          # бар полугласник + че
    assert (korpus.isecci_dir / f"{unos.id}.wav").exists()


def test_prazna_ispravka_puca(tmp_path):
    cfg = _cfg()
    cfg.korpus.koren = str(tmp_path / "korpus")
    stanica = Stanica(cfg)
    audio = _zvuk()
    sesija = stanica.obradi(audio, 16000, "g1")
    korpus = Korpus(cfg.korpus.koren)
    korpus.dodaj_govornika(Govornik("g1", "М. Ј."))
    with pytest.raises(ValueError, match="празан"):
        stanica.sacuvaj_ispravku(korpus, sesija, audio, 0, "   ")


def test_prekratak_segment_ne_ide_u_korpus(tmp_path):
    cfg = _cfg()
    cfg.korpus.koren = str(tmp_path / "korpus")
    cfg.korpus.min_trajanje_s = 100.0        # ништа неће проћи
    stanica = Stanica(cfg)
    audio = _zvuk()
    sesija = stanica.obradi(audio, 16000, "g1")
    korpus = Korpus(cfg.korpus.koren)
    korpus.dodaj_govornika(Govornik("g1", "М. Ј."))
    with pytest.raises(ValueError, match="не иде у корпус"):
        stanica.sacuvaj_ispravku(korpus, sesija, audio, 0, "нешто")


def test_nepostojeci_segment_puca(tmp_path):
    cfg = _cfg()
    cfg.korpus.koren = str(tmp_path / "korpus")
    stanica = Stanica(cfg)
    audio = _zvuk()
    sesija = stanica.obradi(audio, 16000, "g1")
    korpus = Korpus(cfg.korpus.koren)
    korpus.dodaj_govornika(Govornik("g1", "М. Ј."))
    with pytest.raises(IndexError):
        stanica.sacuvaj_ispravku(korpus, sesija, audio, 999, "x")


def test_istaknute_filtriraju_po_skoru():
    sesija = Stanica(_cfg()).obradi(_zvuk(), 16000, "g1")
    svih = len(sesija.stavke)
    istaknutih = len(sesija.istaknute(0.9))
    assert istaknutih <= svih
