"""Издвајање силуете: шта је предмет, а шта позадина.

Најпростији метод који ради: сними празну позадину, па одузми. Где се слика
довољно разликује од празне — ту је предмет. Нема мреже, нема обуке, има праг
који ученик види и може да помери.

Зато позадина мора бити једнобојна и **матирана**: сјајна даје одсјај који се
мења кад се сто заврти, па одузимање пријави одсјај као део предмета.
"""

from __future__ import annotations

import numpy as np


def _u_sivo(slika) -> np.ndarray:
    a = np.asarray(slika, dtype=np.float64)
    if a.ndim == 3:
        return a[:, :, :3].mean(axis=2)
    if a.ndim == 2:
        return a
    raise ValueError(f"Очекивана слика (H, W) или (H, W, 3), добијено: {a.shape}")


def _pomeri_ili(m: np.ndarray) -> np.ndarray:
    """Унија маске са њена четири суседа — једно ширење."""
    out = m.copy()
    out[1:, :] |= m[:-1, :]
    out[:-1, :] |= m[1:, :]
    out[:, 1:] |= m[:, :-1]
    out[:, :-1] |= m[:, 1:]
    return out


def dilatiraj(m, puta: int = 1) -> np.ndarray:
    out = np.asarray(m, dtype=bool)
    for _ in range(int(puta)):
        out = _pomeri_ili(out)
    return out


def erodiraj(m, puta: int = 1) -> np.ndarray:
    """Ерозија је ширење допуне — исти поступак, обрнута маска."""
    return ~dilatiraj(~np.asarray(m, dtype=bool), puta)


def zatvori(m, puta: int = 1) -> np.ndarray:
    """Затварање: залепи ситне прекиде у ивици, а не надува облик."""
    return erodiraj(dilatiraj(m, puta), puta)


def popuni_rupe(m, maks_koraka: int = 4000) -> np.ndarray:
    """Попуни шупљине које не додирују ивицу слике.

    Спољашњост се шири од ивице кроз празно; шта остане недостигнуто — рупа је
    унутар предмета и припада силуети. Без овога резбарење издуби предмет
    изнутра због сваке рупице у маски.
    """
    m = np.asarray(m, dtype=bool)
    if m.ndim != 2:
        raise ValueError(f"Очекивана маска (H, W), добијено: {m.shape}")

    spolja = np.zeros_like(m)
    spolja[0, :] = spolja[-1, :] = True
    spolja[:, 0] = spolja[:, -1] = True
    spolja &= ~m

    for _ in range(int(maks_koraka)):
        novo = _pomeri_ili(spolja) & ~m
        if np.array_equal(novo, spolja):
            break
        spolja = novo
    return ~spolja


def najveca_celina(m) -> np.ndarray:
    """Задржи само највећу повезану област — предмет, не мрву поред њега."""
    m = np.asarray(m, dtype=bool)
    ostatak = m.copy()
    najbolja = np.zeros_like(m)
    najveca = 0
    while ostatak.any():
        seme = np.zeros_like(m)
        i, j = np.argwhere(ostatak)[0]
        seme[i, j] = True
        while True:
            novo = _pomeri_ili(seme) & m
            if np.array_equal(novo, seme):
                break
            seme = novo
        koliko = int(seme.sum())
        if koliko > najveca:
            najveca, najbolja = koliko, seme
        ostatak &= ~seme
    return najbolja


def silueta(slika, pozadina, prag: float = 18.0, zatvaranje: int = 2,
            samo_najveca: bool = True) -> np.ndarray:
    """Кадар + празна позадина → булова маска предмета.

    `prag` је у јединицама сиве (0–255). Прениско: шум и сенке улазе у предмет.
    Превисоко: тамни делови предмета испадну и резбарење их одсече.
    """
    a, b = _u_sivo(slika), _u_sivo(pozadina)
    if a.shape != b.shape:
        raise ValueError(f"Кадар {a.shape} и позадина {b.shape} нису исте величине")
    if prag <= 0:
        raise ValueError("Праг мора бити позитиван")

    m = np.abs(a - b) > float(prag)
    if zatvaranje:
        m = zatvori(m, zatvaranje)
    if samo_najveca and m.any():
        m = najveca_celina(m)
    return popuni_rupe(m)


def udeo_kadra(m) -> float:
    """Колики део слике заузима силуета — за упозорење да предмет бежи из кадра."""
    m = np.asarray(m, dtype=bool)
    return float(m.sum()) / max(m.size, 1)


def dodiruje_ivicu(m) -> bool:
    """Предмет који додирује ивицу слике је исечен — резбарење ће га одсећи."""
    m = np.asarray(m, dtype=bool)
    if not m.any():
        return False
    return bool(m[0, :].any() or m[-1, :].any() or m[:, 0].any() or m[:, -1].any())
