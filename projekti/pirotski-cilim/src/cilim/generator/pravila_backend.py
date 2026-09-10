"""Генератор без иједног модела — шара се гради само из правила заната.

Овај модул постоји из три разлога:

1. Цео ланац ради на било ком рачунару, без Jetson-а, без CUDA и без преузетих
   тежина — па се пројекат може развијати и тестирати ван радионице.
2. Ученик види грамматику ћилима исписану као кôд: појасеви, огледање,
   концентрични ромбови, куке по угловима. Дифузиони модел исто то ради, само
   што се код њега не види.
3. Служи као мерило. Ако дифузиони модел не даје шару бољу од ове, не вреди
   његових петнаест вати.

Ради на **мрежи картона**, не на пикселима. То је намерно: правило о најкраћем
потезу мери се на картону, на ћелији коју ткаља отка у једном маху. Кад би се
шара цртала на пикселима па тек онда сажимала на картон, ситан детаљ би прошао
кроз пиксел-проверу а пао на картону. Зато генератор одмах ради тамо где се и
мери, и све димензије изводи из `min_niti`.
"""

from __future__ import annotations

import zlib

import numpy as np

from cilim import paleta as pal
from cilim import pravila
from cilim.generator.base import GeneratorBackend

PRSTENOVA = 4       # концентричних прстенова у једној ћелији поља


def _seme(motiv_id: str, seed: int) -> int:
    """Стабилно семе — `hash()` за низове мења вредност између покретања."""
    osnova = zlib.crc32((motiv_id or "").encode("utf-8"))
    return (osnova ^ (int(seed) & 0xFFFFFFFF)) & 0xFFFFFFFF


def _prstenovi(h: int, w: int, boje) -> np.ndarray:
    """Ћелија поља: концентрични ромбови — основни облик кроз цео каталог."""
    i = (np.arange(h)[:, None] + 0.5) / h - 0.5
    j = (np.arange(w)[None, :] + 0.5) / w - 0.5
    # 0 у средишту, 1 на врховима ромба
    r = np.abs(i) * 2 + np.abs(j) * 2
    n = len(boje)
    k = np.clip((r / 1.15 * n).astype(int), 0, n - 1)
    return np.asarray(boje, dtype=np.int16)[k]


def _kuke(celija: np.ndarray, boja: int, udeo: float = 0.18) -> np.ndarray:
    """Куке по угловима ћелије — аутохтона шара, и најлакша за препознати."""
    h, w = celija.shape
    d = max(int(min(h, w) * udeo), 1)
    for si in (slice(0, d), slice(h - d, h)):
        for sj in (slice(0, d), slice(w - d, w)):
            celija[si, sj] = boja
    return celija


def _rombici(h: int, w: int, korak: int, boja: int, pozadina: int) -> np.ndarray:
    """Ситни ромбови у низу — оно што иде у бордуру."""
    i = np.arange(h)[:, None] % korak
    j = np.arange(w)[None, :] % korak
    sredina = korak / 2.0
    unutra = np.abs(i - sredina) + np.abs(j - sredina) < korak / 3.0
    return np.where(unutra, boja, pozadina).astype(np.int16)


def _debljine_bar(pravila_cfg, pola_celija: float, min_niti: int):
    """Појасеви морају бити дебели бар `min_niti` ћелија, ма шта удели говорили.

    Удео од 4% на картону од 48 колона даје појас од једне ћелије. Ред који га
    пресеца тако добија потез дужине 1 на оба краја — шара која на папиру
    изгледа добро, а на разбоју не ваља. Зато се удели овде подижу на праг.
    """
    from dataclasses import replace

    najmanji = min_niti / max(pola_celija, 1e-9)
    debljine = {
        "spoljasnji_cenar": max(pravila_cfg.spoljasnji_cenar, najmanji),
        "bordura": max(pravila_cfg.bordura, najmanji),
        "unutrasnji_cenar": max(pravila_cfg.unutrasnji_cenar, najmanji),
    }
    if sum(debljine.values()) >= 1.0:
        raise ValueError(
            f"Картон је преситан: појасеви од бар {min_niti} ћелија не стају "
            f"у {int(pola_celija * 2)} ћелија. Повећај картон или смањи min_niti."
        )
    return replace(pravila_cfg, **debljine)


