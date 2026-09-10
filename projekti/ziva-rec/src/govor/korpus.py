"""Корпус — оно што станица заправо производи.

Није бот, него збирка поравнатих парова: исечак снимка + исправљен препис + ко
је говорио и да ли је дао сагласност. После неколико стотина парова, Whisper се
дообучи на њима.

Приватност: снимак остаје на уређају док говорник не одобри. Одобрење је
експлицитно поље, а извоз (`za_doobuku`) прескаче све што није одобрено.

На диску:
    korpus/
      meta.json            — говорници, сесије
      unosi/000123.json     — један пар (текст, границе, ознаке)
      isecci/000123.wav     — исечак звука тог пара
"""

from __future__ import annotations

import json
import wave
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def _sada() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class Govornik:
    id: str
    inicijali: str            # не пуно име — „М. Ј.“
    selo: str = ""
    godiste: str = ""         # „193x“ или деценија — не тачан датум
    saglasnost: bool = False
    beleska: str = ""

    def __post_init__(self):
        if not self.id or not self.inicijali:
            raise ValueError("Говорник мора имати id и иницијале")


@dataclass
class Unos:
    id: str
    govornik_id: str
    tekst_asr: str            # шта је модел чуо (обично лоше)
    tekst_ispravljen: str     # шта је говорник рекао да је тачно
    pocetak: float            # секунде у оригиналном снимку
    kraj: float
    samplerate: int
    skor_torlacnosti: float = 0.0
    crte: dict = field(default_factory=dict)   # id црте → колико пута
    odobreno: bool = False
    napravljen: str = field(default_factory=_sada)

    @property
    def trajanje(self) -> float:
        return self.kraj - self.pocetak

    @property
    def ispravljan(self) -> bool:
        return self.tekst_asr.strip() != self.tekst_ispravljen.strip()


class Korpus:
    def __init__(self, koren) -> None:
        self.koren = Path(koren)
        self.unosi_dir = self.koren / "unosi"
        self.isecci_dir = self.koren / "isecci"
        self._meta_put = self.koren / "meta.json"
        self.govornici: dict = {}
        self._ucitaj_meta()

    # --- метаподаци ------------------------------------------------------

    def _ucitaj_meta(self) -> None:
        if self._meta_put.exists():
            podaci = json.loads(self._meta_put.read_text(encoding="utf-8"))
            self.govornici = {
                g["id"]: Govornik(**g) for g in podaci.get("govornici", [])
            }

    def _upisi_meta(self) -> None:
        self.koren.mkdir(parents=True, exist_ok=True)
        self._meta_put.write_text(
            json.dumps(
                {"govornici": [asdict(g) for g in self.govornici.values()]},
                ensure_ascii=False, indent=2,
            ),
            encoding="utf-8",
        )

    def dodaj_govornika(self, govornik: Govornik) -> None:
        self.govornici[govornik.id] = govornik
        self._upisi_meta()

    # --- уноси ----------------------------------------------------------

    def _sledeci_id(self) -> str:
        postojeci = sorted(self.unosi_dir.glob("*.json")) if self.unosi_dir.exists() else []
        n = int(postojeci[-1].stem) + 1 if postojeci else 0
        return f"{n:06d}"

    def dodaj_unos(self, unos: Unos, isecak: np.ndarray) -> Path:
        if unos.govornik_id not in self.govornici:
            raise ValueError(
                f"Говорник '{unos.govornik_id}' није у корпусу — прво dodaj_govornika()"
            )
        self.unosi_dir.mkdir(parents=True, exist_ok=True)
        self.isecci_dir.mkdir(parents=True, exist_ok=True)

        put = self.unosi_dir / f"{unos.id}.json"
        put.write_text(json.dumps(asdict(unos), ensure_ascii=False, indent=2),
                       encoding="utf-8")
        upisi_wav(self.isecci_dir / f"{unos.id}.wav", isecak, unos.samplerate)
        return put

    def unosi(self) -> list:
        if not self.unosi_dir.exists():
            return []
        out = []
        for put in sorted(self.unosi_dir.glob("*.json")):
            out.append(Unos(**json.loads(put.read_text(encoding="utf-8"))))
        return out

    def odobri(self, unos_id: str, odobreno: bool = True) -> None:
        put = self.unosi_dir / f"{unos_id}.json"
        if not put.exists():
            raise KeyError(f"Нема уноса '{unos_id}'")
        podaci = json.loads(put.read_text(encoding="utf-8"))
        podaci["odobreno"] = bool(odobreno)
        put.write_text(json.dumps(podaci, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- преглед и извоз ----------------------------------------------

    def rezime(self) -> dict:
        u = self.unosi()
        odobrenih = [x for x in u if x.odobreno]
        return {
            "unosa": len(u),
            "odobrenih": len(odobrenih),
            "ispravljanih": sum(1 for x in u if x.ispravljan),
            "govornika": len(self.govornici),
            "sa_saglasnoscu": sum(1 for g in self.govornici.values() if g.saglasnost),
            "sati_zvuka": round(sum(x.trajanje for x in u) / 3600, 2),
            "sati_odobreno": round(sum(x.trajanje for x in odobrenih) / 3600, 2),
            "prosecan_skor": round(
                sum(x.skor_torlacnosti for x in u) / len(u), 3) if u else 0.0,
        }

    def za_doobuku(self) -> list:
        """Парови (put_do_wav, tekst) — само одобрени и само са сагласношћу.

        Ово је једина капија ка тренингу. Све што овде не прође, не постоји за
        модел.
        """
        out = []
        for u in self.unosi():
            if not u.odobreno:
                continue
            g = self.govornici.get(u.govornik_id)
            if g is None or not g.saglasnost:
                continue
            wav = self.isecci_dir / f"{u.id}.wav"
            if wav.exists():
                out.append((wav, u.tekst_ispravljen))
        return out


# --- WAV, без зависности ------------------------------------------------

def upisi_wav(putanja, audio, samplerate: int) -> Path:
    a = np.asarray(audio, dtype=np.float32)
    if a.ndim > 1:
        a = a.mean(axis=1)
    pcm = np.clip(a, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype("<i2")

    p = Path(putanja)
    p.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(int(samplerate))
        w.writeframes(pcm.tobytes())
    return p


def ucitaj_wav(putanja) -> tuple:
    with wave.open(str(putanja), "rb") as w:
        if w.getsampwidth() != 2:
            raise ValueError("Очекиван 16-битни WAV")
        okvira = w.getnframes()
        podaci = np.frombuffer(w.readframes(okvira), dtype="<i2")
        kanali = w.getnchannels()
        if kanali > 1:
            podaci = podaci.reshape(-1, kanali).mean(axis=1)
        return podaci.astype(np.float32) / 32768.0, w.getframerate()
