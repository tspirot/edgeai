"""Лажни VLM — детерминистичан опис слике и питања, без модела.

Не „разуме" слику; описује њене основне особине (величина, светлина, боја) и
понови питање и приложене материјале. Довољно да се проба цео ланац и да
тестови имају предвидив излаз.
"""

from __future__ import annotations

import numpy as np

from asistent.vlm.base import Answer, VlmBackend


def _opis_slike(image: "np.ndarray | None") -> str:
    if image is None:
        return "Слика није приложена."
    arr = np.asarray(image)
    if arr.ndim != 3:
        return f"Слика чудног облика: {arr.shape}."
    h, w = arr.shape[:2]
    svetlina = float(arr.mean())
    stanje = "тамна" if svetlina < 85 else "светла" if svetlina > 170 else "средње осветљена"
    return f"Слика {w}×{h}, {stanje} (просечна светлина {svetlina:.0f}/255)."


class DummyVlm(VlmBackend):
    def __init__(self, vlm_cfg=None) -> None:
        self.cfg = vlm_cfg

    def answer(self, image, question, context=None) -> Answer:
        context = context or []
        delovi = [
            f"(демо одговор) {_opis_slike(image)}",
            f"Питање је било: „{question.strip()}“.",
        ]
        if context:
            delovi.append(f"Ослонац у материјалима: {len(context)} исечак(а).")
            delovi.append(context[0].strip()[:160])
        else:
            delovi.append("Материјали нису коришћени (RAG искључен или нема поготка).")
        return Answer(text=" ".join(delovi), used_context=list(context), latency_ms=0.0)
