"""Командна линија: `govor oceni | preslusaj | prepisi | ispravi | korpus | recnik | devices`."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from govor import OGRADA, __version__
from govor.config import load_config

log = logging.getLogger("govor")


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="govor",
        description="Жива реч — теренска станица за пиротски говор, на самом уређају",
        epilog=OGRADA,
    )
    p.add_argument("--version", action="version", version=f"govor {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    oc = sub.add_parser("oceni", help="Оцени торлачност реченице (текст, без звука)")
    oc.add_argument("recenica", nargs="+")
    oc.add_argument("-c", "--config")
    oc.add_argument("-v", "--verbose", action="store_true")

    pr = sub.add_parser("prepisi", help="WAV → препис + оцена по сегменту")
    pr.add_argument("wav")
    pr.add_argument("-c", "--config")
    pr.add_argument("--asr", choices=["faster-whisper", "dummy"])
    pr.add_argument("--govornik", default="nepoznat")
    pr.add_argument("-v", "--verbose", action="store_true")

    isp = sub.add_parser("ispravi", help="Препиши, па упиши исправке у корпус")
    isp.add_argument("wav")
    isp.add_argument("-c", "--config")
    isp.add_argument("--asr", choices=["faster-whisper", "dummy"])
    isp.add_argument("--govornik", required=True, help="id говорника из корпуса")
    isp.add_argument("--samo-istaknute", action="store_true",
                     help="понуди само сегменте изнад прага торлачности")
    isp.add_argument("-v", "--verbose", action="store_true")

    ko = sub.add_parser("korpus", help="Стање корпуса и извоз за дообуку")
    ko.add_argument("-c", "--config")
    ko_sub = ko.add_subparsers(dest="korpus_cmd", required=True)
    ko_sub.add_parser("stanje", help="Бројке")
    dodaj = ko_sub.add_parser("govornik", help="Додај говорника")
    dodaj.add_argument("id")
    dodaj.add_argument("--inicijali", required=True)
    dodaj.add_argument("--selo", default="")
    dodaj.add_argument("--godiste", default="")
    dodaj.add_argument("--saglasnost", action="store_true")
    od = ko_sub.add_parser("odobri", help="Означи унос као одобрен")
    od.add_argument("unos_id")
    od.add_argument("--ponisti", action="store_true")
    izv = ko_sub.add_parser("izvoz", help="Списак (wav, текст) за дообуку")
    izv.add_argument("-o", "--out", help="упиши као TSV (иначе испис)")

    re = sub.add_parser("recnik", help="Речник: колико одредница и шта је потврђено")
    re.add_argument("-c", "--config")
    re.add_argument("--sve", action="store_true")

    sub.add_parser("devices", help="Прикажи микрофоне")

    dm = sub.add_parser("download-model", help="Преузми Whisper унапред (тражи интернет)")
    dm.add_argument("-c", "--config")
    return p


def _nivo(cfg, args) -> None:
    logging.getLogger().setLevel(
        logging.DEBUG if getattr(args, "verbose", False) else cfg.log_level
    )


# --- команде -----------------------------------------------------------

def cmd_oceni(args) -> int:
    cfg = load_config(args.config)
    _nivo(cfg, args)
    from govor import crte
    from govor import recnik as recnik_mod

    recnik = recnik_mod.ucitaj(cfg.recnik or None)
    nalaz = crte.oceni(" ".join(args.recenica), recnik)

    print(nalaz.sazetak())
    for rec, oznake in zip(nalaz.reci, nalaz.oznake):
        if oznake:
            opisi = "; ".join(crte.CRTA_PO_ID[i].opis for i in oznake)
            print(f"  {rec:<16} {opisi}")
    print("\n" + ("ЈАКО дијалекатска" if nalaz.jako_dijalekatska
                   else "слабо изражене црте"))
    return 0


def _stanica_i_sesija(args, cfg):
    from govor.audio import load_audio
    from govor.pipeline import Stanica

    if getattr(args, "asr", None):
        cfg.asr.backend = args.asr
    audio, sr = load_audio(args.wav)
    stanica = Stanica(cfg)
    sesija = stanica.obradi(audio, sr, args.govornik)
    return stanica, sesija, audio, sr


def cmd_prepisi(args) -> int:
    cfg = load_config(args.config)
    _nivo(cfg, args)
    stanica, sesija, _, _ = _stanica_i_sesija(args, cfg)
    try:
        print(f"Модел: {sesija.transkript.model}   "
              f"просечан скор: {sesija.prosecan_skor:.2f}\n")
        for stavka in sesija.stavke:
            print(stavka)
        print(f"\n{OGRADA}")
    finally:
        stanica.close()
    return 0


def cmd_ispravi(args) -> int:
    cfg = load_config(args.config)
    _nivo(cfg, args)
    from govor.korpus import Korpus

    stanica, sesija, audio, _ = _stanica_i_sesija(args, cfg)
    korpus = Korpus(cfg.korpus.koren)
    if args.govornik not in korpus.govornici:
        print(f"Говорник '{args.govornik}' није у корпусу. Додај га:")
        print(f"  govor korpus govornik {args.govornik} --inicijali 'X. Y.' --selo ... --saglasnost")
        return 2

    stavke = (sesija.istaknute(cfg.korpus.min_skor_za_isticanje)
              if args.samo_istaknute else sesija.stavke)
    print(f"{len(stavke)} сегмената за преглед. Enter = препис је тачан, "
          f". = прескочи, текст = исправка.\n")
    upisano = 0
    try:
        for stavka in stavke:
            print(stavka)
            try:
                unos = input("исправка > ").strip()
            except EOFError:
                break
            if unos == ".":
                continue
            tekst = unos or stavka.tekst_asr
            u = stanica.sacuvaj_ispravku(korpus, sesija, audio, stavka.redni, tekst)
            upisano += 1
            print(f"  → унос {u.id}\n")
    finally:
        stanica.close()
    print(f"Уписано {upisano} у {cfg.korpus.koren}/. "
          f"Одобравање: govor korpus odobri <id>")
    return 0


def cmd_korpus(args) -> int:
    cfg = load_config(args.config)
    from govor.korpus import Govornik, Korpus

    korpus = Korpus(cfg.korpus.koren)

    if args.korpus_cmd == "stanje":
        r = korpus.rezime()
        for k, v in r.items():
            print(f"  {k:<18} {v}")
        return 0

    if args.korpus_cmd == "govornik":
        korpus.dodaj_govornika(Govornik(
            id=args.id, inicijali=args.inicijali, selo=args.selo,
            godiste=args.godiste, saglasnost=args.saglasnost,
        ))
        stanje = "СА сагласношћу" if args.saglasnost else "БЕЗ сагласности (неће у извоз)"
        print(f"Говорник '{args.id}' додат — {stanje}.")
        return 0

    if args.korpus_cmd == "odobri":
        korpus.odobri(args.unos_id, not args.ponisti)
        print(f"Унос {args.unos_id}: {'поништено одобрење' if args.ponisti else 'одобрено'}.")
        return 0

    if args.korpus_cmd == "izvoz":
        parovi = korpus.za_doobuku()
        if not parovi:
            print("Ниједан одобрен унос са сагласношћу говорника.")
            return 0
        if args.out:
            Path(args.out).write_text(
                "".join(f"{wav}\t{tekst}\n" for wav, tekst in parovi), encoding="utf-8"
            )
            print(f"{len(parovi)} парова → {args.out}")
        else:
            for wav, tekst in parovi:
                print(f"{wav}\t{tekst}")
        return 0
    return 1


def cmd_recnik(args) -> int:
    cfg = load_config(args.config)
    from govor import recnik as recnik_mod

    recnik = recnik_mod.ucitaj(cfg.recnik or None)
    print(f"Речник: {len(recnik)} одредница, потврђених: {recnik.potvrdjenih}\n")
    for o in recnik:
        oznaka = "✓" if o.potvrdio_govornik else "?"
        print(f"  {oznaka} {o.opis()}" if args.sve else f"  {oznaka} {o.rec} — {o.znaci}")
    upoz = recnik.upozorenje()
    if upoz:
        print(f"\n{upoz}")
    return 0


def cmd_devices(_args) -> int:
    try:
        from govor.audio import list_devices

        for d in list_devices():
            print(f"  [{d['index']}] {d['naziv']}  ({d['ulaza']} улаза)")
    except Exception as exc:  # pragma: no cover
        print(f"Микрофони: грешка ({exc}). Инсталирај: pip install -e '.[zvuk]'")
    return 0


def cmd_download(args) -> int:  # pragma: no cover
    cfg = load_config(args.config)
    from faster_whisper import WhisperModel

    print(f"Whisper '{cfg.asr.model}' → {cfg.asr.download_root} …")
    WhisperModel(cfg.asr.model, download_root=cfg.asr.download_root or None)
    print("Готово. Станица сада ради офлајн.")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    return {
        "oceni": cmd_oceni,
        "prepisi": cmd_prepisi,
        "ispravi": cmd_ispravi,
        "korpus": cmd_korpus,
        "recnik": cmd_recnik,
        "devices": cmd_devices,
        "download-model": cmd_download,
    }[args.cmd](args)
