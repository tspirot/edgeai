"""Картон за ткање — превод шаре у нешто што се чита за разбојем.

Слика није упутство. Ткаљи треба мрежа: колико нити које боје иде у сваки ред.
Овде се шара са пуном резолуцијом своди на мрежу ћелија, а свака ћелија добија
боју већине — исто што рука ионако ради кад „заокружи“ ситан детаљ.

Мера која нешто значи: **број промена боје по реду**. То је оно што кошта време
за разбојем, а не површина шаре.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from cilim import paleta as pal
from cilim.pravila import duzine_poteza


def _vecina(blok: np.ndarray, n_boja: int) -> int:
    return int(np.bincount(blok.ravel(), minlength=n_boja).argmax())


@dataclass
class Karton:
    """Мрежа за ткање: у свакој ћелији индекс боје из палете."""

    mreza: np.ndarray          # (redova, kolona), индекси палете
    paleta: tuple = pal.PALETA
    niti_po_celiji: int = 2    # колико нити потке чини једну ћелију

    @property
    def redova(self) -> int:
        return int(self.mreza.shape[0])

    @property
    def kolona(self) -> int:
        return int(self.mreza.shape[1])

    # --- прављење ---------------------------------------------------------

    @classmethod
    def iz_indeksa(cls, indeksi, redova: int, kolona: int, paleta=pal.PALETA, **kw) -> "Karton":
        """Сведи мрежу индекса пуне резолуције на `redova` × `kolona` ћелија."""
        idx = np.asarray(indeksi)
        if idx.ndim != 2:
            raise ValueError(f"Очекивана мрежа (H, W), добијено: {idx.shape}")
        if redova < 1 or kolona < 1:
            raise ValueError("Картон мора имати бар један ред и једну колону")
        h, w = idx.shape
        if redova > h or kolona > w:
            raise ValueError(
                f"Картон {redova}×{kolona} је гушћи од саме шаре {h}×{w} — "
                "нема се шта сажети"
            )

        granice_r = np.linspace(0, h, redova + 1).astype(int)
        granice_k = np.linspace(0, w, kolona + 1).astype(int)
        out = np.zeros((redova, kolona), dtype=np.int16)
        for r in range(redova):
            for k in range(kolona):
                blok = idx[granice_r[r] : granice_r[r + 1], granice_k[k] : granice_k[k + 1]]
                out[r, k] = _vecina(blok, len(paleta))
        return cls(mreza=out, paleta=paleta, **kw)

    # --- читање -----------------------------------------------------------

    def legenda(self) -> list:
        """Само боје које се стварно појављују, са бројем ћелија."""
        broj = np.bincount(self.mreza.ravel(), minlength=len(self.paleta))
        return [
            {"indeks": i, "id": b.id, "naziv": b.naziv, "celija": int(broj[i])}
            for i, b in enumerate(self.paleta)
            if broj[i] > 0
        ]

    def promene_po_redu(self) -> np.ndarray:
        """Колико пута се боја мења у сваком реду — цена рада за разбојем."""
        return np.array([max(len(duzine_poteza(red)) - 1, 0) for red in self.mreza])

    def rezime(self) -> str:
        promene = self.promene_po_redu()
        redovi = [
            f"Картон: {self.redova} редова × {self.kolona} колона "
            f"({self.niti_po_celiji} нити по ћелији → "
            f"{self.redova * self.niti_po_celiji} нити потке)",
            f"Промена боје по реду: просек {promene.mean():.1f}, највише {promene.max()}",
            "Боје:",
        ]
        ukupno = self.redova * self.kolona
        for s in self.legenda():
            redovi.append(f"  {s['indeks']}  {s['naziv']:<18} {s['celija']:>6} ћелија "
                          f"({s['celija'] / ukupno:.1%})")
        return "\n".join(redovi)

    # --- извоз ------------------------------------------------------------

    def u_csv(self, putanja) -> Path:
        """CSV са индексима боја; легенда иде у коментаре изнад мреже."""
        p = Path(putanja)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            f.write(f"# картон за ткање, {self.redova}×{self.kolona} ћелија, "
                    f"{self.niti_po_celiji} нити по ћелији\n")
            for s in self.legenda():
                f.write(f"# {s['indeks']} = {s['naziv']} ({s['celija']} ћелија)\n")
            csv.writer(f).writerows(self.mreza.tolist())
        return p

    def u_png(self, putanja, piksela_po_celiji: int = 12, mreza_linije: bool = True) -> Path:
        """Слика картона за штампу — ћелије са мрежом, да се броји прстом."""
        from PIL import Image

        p = Path(putanja)
        p.parent.mkdir(parents=True, exist_ok=True)
        boje = pal.u_sliku(self.mreza, self.paleta)
        slika = np.repeat(np.repeat(boje, piksela_po_celiji, axis=0), piksela_po_celiji, axis=1)
        if mreza_linije and piksela_po_celiji >= 4:
            siva = np.array([120, 120, 120], dtype=np.uint8)
            slika[::piksela_po_celiji, :] = siva
            slika[:, ::piksela_po_celiji] = siva
            # свака пета линија тамнија — да се редови броје у групама
            slika[:: piksela_po_celiji * 5, :] = np.array([40, 40, 40], dtype=np.uint8)
            slika[:, :: piksela_po_celiji * 5] = np.array([40, 40, 40], dtype=np.uint8)
        Image.fromarray(slika, mode="RGB").save(p)
        return p
