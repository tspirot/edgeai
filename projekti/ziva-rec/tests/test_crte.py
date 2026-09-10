import pytest

from govor import crte


# --- издвајање речи ------------------------------------------------------

def test_reci_hvata_cirilicu_i_crticu():
    assert crte.reci("Той човекат нај-убаво пее.") == ["той", "човекат", "нај-убаво", "пее"]


def test_reci_preslovljava_latinicu():
    assert crte.reci("saga che idem") == ["сага", "цхе", "идем"]  # груб пресловник, без диграфа


def test_reci_cuva_poluglas_i_dz():
    assert crte.reci("със ѕвезда") == ["със", "ѕвезда"]


# --- појединачне црте ---------------------------------------------------

def test_poluglas_je_jak_znak():
    n = crte.oceni("Съга че идем.")
    assert "poluglas" in n.oznake[0]
    assert n.skor > 0.5


def test_dz_se_prepoznaje():
    n = crte.oceni("Гледа у ѕвезде.")
    assert "dz" in n.oznake[crte.reci("Гледа у ѕвезде.").index("ѕвезде")]


def test_analiticki_komparativ():
    n = crte.oceni("Тъг беше по-убаво него съга.")
    assert any("komparativ-po" in o for o in n.oznake)
    assert any("superlativ-naj" in o for o in crte.oceni("Той нај-убаво пее.").oznake)


def test_postpozitivni_clan_muski():
    n = crte.oceni("Дошја човекат из град.")
    assert "clan-m" in n.oznake[1]


def test_postpozitivni_clan_srednji():
    n = crte.oceni("Детето спи.")
    assert "clan-s" in n.oznake[0]


def test_izgubljeno_h():
    n = crte.oceni("Оћу да купим лебац.")
    assert "izgubljeno-h" in n.oznake[0]     # оћу
    assert "izgubljeno-h" in n.oznake[3]     # лебац


def test_aorist_imperfekat():
    n = crte.oceni("Ја реко, тъг беше.")
    assert "aorist-imperfekat" in n.oznake[1]
    assert "aorist-imperfekat" in n.oznake[-1]


def test_ce_futur():
    n = crte.oceni("Че идем у град.")
    assert "ce-futur" in n.oznake[0]


def test_radni_pridev_dosja():
    n = crte.oceni("Он дошја кући.")
    assert "radni-pridev" in n.oznake[1]


def test_da_prezent_kao_par():
    n = crte.oceni("Оћу да идем.")
    da = n.reci.index("да")
    assert "da-prezent" in n.oznake[da]


def test_da_na_kraju_recenice_nije_par():
    n = crte.oceni("Реко да.")
    assert "da-prezent" not in n.oznake[-1]


# --- скор --------------------------------------------------------------

def test_standardna_recenica_ima_nizak_skor():
    n = crte.oceni("Данас ћу отићи у град да купим хлеб.")
    assert n.skor < 0.2
    assert not n.jako_dijalekatska


def test_jako_dijalekatska_recenica():
    n = crte.oceni("Съга че идем да купим лебац, море.")
    assert n.jako_dijalekatska
    assert n.skor >= 0.35


def test_prazna_recenica_skor_nula():
    assert crte.oceni("").skor == 0.0
    assert crte.oceni("   ...  ").skor == 0.0


def test_skor_je_ogranicen_na_jedan():
    n = crte.oceni("Със ѕид, съга, тъг, по-убав.")
    assert n.skor <= 1.0


def test_sazetak_navodi_crte():
    s = crte.oceni("Съга че идем.").sazetak()
    assert "скор" in s and "poluglas" in s


# --- речник подиже скор ------------------------------------------------

def test_recnik_pogodak_povecava_skor():
    from govor import recnik as recnik_mod

    r = recnik_mod.ucitaj()
    tekst = "Сакам да вревим."
    bez = crte.oceni(tekst).skor
    sa = crte.oceni(tekst, r).skor
    assert sa > bez


def test_torlackih_reci_broji_i_crte_i_recnik():
    from govor import recnik as recnik_mod

    n = crte.oceni("Съга сакам лебац.", recnik_mod.ucitaj())
    assert n.torlackih_reci >= 2
