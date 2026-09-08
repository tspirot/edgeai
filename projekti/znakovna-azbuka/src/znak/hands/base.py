from __future__ import annotations


class HandDetector:
    def detect(self, frame):  # pragma: no cover - интерфејс
        """Врати (21, 2) тачке шаке у пикселима, или None ако шаке нема."""
        raise NotImplementedError

    def close(self) -> None:
        pass
