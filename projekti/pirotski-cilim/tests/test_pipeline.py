import numpy as np
import pytest

from cilim import motivi as mot
from cilim import paleta as pal
from cilim import pravila as prv
from cilim.config import Config, load_config
from cilim.generator import build_generator
from cilim.klasifikator import build_klasifikator
from cilim.pipeline import Radionica


def _cfg_bez_modela():
    """Подразумевана мрежа картона (64×48) — на њој шара има где да стане."""
    cfg = Config()
    cfg.klasifikator.backend = "dummy"
    cfg.generator.backend = "pravila"
    return cfg


def _skica_u_sredini(n=128):
    """Бели лист са потезом у средини — потез преживи огледање."""
    skica = np.full((n, n, 3), 255, dtype=np.uint8)
    cetvrt = n // 4
    skica[cetvrt : n - cetvrt, cetvrt : n - cetvrt] = 0
    return skica


def _slika(vrednost=120, n=64):
    return np.full((n, n, 3), vrednost, dtype=np.uint8)


# --- конфигурација --------------------------------------------------------

def test_podrazumevana_konfiguracija_bez_fajla():
    cfg = load_config()
    assert cfg.generator.backend == "difuzija"
    assert cfg.pravila.min_niti == 3


def test_konfiguracija_iz_fajla(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("pravila:\n  min_niti: 6\nlog_level: DEBUG\n", encoding="utf-8")
    cfg = load_config(p)
    assert cfg.pravila.min_niti == 6
    assert cfg.log_level == "DEBUG"
    assert cfg.karton.redova == 64          # остало нетакнуто


def test_nepoznata_opcija_puca(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("pravila:\n  nepostojeca: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Непозната опција"):
        load_config(p)


def test_nepostojeci_config_puca(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nema.yaml")


# --- избор модула ---------------------------------------------------------

def test_nepoznat_klasifikator_puca():
    cfg = Config()
    cfg.klasifikator.backend = "cudo"
    with pytest.raises(ValueError, match="Непознат класификатор"):
        build_klasifikator(mot.ucitaj(), cfg.klasifikator)


def test_nepoznat_generator_puca():
    cfg = Config()
    cfg.generator.backend = "cudo"
    with pytest.raises(ValueError, match="Непознат генератор"):
        build_generator(mot.ucitaj(), cfg)


# --- класификатор ---------------------------------------------------------

def test_dummy_klasifikator_je_deterministican():
    k = build_klasifikator(mot.ucitaj(), _cfg_bez_modela().klasifikator)
    assert k.prepoznaj(_slika()).motiv_id == k.prepoznaj(_slika()).motiv_id


def test_dummy_klasifikator_vraca_saru_iz_kataloga():
    katalog = mot.ucitaj()
    k = build_klasifikator(katalog, _cfg_bez_modela().klasifikator)
    assert k.prepoznaj(_slika()).motiv_id in katalog


def test_dummy_klasifikator_odbija_praznu_sliku():
    k = build_klasifikator(mot.ucitaj(), _cfg_bez_modela().klasifikator)
    with pytest.raises(ValueError):
        k.prepoznaj(np.zeros((0, 0, 3), dtype=np.uint8))


def test_klasifikator_bez_kataloga_puca():
    from cilim.klasifikator.dummy_backend import DummyKlasifikator

    with pytest.raises(ValueError, match="празан"):
        DummyKlasifikator(mot.Katalog([]))


# --- читање шаре ----------------------------------------------------------

def test_procitaj_vraca_znacenje_sa_ogradom():
    radionica = Radionica(_cfg_bez_modela())
    _, tekst = radionica.procitaj(_slika())
    # каталог још нико није потврдио, па свако значење мора носити ограду
    assert "НЕПОТВРЂЕНО" in tekst or "Нисам сигуран" in tekst


def test_procitaj_priznaje_nesigurnost():
    cfg = _cfg_bez_modela()
    cfg.klasifikator.min_pouzdanost = 0.99      # ништа не пролази
    _, tekst = Radionica(cfg).procitaj(_slika())
    assert "Нисам сигуран" in tekst


# --- предлог шаре ---------------------------------------------------------

def test_smisli_daje_izvodljiv_predlog():
    predlog = Radionica(_cfg_bez_modela()).smisli(seed=3)
    assert predlog.izvestaj.izvodljivo()
    assert predlog.karton.mreza.shape == (64, 48)


def test_procedurani_predlog_nema_nijedan_kratak_potez():
    """Правила генератор не сме да се ослања на накнадно чишћење."""
    for seed in range(6):
        izvestaj = Radionica(_cfg_bez_modela()).smisli(seed=seed).izvestaj
        assert izvestaj.kratkih == 0, f"seed {seed}: {izvestaj}"


def test_premali_karton_puca():
    cfg = _cfg_bez_modela()
    cfg.karton.redova = 12
    cfg.karton.kolona = 12
    with pytest.raises(ValueError, match="премали"):
        Radionica(cfg).smisli()


def test_predlog_je_simetrican():
    idx = Radionica(_cfg_bez_modela()).smisli(seed=1).indeksi
    assert (idx == np.flip(idx, axis=1)).all()
    assert (idx == np.flip(idx, axis=0)).all()


def test_predlog_koristi_samo_paletu():
    predlog = Radionica(_cfg_bez_modela()).smisli(seed=5)
    assert predlog.indeksi.max() < len(pal.PALETA)
    assert predlog.slika.shape[2] == 3


def test_isti_seed_daje_isti_predlog():
    a = Radionica(_cfg_bez_modela()).smisli(motiv_id="kornjaca", seed=42)
    b = Radionica(_cfg_bez_modela()).smisli(motiv_id="kornjaca", seed=42)
    assert (a.indeksi == b.indeksi).all()


def test_razlicit_seed_daje_razlicit_predlog():
    a = Radionica(_cfg_bez_modela()).smisli(motiv_id="kornjaca", seed=1)
    b = Radionica(_cfg_bez_modela()).smisli(motiv_id="kornjaca", seed=2)
    assert not (a.indeksi == b.indeksi).all()


def test_skica_menja_rezultat():
    cfg = _cfg_bez_modela()
    bez = Radionica(cfg).smisli(seed=4)
    sa = Radionica(cfg).smisli(skica=_skica_u_sredini(), seed=4)
    assert not (bez.indeksi == sa.indeksi).all()


def test_skica_u_uglu_nestaje_u_ogledanju():
    """Од скице преживи само горња лева четвртина — то је последица симетрије.

    Ако се ово икад промени, промењена је и грамматика ћилима, па нека тест
    падне и натера некога да то објасни.
    """
    cfg = _cfg_bez_modela()
    puna = np.zeros((128, 128, 3), dtype=np.uint8)          # све „потез“
    ugao = np.zeros((128, 128, 3), dtype=np.uint8)
    ugao[64:, 64:] = 255                                     # доњи десни угао празан
    a = Radionica(cfg).smisli(skica=puna, seed=6)
    b = Radionica(cfg).smisli(skica=ugao, seed=6)
    assert (a.indeksi == b.indeksi).all()


def test_nepoznata_sara_u_predlogu_puca():
    with pytest.raises(KeyError):
        Radionica(_cfg_bez_modela()).smisli(motiv_id="zmaj")


def test_skica_bez_kontrasta_znaci_punu_saru():
    """Потпуно поцрњен лист је „нема упутства“, не „празан ћилим“."""
    cfg = _cfg_bez_modela()
    bez = Radionica(cfg).smisli(seed=9)
    puna = Radionica(cfg).smisli(skica=np.zeros((64, 64, 3), dtype=np.uint8), seed=9)
    assert (bez.indeksi == puna.indeksi).all()


def test_ispis_predloga_nosi_pravnu_ogradu():
    """Уређај никад не сме свој излаз назвати „пиротски ћилим“."""
    ispis = str(Radionica(_cfg_bez_modela()).smisli(seed=2))
    assert "У ДУХУ" in ispis
    assert "географска ознака" in ispis


def test_predlog_prolazi_proveru_razboja():
    predlog = Radionica(_cfg_bez_modela()).smisli(seed=8)
    ponovo = prv.proveri(predlog.karton.mreza, min_niti=3)
    assert ponovo.kratkih == predlog.izvestaj.kratkih


def test_slika_prikazuje_bas_ono_sto_karton_kaze():
    """Оно што посетилац гледа мора бити оно што ткаља тка."""
    predlog = Radionica(_cfg_bez_modela()).smisli(seed=11)
    f = predlog.indeksi.shape[0] // predlog.karton.redova
    sazeto = predlog.indeksi[::f, ::f]
    assert (sazeto == predlog.karton.mreza).all()


def test_radionica_se_zatvara_bez_greske():
    radionica = Radionica(_cfg_bez_modela())
    radionica.smisli(seed=0)
    radionica.close()
