"""„Скрининг“ извештај — асиметрија рамена/кукова кроз недеље.

Систем ништа не тврди. Даје бројке кроз време и обележи оне који стално прелазе
праг — да их човек погледа. Извештај се носи школском лекару.
"""

from __future__ import annotations

from statistics import mean, pstdev


def summarize(rows: list, flag_deg: float) -> dict:
    """rows: листа {'date','shoulder_tilt','hip_tilt'} (стрингови из CSV-а)."""
    if not rows:
        return {"n": 0, "flagged": False, "note": "нема података"}

    sh = [float(r["shoulder_tilt"]) for r in rows]
    hp = [float(r["hip_tilt"]) for r in rows]

    def block(vals):
        m = mean(vals)
        return {
            "mean": round(m, 2),
            "abs_mean": round(mean(abs(v) for v in vals), 2),
            "std": round(pstdev(vals), 2) if len(vals) > 1 else 0.0,
            "n_over": sum(1 for v in vals if abs(v) > flag_deg),
        }

    sb, hb = block(sh), block(hp)
    # обележи ако већина мерења прелази праг И увек на исту страну (доследан знак)
    consistent = (
        (sb["n_over"] >= 0.6 * len(sh) and _same_sign(sh))
        or (hb["n_over"] >= 0.6 * len(hp) and _same_sign(hp))
    )
    return {
        "n": len(rows),
        "period": f"{rows[0]['date']} … {rows[-1]['date']}",
        "shoulder": sb,
        "hip": hb,
        "flagged": bool(consistent),
        "note": (
            "Доследна асиметрија изнад прага — показати школском лекару. Ово није дијагноза."
            if consistent else
            "Нема доследног одступања. Ово није дијагноза ни потврда здравља."
        ),
    }


def _same_sign(vals) -> bool:
    pos = sum(1 for v in vals if v > 0)
    neg = sum(1 for v in vals if v < 0)
    return max(pos, neg) >= 0.8 * len(vals)
