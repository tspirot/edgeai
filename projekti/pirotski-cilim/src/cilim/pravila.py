"""Правила заната, записана као кôд.

Дифузиони модел не зна ништа о ткању. Он даје слику; ткаљи треба шара. Овај
модул је разлика између то двоје и намерно **нема ниједан неурон** — свака
функција стаје у неколико десетина линија, има тест и може се објаснити ученику.

Три правила која долазе из самог заната:

1. **Пет појасева.** Пиротски ћилим се чита однутра напоље: поље (главне шаре),
   унутрашњи ћенар, бордура (плоча), спољашњи ћенар, ресе. Шара која се разлива
   преко ивице није ћилим него слика ћилима.
2. **Симетрија.** Шаре се граде огледањем и понављањем — то ћилиму даје ону
   мирноћу коју сви препознају а мало ко уме да именује.
3. **Два лица.** Техником клечања на вертикалном разбоју оба лица ћилима испадну
   потпуно иста; по томе се пиротски разликује од осталих балканских. Цена је да
   нема пловећих нити: свака боја мора да стоји у довољно дугом потезу. Косу
   линију и меки прелаз — оно што дифузиони модел најрадије црта — разбој не
   уме да исктка.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from cilim import paleta as pal

# Ознаке појасева (споља ка унутра)
SPOLJASNJI_CENAR = 3
BORDURA = 2
UNUTRASNJI_CENAR = 1
POLJE = 0

IMENA_POJASEVA = {
    POLJE: "поље",
    UNUTRASNJI_CENAR: "унутрашњи ћенар",
    BORDURA: "бордура",
    SPOLJASNJI_CENAR: "спољашњи ћенар",
}


def _udaljenost_od_ivice(h: int, w: int) -> np.ndarray:
    """За сваку тачку: колико је редова/колона удаљена од најближе ивице."""
    i = np.arange(h)[:, None]
    j = np.arange(w)[None, :]
    return np.minimum(np.minimum(i, h - 1 - i), np.minimum(j, w - 1 - j))


def pojasevi(h: int, w: int, cfg=None) -> np.ndarray:
    """Мапа појасева (H, W) са ознакама SPOLJASNJI_CENAR … POLJE.

    Дебљине се задају као удео половине краће странице, па распоред остаје исти
    без обзира на величину и однос страница.
    """
    spoljni = 0.04 if cfg is None else cfg.spoljasnji_cenar
    bordura = 0.14 if cfg is None else cfg.bordura
    unutrasnji = 0.05 if cfg is None else cfg.unutrasnji_cenar
    if min(spoljni, bordura, unutrasnji) < 0:
        raise ValueError("Дебљина појаса не може бити негативна")
    if spoljni + bordura + unutrasnji >= 1.0:
        raise ValueError("Појасеви заузимају цео ћилим — не остаје поље")

    pola = max(min(h, w) / 2.0, 1e-9)
    t = _udaljenost_od_ivice(h, w) / pola

    mapa = np.full((h, w), POLJE, dtype=np.int8)
    mapa[t < spoljni + bordura + unutrasnji] = UNUTRASNJI_CENAR
    mapa[t < spoljni + bordura] = BORDURA
    mapa[t < spoljni] = SPOLJASNJI_CENAR
    return mapa


def ogledaj(a, uspravno: bool = True, vodoravno: bool = True) -> np.ndarray:
    """Наметни огледалску симетрију: леву половину пресликај на десну (и горњу на доњу).

    Ради и за непаран број редова/колона — средња линија остаје као што јесте.
    """
    a = np.asarray(a)
    if a.ndim < 2:
        raise ValueError("Очекиван је бар дводимензионалан низ")
    if uspravno:
        w = a.shape[1]
        levo = a[:, : (w + 1) // 2]
        a = np.concatenate([levo, np.flip(levo[:, : w // 2], axis=1)], axis=1)
    if vodoravno:
        h = a.shape[0]
        gore = a[: (h + 1) // 2]
        a = np.concatenate([gore, np.flip(gore[: h // 2], axis=0)], axis=0)
    return a


def duzine_poteza(red) -> np.ndarray:
    """Дужине узастопних потеза исте боје у једном реду.

    Потез је оно што ткаља отка у једном маху. Кратки потези нису грешка сами по
    себи, али их много значи спор рад и, испод неке границе, шару коју разбој не
    може да изведе.
    """
    red = np.asarray(red).ravel()
    if red.size == 0:
        return np.array([], dtype=np.int64)
    granice = np.flatnonzero(np.diff(red)) + 1
    ivice = np.concatenate(([0], granice, [red.size]))
    return np.diff(ivice)


@dataclass
class Izvestaj:
    """Шта разбој каже о предложеној шари."""

    poteza: int
    kratkih: int
    najkraci: int
    promena_po_redu: float
    crvena_preovladjuje: bool
    min_niti: int

    @property
    def udeo_kratkih(self) -> float:
        return self.kratkih / self.poteza if self.poteza else 0.0

    def izvodljivo(self, prag: float = 0.05) -> bool:
        """Изводљиво ако кратких потеза има мање од `prag` од укупног броја."""
        return self.udeo_kratkih < prag

    def __str__(self) -> str:
        ocena = "изводљиво" if self.izvodljivo() else "ТЕШКО ИЗВОДЉИВО"
        return (
            f"{ocena}: {self.poteza} потеза, кратких (< {self.min_niti} нити) "
            f"{self.kratkih} ({self.udeo_kratkih:.1%}), најкраћи {self.najkraci}, "
            f"промена боје по реду {self.promena_po_redu:.1f}, "
            f"црвена преовлађује: {'да' if self.crvena_preovladjuje else 'не'}"
        )


def proveri(indeksi, min_niti: int = 3, paleta=pal.PALETA) -> Izvestaj:
    """Провера изводљивости на разбоју, ред по ред."""
    idx = np.asarray(indeksi)
    if idx.ndim != 2:
        raise ValueError(f"Очекивана мрежа (H, W), добијено: {idx.shape}")
    if min_niti < 1:
        raise ValueError("min_niti мора бити бар 1")

    sve = [duzine_poteza(red) for red in idx]
    duzine = np.concatenate(sve) if sve else np.array([], dtype=np.int64)
    poteza = int(duzine.size)
    return Izvestaj(
        poteza=poteza,
        kratkih=int((duzine < min_niti).sum()),
        najkraci=int(duzine.min()) if poteza else 0,
        promena_po_redu=float(np.mean([max(len(r) - 1, 0) for r in sve])) if sve else 0.0,
        crvena_preovladjuje=pal.crvena_preovladjuje(idx, paleta),
        min_niti=min_niti,
    )


def ujednaci_poteze(indeksi, min_niti: int = 3) -> np.ndarray:
    """Прогутај потезе краће од `min_niti` — припоји их суседном, дужем потезу.

    Груб поступак, али ради оно што ткаља ионако ради руком: ситну мрљу коју је
    модел оставио замени оним што је око ње. Понавља се док има шта да се гута,
    јер спајањем два потеза може настати нови кратак сусед.
    """
    idx = np.array(indeksi, dtype=np.int16, copy=True)
    if idx.ndim != 2:
        raise ValueError(f"Очекивана мрежа (H, W), добијено: {idx.shape}")

    for r in range(idx.shape[0]):
        red = idx[r]
        while True:
            duzine = duzine_poteza(red)
            if duzine.size <= 1 or duzine.min() >= min_niti:
                break
            pocetci = np.concatenate(([0], np.cumsum(duzine)[:-1]))
            k = int(np.argmin(duzine))
            # припој суседу који је дужи; на крајевима постоји само један сусед
            levo = duzine[k - 1] if k > 0 else -1
            desno = duzine[k + 1] if k + 1 < duzine.size else -1
            sused = k - 1 if levo >= desno else k + 1
            red[pocetci[k] : pocetci[k] + duzine[k]] = red[pocetci[sused]]
    return idx


def ujednaci_simetricno(indeksi, min_niti: int = 3, uspravno: bool = True,
                        vodoravno: bool = True) -> np.ndarray:
    """Поравнај потезе тако да симетрија преживи.

    Ово није исто што и `ujednaci_poteze` па `ogledaj`, ни обрнуто — оба та
    редоследа су погрешна:

    - Поравнање после огледања иде слева надесно и разбија симетрију коју је
      огледање управо наметнуло.
    - Огледање после поравнања пресеца потез који лежи преко средишње линије и
      задржи само његову леву половину, па је удвостручи. Потез дужине 1 у левој
      половини тако даје потез дужине 2 — испод прага, иако је пре огледања био
      довољно дуг.

    Решење је да се поравна **само лева половина**, па да се она огледа. Потези
    унутар половине остају какви јесу, а онај на средишњој линији се удвостручи
    — дакле само продужи. Тако оба својства важе истовремено.
    """
    idx = np.asarray(indeksi)
    if idx.ndim != 2:
        raise ValueError(f"Очекивана мрежа (H, W), добијено: {idx.shape}")

    if not uspravno:
        return ogledaj(ujednaci_poteze(idx, min_niti), uspravno=False, vodoravno=vodoravno)

    w = idx.shape[1]
    leva = ujednaci_poteze(idx[:, : (w + 1) // 2], min_niti)
    spojeno = np.concatenate([leva, np.flip(leva[:, : w // 2], axis=1)], axis=1)
    # огледање по редовима не дира потезе унутар реда, па иде без бојазни
    return ogledaj(spojeno, uspravno=False, vodoravno=vodoravno)


def primeni(slika, cfg=None, paleta=pal.PALETA) -> np.ndarray:
    """Цео пут: слика → индекси палете → симетрија и поравнати потези.

    Појасеви се овде не цртају — они су посао генератора, који зна шта иде у
    поље а шта у бордуру. Овде се намеће само оно што важи за целу површину.
    """
    min_niti = 3 if cfg is None else cfg.min_niti
    uspravno = True if cfg is None else cfg.ogledalo_uspravno
    vodoravno = True if cfg is None else cfg.ogledalo_vodoravno

    idx = pal.kvantizuj(slika, paleta)
    return ujednaci_simetricno(idx, min_niti, uspravno, vodoravno)
