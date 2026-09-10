"""Камера као математика: од тачке у простору до пиксела.

Овде нема ниједног модела нити обуке — само пројективна геометрија. Цео
пројекат стоји на томе да се положај камере **зна**, а не процењује: предмет је
на окретном столу који се врти за наређени угао, па је довољно завртети тачке
око усправне осе и пројектовати их кроз непомичну камеру.

Координатни систем света: `z` је увис, оса стола пролази кроз координатни
почетак, а сто лежи у равни `z = 0`.

Координатни систем камере (као у OpenCV-у): `x` десно, `y` наниже, `z` напред.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

USPRAVNO = np.array([0.0, 0.0, 1.0])


def rotacija_z(ugao_stepeni: float) -> np.ndarray:
    """Заокрет око усправне осе — оно што окретни сто ради предмету."""
    a = np.radians(float(ugao_stepeni))
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


@dataclass
class Kamera:
    """Непомична камера која гледа у осу стола.

    Све дужине су у милиметрима — исто мерило у ком се на крају штампа.
    """

    sirina: int = 640                 # пиксела
    visina: int = 480
    vfov: float = 42.0                # усправно видно поље, степени
    rastojanje: float = 300.0         # од осе стола до камере
    visina_kamere: float = 220.0      # изнад површине стола
    cilj: float = 60.0                # висина тачке у коју камера гледа, на оси

    def __post_init__(self) -> None:
        if self.sirina < 2 or self.visina < 2:
            raise ValueError("Слика мора имати бар 2×2 пиксела")
        if not 1.0 < self.vfov < 179.0:
            raise ValueError(f"Видно поље ван смисла: {self.vfov}°")
        if self.rastojanje <= 0:
            raise ValueError("Камера мора бити на позитивном растојању од осе")

    # --- унутрашњи параметри ---------------------------------------------

    @property
    def fy(self) -> float:
        return (self.visina / 2.0) / np.tan(np.radians(self.vfov) / 2.0)

    @property
    def fx(self) -> float:
        return self.fy            # квадратни пиксели

    @property
    def cx(self) -> float:
        return self.sirina / 2.0

    @property
    def cy(self) -> float:
        return self.visina / 2.0

    # --- спољашњи параметри ----------------------------------------------

    @property
    def polozaj(self) -> np.ndarray:
        return np.array([self.rastojanje, 0.0, self.visina_kamere])

    @property
    def rotacija(self) -> np.ndarray:
        """Редови су осе камере у свету: десно, наниже, напред."""
        napred = np.array([0.0, 0.0, self.cilj]) - self.polozaj
        napred = napred / np.linalg.norm(napred)
        desno = np.cross(napred, USPRAVNO)
        n = np.linalg.norm(desno)
        if n < 1e-9:  # pragma: no cover — камера тачно изнад осе
            raise ValueError("Камера не сме да гледа право надоле низ осу стола")
        desno = desno / n
        nanize = np.cross(napred, desno)
        return np.stack([desno, nanize, napred])

    # --- пројекција -------------------------------------------------------

    def projektuj(self, tacke) -> tuple:
        """Тачке света (N, 3) → (u, v, dubina).

        `dubina` је растојање дуж осе гледања; негативна значи иза камере, што
        се увек мора одбацити — иначе тачке иза леђа „падну“ у слику.
        """
        P = np.asarray(tacke, dtype=np.float64)
        if P.ndim != 2 or P.shape[1] != 3:
            raise ValueError(f"Очекивано (N, 3), добијено: {P.shape}")

        u_kameri = (P - self.polozaj) @ self.rotacija.T
        dubina = u_kameri[:, 2]
        bezbedna = np.where(np.abs(dubina) < 1e-9, 1e-9, dubina)
        u = self.fx * u_kameri[:, 0] / bezbedna + self.cx
        v = self.fy * u_kameri[:, 1] / bezbedna + self.cy
        return u, v, dubina

    def u_kadru(self, u, v, dubina) -> np.ndarray:
        """Које тачке заиста падају у слику, испред камере."""
        return (
            (dubina > 0)
            & (u >= 0) & (u < self.sirina)
            & (v >= 0) & (v < self.visina)
        )


def resetka(granice, podela) -> tuple:
    """Средишта воксела у радном простору.

    `granice` = (xmin, xmax, ymin, ymax, zmin, zmax) у mm,
    `podela` = (nx, ny, nz). Враћа (центри облика (nx, ny, nz, 3), корак).
    """
    xmin, xmax, ymin, ymax, zmin, zmax = (float(g) for g in granice)
    nx, ny, nz = (int(n) for n in podela)
    if min(nx, ny, nz) < 1:
        raise ValueError("Подела мора бити бар 1 по оси")
    if xmax <= xmin or ymax <= ymin or zmax <= zmin:
        raise ValueError(f"Границе радног простора нису растуће: {granice}")

    def osa(lo, hi, n):
        korak = (hi - lo) / n
        return lo + korak * (np.arange(n) + 0.5), korak

    x, kx = osa(xmin, xmax, nx)
    y, ky = osa(ymin, ymax, ny)
    z, kz = osa(zmin, zmax, nz)
    centri = np.stack(np.meshgrid(x, y, z, indexing="ij"), axis=-1)
    return centri, (kx, ky, kz)