class PravilaGenerator(GeneratorBackend):
    def __init__(self, katalog, cfg) -> None:
        self.katalog = katalog
        self.cfg = cfg.generator
        self.pravila_cfg = cfg.pravila
        self.karton_cfg = cfg.karton

    # --- избор боја --------------------------------------------------------

    def _boje(self, rng):
        """Црвена носи, остале прате — тако ћилим и изгледа."""
        crvene = [pal.indeks_boje(c) for c in pal.CRVENE]
        ostale = [
            pal.indeks_boje(c) for c in ("crna", "bela", "zuta", "plava", "zelena")
        ]
        glavna = int(rng.choice(crvene))
        prateca = rng.choice(ostale, size=2, replace=False)
        return {
            "polje_pozadina": glavna,
            "prstenovi": [int(prateca[0]), glavna, int(prateca[1]), glavna],
            "kuka": int(prateca[0]),
            "bordura_pozadina": pal.indeks_boje("crna"),
            "bordura_sara": int(prateca[1]),
            "cenar_spolja": pal.indeks_boje("bela"),
            "cenar_unutra": glavna,
        }

    # --- скица као управљач ------------------------------------------------

    @staticmethod
    def _skica_na_resetku(skica, redova: int, kolona: int) -> np.ndarray:
        """Скица → булова решетка: где је ученик повукао потез, ту иде пуна шара.

        Ово је оно што код дифузионог модела ради ControlNet — само видљиво.

        Пази: решетка се на крају огледа, па од скице преживи само њена горња
        лева четвртина. То није грешка него последица симетрије ћилима — али
        значи да скица мора имати бар неколико ћелија у тој четвртини да би
        уопште нешто променила.
        """
        if skica is None:
            return np.ones((redova, kolona), dtype=bool)
        arr = np.asarray(skica)
        if arr.ndim == 3:
            arr = arr[:, :, :3].mean(axis=2)
        if arr.ndim != 2 or arr.size == 0:
            raise ValueError(f"Скица мора бити (H, W) или (H, W, 3), добијено: {arr.shape}")

        # Скица без иједног контраста (празан или потпуно попуњен лист) значи
        # „нема упутства“ — не празну шару. Праг је просек, а кад је све исто,
        # ништа није испод просека, па би маска испала празна.
        if float(arr.max()) - float(arr.min()) < 1e-9:
            return np.ones((redova, kolona), dtype=bool)

        h, w = arr.shape
        if redova > h or kolona > w:
            # скица ситнија од решетке — рашири је најближим суседом
            arr = arr[np.linspace(0, h - 1, redova).astype(int)][
                :, np.linspace(0, w - 1, kolona).astype(int)
            ]
            return arr < arr.mean()

        gr = np.linspace(0, h, redova + 1).astype(int)
        gk = np.linspace(0, w, kolona + 1).astype(int)
        prosek = np.array(
            [
                [arr[gr[r] : gr[r + 1], gk[k] : gk[k + 1]].mean() for k in range(kolona)]
                for r in range(redova)
            ]
        )
        # потез је тамнији од просека целе скице
        return prosek < arr.mean()

    # --- састављање --------------------------------------------------------

    def napravi(self, skica=None, motiv_id=None, seed: int = 0) -> np.ndarray:
        if motiv_id is not None and motiv_id not in self.katalog:
            raise KeyError(f"Нема шаре '{motiv_id}' у каталогу")

        redova, kolona = int(self.karton_cfg.redova), int(self.karton_cfg.kolona)
        min_niti = int(self.pravila_cfg.min_niti)
        kraca = min(redova, kolona)

        # Ћелија поља носи PRSTENOVA концентричних прстенова, а прстен се пружа
        # преко половине ћелије — да сваки буде дебео бар `min_niti`, ћелија мора
        # бити бар 2 × PRSTENOVA × min_niti.
        najmanja_celija = 2 * PRSTENOVA * min_niti
        if kraca < najmanja_celija + 6 * min_niti:
            raise ValueError(
                f"Картон {redova}×{kolona} је премали: шара са потезом од бар "
                f"{min_niti} ћелија тражи краћу страну од најмање "
                f"{najmanja_celija + 6 * min_niti} ћелија."
            )

        rng = np.random.default_rng(_seme(motiv_id or "", seed))
        boje = self._boje(rng)

        cfg_pojasevi = _debljine_bar(self.pravila_cfg, kraca / 2.0, min_niti)
        mapa = pravila.pojasevi(redova, kolona, cfg_pojasevi)
        platno = np.full((redova, kolona), boje["polje_pozadina"], dtype=np.int16)

        # --- поље: решетка ромбова, а скица бира које су ћелије пуне --------
        najvise = max(kraca // najmanja_celija, 1)
        po_strani = int(rng.integers(1, min(najvise, 4) + 1))
        korak = max(kraca // po_strani, najmanja_celija)

        nr = -(-redova // korak)          # заокружено навише
        nk = -(-kolona // korak)
        puna = self._skica_na_resetku(skica, nr, nk)

        celija = _kuke(
            _prstenovi(korak, korak, boje["prstenovi"]), boje["kuka"],
            udeo=max(min_niti / korak, 0.12),
        )
        prazna = np.full((korak, korak), boje["polje_pozadina"], dtype=np.int16)
        for r in range(nr):
            for k in range(nk):
                blok = celija if puna[r, k] else prazna
                i0, j0 = r * korak, k * korak
                i1, j1 = min(i0 + korak, redova), min(j0 + korak, kolona)
                platno[i0:i1, j0:j1] = blok[: i1 - i0, : j1 - j0]

        # --- појасеви преко поља -------------------------------------------
        bordura = _rombici(
            redova, kolona, 3 * min_niti, boje["bordura_sara"], boje["bordura_pozadina"]
        )
        platno = np.where(mapa == pravila.BORDURA, bordura, platno)
        platno = np.where(mapa == pravila.UNUTRASNJI_CENAR, boje["cenar_unutra"], platno)
        platno = np.where(mapa == pravila.SPOLJASNJI_CENAR, boje["cenar_spolja"], platno)

        # --- симетрија, па поравнање потеза на самој мрежи картона ----------
        platno = pravila.ujednaci_simetricno(
            platno, min_niti,
            self.pravila_cfg.ogledalo_uspravno,
            self.pravila_cfg.ogledalo_vodoravno,
        )

        # --- увећање до слике ------------------------------------------------
        f = max(int(self.cfg.velicina) // max(redova, kolona), 1)
        pun = np.repeat(np.repeat(platno, f, axis=0), f, axis=1)
        return pal.u_sliku(pun)
