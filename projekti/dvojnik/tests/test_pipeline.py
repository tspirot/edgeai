import numpy as np
import pytest

from dvojnik import sim
from dvojnik.config import Config, kamera_iz, load_config
from dvojnik.karving import granice_oko_stola
from dvojnik.pipeline import Skener
from dvojnik.sto import DummySto, build_sto


def _cfg():
    cfg = Config()
    cfg.kamera.sirina = cfg.kamera.visina = 180
    cfg.kamera.vfov = 44.0
    cfg.kamera.rastojanje = 420.0
    cfg.kamera.visina_kamere = 180.0
    cfg.kamera.cilj = 45.0
    cfg.zapremina.podela = 56
    cfg.sto.backend = "dummy"
    cfg.kadrova = 18
    return cfg


def _snimak(cfg, telo):
    kamera = kamera_iz(cfg)
    granice = granice_oko_stola(cfg.zapremina.precnik, cfg.zapremina.visina)
    uglovi = sim.uglovi_punog_kruga(cfg.kadrova)
    kadrovi, pozadina = sim.kadrovi(telo, kamera, uglovi, granice, gustina=100)
    return kadrovi, pozadina, uglovi


# --- конфигурација --------------------------------------------------------

def test_podrazumevana_konfiguracija():
    cfg = load_config()
    assert cfg.kadrova == 120
    assert cfg.sto.backend == "koracni"


def test_konfiguracija_iz_fajla(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("kadrova: 60\nzapremina:\n  podela: 96\n", encoding="utf-8")
    cfg = load_config(p)
    assert cfg.kadrova == 60
    assert cfg.zapremina.podela == 96
    assert cfg.kamera.sirina == 640          # остало нетакнуто


def test_nepoznata_opcija_puca(tmp_path):
    p = tmp_path / "config.yaml"
    p.write_text("zapremina:\n  nepostojeca: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Непозната опција"):
        load_config(p)


def test_nepostojeci_config_puca(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nema.yaml")


# --- окретни сто ----------------------------------------------------------

def test_dummy_sto_broji_ugao():
    sto = DummySto(Config().sto)
    sto.okreni_za(90)
    sto.okreni_za(300)
    assert sto.ugao == pytest.approx(30.0)      # 390 ° = 30 °


def test_uglovi_pokrivaju_pun_krug():
    uglovi = DummySto(Config().sto).uglovi(4)
    assert uglovi == [0.0, 90.0, 180.0, 270.0]


def test_premalo_kadrova_puca():
    with pytest.raises(ValueError, match="премало"):
        DummySto(Config().sto).uglovi(2)


def test_nepoznat_sto_puca():
    cfg = Config().sto
    cfg.backend = "cudo"
    with pytest.raises(ValueError, match="Непознат сто"):
        build_sto(cfg)


# --- цео ланац ------------------------------------------------------------

def test_ceo_lanac_na_kugli():
    cfg = _cfg()
    skeniranje = Skener(cfg).skeniraj(*_snimak(cfg, sim.kugla(60.0)))
    dx, dy, dz = skeniranje.gabarit_mm
    for d in (dx, dy, dz):
        assert d == pytest.approx(60.0, abs=8.0)
    assert len(skeniranje.trouglovi) > 0


def test_bez_merenja_razmera_nije_poznata():
    cfg = _cfg()
    skeniranje = Skener(cfg).skeniraj(*_snimak(cfg, sim.kugla(60.0)))
    assert not skeniranje.razmera_poznata
    assert "РАЗМЕРА НИЈЕ ПОСТАВЉЕНА" in str(skeniranje)


def test_merena_visina_postavlja_razmeru():
    """Скенер нема осећај за величину док му се не да једна измерена дужина."""
    cfg = _cfg()
    kadrovi, pozadina, uglovi = _snimak(cfg, sim.kugla(60.0))
    skeniranje = Skener(cfg).skeniraj(kadrovi, pozadina, uglovi, visina_mm=100.0)
    assert skeniranje.razmera_poznata
    assert skeniranje.gabarit_mm[2] == pytest.approx(100.0, abs=0.01)
    assert "Размера постављена" in str(skeniranje)


def test_razmera_menja_i_ostale_dimenzije():
    cfg = _cfg()
    kadrovi, pozadina, uglovi = _snimak(cfg, sim.valjak(40.0, 80.0))
    bez = Skener(cfg).skeniraj(kadrovi, pozadina, uglovi)
    sa = Skener(cfg).skeniraj(kadrovi, pozadina, uglovi, visina_mm=160.0)
    odnos = sa.gabarit_mm[0] / bez.gabarit_mm[0]
    assert odnos == pytest.approx(sa.faktor_razmere, rel=1e-6)


def test_prazna_silueta_daje_jasnu_gresku():
    cfg = _cfg()
    kadrovi, pozadina, uglovi = _snimak(cfg, sim.kugla(60.0))
    cfg.silueta.prag = 250.0                    # ништа не пролази
    with pytest.raises(ValueError, match="спусти silueta.prag"):
        Skener(cfg).skeniraj(kadrovi, pozadina, uglovi)


def test_nepoznata_vrsta_mreze_puca():
    cfg = _cfg()
    cfg.mreza.vrsta = "cudo"
    with pytest.raises(ValueError, match="Непозната мрежа"):
        Skener(cfg).skeniraj(*_snimak(cfg, sim.kugla(60.0)))


def test_solja_i_valjak_daju_isti_model():
    """Граница методе, још једном — сад кроз цео ланац и на габариту."""
    cfg = _cfg()
    solja = Skener(cfg).skeniraj(*_snimak(cfg, sim.solja(60.0, 72.0, 9.0)))
    valjak = Skener(cfg).skeniraj(*_snimak(cfg, sim.valjak(60.0, 72.0)))
    assert solja.gabarit_mm == pytest.approx(valjak.gabarit_mm, abs=3.0)


def test_stl_se_upise(tmp_path):
    from dvojnik.mreza import u_stl

    cfg = _cfg()
    skeniranje = Skener(cfg).skeniraj(*_snimak(cfg, sim.kocka(50.0)))
    p = u_stl(skeniranje.trouglovi, tmp_path / "model.stl")
    assert p.exists() and p.stat().st_size > 84


# --- учитавање снимка са диска --------------------------------------------

def test_ucitavanje_snimka(tmp_path):
    from dvojnik.capture import save_image, ucitaj_snimak

    cfg = _cfg()
    kadrovi, pozadina, uglovi = _snimak(cfg, sim.kugla(60.0))
    save_image(pozadina, tmp_path / "pozadina.png")
    for i, (k, u) in enumerate(zip(kadrovi[:4], uglovi[:4])):
        save_image(k, tmp_path / f"kadar_{i:03d}_ugao_{u:.1f}.png")

    ucitani, poz, uc = ucitaj_snimak(tmp_path)
    assert len(ucitani) == 4
    assert uc == pytest.approx(uglovi[:4])
    assert poz.shape == pozadina.shape


def test_snimak_bez_pozadine_puca(tmp_path):
    from dvojnik.capture import ucitaj_snimak

    with pytest.raises(FileNotFoundError, match="pozadina.png"):
        ucitaj_snimak(tmp_path)


def test_kadar_bez_ugla_u_imenu_puca(tmp_path):
    from dvojnik.capture import save_image, ucitaj_snimak

    save_image(np.zeros((4, 4, 3), np.uint8), tmp_path / "pozadina.png")
    save_image(np.zeros((4, 4, 3), np.uint8), tmp_path / "kadar_000.png")
    with pytest.raises(ValueError, match="нема угао"):
        ucitaj_snimak(tmp_path)
