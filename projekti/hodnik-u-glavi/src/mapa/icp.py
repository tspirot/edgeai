"""Iterative Closest Point — поравнање два 2D облака тачака.

Нема спољних зависности осим NumPy. Сваку итерацију: за сваку тачку извора
нађи најближу тачку циља, израчунај најбоље крутo померање (ротација + транслација)
затвореном формулом (Umeyama/Kabsch у 2D), примени, понови.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from mapa.pose import Pose, from_matrix


@dataclass
class IcpResult:
    pose: Pose            # померање које извор доводи на циљ
    fitness: float        # удео упарених тачака (0..1)
    rmse: float           # корен средње квадратне грешке упарених парова (m)
    iterations: int
    converged: bool


def _nearest(src: np.ndarray, dst: np.ndarray):
    """За сваку тачку `src` индекс најближе у `dst` и растојање (брутална сила).

    Ради са квадратом растојања (без sqrt) док не изабере најближу.
    """
    diff = src[:, None, :] - dst[None, :, :]
    d2 = np.einsum("ijk,ijk->ij", diff, diff)
    idx = np.argmin(d2, axis=1)
    return idx, np.sqrt(d2[np.arange(len(src)), idx])


def _best_rigid_transform(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Крутo померање (3x3) које `a` најбоље доводи на `b` (упарене тачке)."""
    ca, cb = a.mean(axis=0), b.mean(axis=0)
    h = (a - ca).T @ (b - cb)
    u, _, vt = np.linalg.svd(h)
    r = vt.T @ u.T
    if np.linalg.det(r) < 0:            # спречи рефлексију
        vt[-1, :] *= -1
        r = vt.T @ u.T
    t = cb - r @ ca
    m = np.eye(3)
    m[:2, :2] = r
    m[:2, 2] = t
    return m


def icp(
    source: np.ndarray,
    target: np.ndarray,
    init: "Pose | None" = None,
    max_iter: int = 30,
    tol: float = 1e-4,
    max_pairs_dist: float = 0.5,
) -> IcpResult:
    src0 = np.asarray(source, dtype=float)
    dst = np.asarray(target, dtype=float)
    if len(src0) < 3 or len(dst) < 3:
        return IcpResult(init or Pose(), 0.0, float("inf"), 0, False)

    total = (init or Pose()).as_matrix()
    src = _apply(total, src0)
    converged = False
    it = 0
    rmse = float("inf")
    fitness = 0.0

    for it in range(1, max_iter + 1):
        idx, dists = _nearest(src, dst)
        keep = dists < max_pairs_dist
        fitness = float(keep.mean())
        if keep.sum() < 3:
            break
        a, b = src[keep], dst[idx[keep]]
        step = _best_rigid_transform(a, b)
        total = step @ total
        src = _apply(total, src0)

        rmse = float(np.sqrt(np.mean(np.sum((_apply(step, a) - b) ** 2, axis=1))))
        shift = np.linalg.norm(step[:2, 2])
        if shift < tol:
            converged = True
            break

    return IcpResult(from_matrix(total), fitness, rmse, it, converged)


def _apply(m: np.ndarray, pts: np.ndarray) -> np.ndarray:
    return pts @ m[:2, :2].T + m[:2, 2]
