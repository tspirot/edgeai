"""Командна линија: `dvojnik sim | snimi | slozi | devices | sto`."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from dvojnik import OGRADA, __version__
from dvojnik.config import load_config

log = logging.getLogger("dvojnik")

TELA = ("kugla", "kocka", "valjak", "solja")


def _force_utf8() -> None:
    """Windows конзола је подразумевано cp1252 — ћирилица тада руши испис."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dvojnik",
        description="3D скенер предмета на окретном столу — на самом уређају",
        epilog=OGRADA,
    )
    p.add_argument("--version", action="version", version=f"dvojnik {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    sim = sub.add_parser("sim", help="Цео ланац на синтетичком предмету, без хардвера")
    sim.add_argument("-c", "--config")
    sim.add_argument("--telo", choices=TELA, default="kugla")
    sim.add_argument("--mera", type=float, default=60.0, help="пречник/страница у mm")
    sim.add_argument("--kadrova", type=int)
    sim.add_argument("-o", "--out", default="izlaz")
    sim.add_argument("-v", "--verbose", action="store_true")

    sn = sub.add_parser("snimi", help="Заврти сто и сними круг кадрова")
    sn.add_argument("-c", "--config")
    sn.add_argument("--kadrova", type=int)
    sn.add_argument("--sto", choices=["koracni", "dummy"])
    sn.add_argument("-o", "--out", default="snimak")
    sn.add_argument("-v", "--verbose", action="store_true")

    sl = sub.add_parser("slozi", help="Снимљени кадрови → 3D модел и STL")
    sl.add_argument("snimak", help="фолдер са kadar_*.png и pozadina.png")
    sl.add_argument("-c", "--config")
    sl.add_argument("--visina-mm", type=float,
                    help="права висина предмета са шублера — без ње нема размере")
    sl.add_argument("--mreza", choices=["blokovska", "glatka"])
    sl.add_argument("-o", "--out", default="izlaz")
    sl.add_argument("-v", "--verbose", action="store_true")

    st = sub.add_parser("sto", help="Проба стола: заврти за задати угао")
    st.add_argument("-c", "--config")
    st.add_argument("--stepeni", type=float, default=360.0)
    st.add_argument("--sto", choices=["koracni", "dummy"])

    sub.add_parser("devices", help="Прикажи камере")
    return p


def _apply_overrides(cfg, args) -> None:
    if getattr(args, "sto", None):
        cfg.sto.backend = args.sto
    if getattr(args, "mreza", None):
        cfg.mreza.vrsta = args.mreza
    if getattr(args, "kadrova", None):
        cfg.kadrova = args.kadrova


def _nivo(cfg, args) -> None:
    logging.getLogger().setLevel(
        logging.DEBUG if getattr(args, "verbose", False) else cfg.log_level
    )


def _sacuvaj(skeniranje, cfg, out: str) -> None:
    from dvojnik.mreza import u_stl

    folder = Path(out)
    putanja = u_stl(skeniranje.trouglovi, folder / "model.stl", cfg.mreza.naziv)
    print(f"\n{skeniranje}")
    print(f"\nУписано: {putanja}")
    if not skeniranje.razmera_poznata:
        print("Пре штампе постави размеру: измери предмет и понови са --visina-mm.")


def cmd_sim(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    _nivo(cfg, args)

    from dvojnik import sim
    from dvojnik.config import kamera_iz
    from dvojnik.karving import granice_oko_stola
    from dvojnik.pipeline import Skener

    telo = {
        "kugla": lambda m: sim.kugla(m),
        "kocka": lambda m: sim.kocka(m),
        "valjak": lambda m: sim.valjak(m, m * 1.5),
        "solja": lambda m: sim.solja(m, m * 1.2, m * 0.15),
    }[args.telo](args.mera)

    kamera = kamera_iz(cfg)
    granice = granice_oko_stola(cfg.zapremina.precnik, cfg.zapremina.visina)
    uglovi = sim.uglovi_punog_kruga(cfg.kadrova)

    print(f"Синтетички предмет: {args.telo}, мера {args.mera:g} mm, "
          f"{cfg.kadrova} кадрова")
    kadrovi, pozadina = sim.kadrovi(telo, kamera, uglovi, granice)

    skener = Skener(cfg)
    skeniranje = skener.skeniraj(kadrovi, pozadina, uglovi)
    print(OGRADA)
    _sacuvaj(skeniranje, cfg, args.out)
    return 0


def cmd_snimi(args) -> int:  # pragma: no cover — тражи камеру и сто
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    _nivo(cfg, args)

    from dvojnik.capture import Camera, save_image
    from dvojnik.sto import build_sto

    folder = Path(args.out)
    sto = build_sto(cfg.sto)
    uglovi = sto.uglovi(cfg.kadrova)
    korak = 360.0 / cfg.kadrova

    try:
        with Camera(cfg.kamera) as kamera:
            input("Склони предмет са стола, па Enter (снимам празну позадину) ")
            save_image(kamera.grab(), folder / "pozadina.png")
            input("Стави предмет на средину стола, па Enter ")
            for i, ugao in enumerate(uglovi):
                save_image(kamera.grab(), folder / f"kadar_{i:03d}_ugao_{ugao:.1f}.png")
                print(f"\r{i + 1}/{cfg.kadrova}  {ugao:6.1f}°", end="", flush=True)
                sto.okreni_za(korak)
    finally:
        sto.close()
    print(f"\nСнимак у {folder}/. Даље: dvojnik slozi {folder} --visina-mm <измерено>")
    return 0


def cmd_slozi(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    _nivo(cfg, args)

    from dvojnik.capture import ucitaj_snimak
    from dvojnik.pipeline import Skener

    kadrovi, pozadina, uglovi = ucitaj_snimak(args.snimak)
    print(f"Учитано {len(kadrovi)} кадрова из {args.snimak}")
    skeniranje = Skener(cfg).skeniraj(kadrovi, pozadina, uglovi, args.visina_mm)
    print(OGRADA)
    _sacuvaj(skeniranje, cfg, args.out)
    return 0


def cmd_sto(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    from dvojnik.sto import build_sto

    sto = build_sto(cfg.sto)
    try:
        print(f"Окрећем за {args.stepeni:g}° …")
        print(f"Угао после окретања: {sto.okreni_za(args.stepeni):.1f}°")
    finally:
        sto.close()
    return 0


def cmd_devices(_args) -> int:
    try:
        from dvojnik.capture import list_cameras

        print("Камере:", list_cameras() or "нема")
    except Exception as exc:  # pragma: no cover
        print(f"Камере: грешка ({exc}). Инсталирај extras: pip install -e '.[kamera]'")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    return {
        "sim": cmd_sim,
        "snimi": cmd_snimi,
        "slozi": cmd_slozi,
        "sto": cmd_sto,
        "devices": cmd_devices,
    }[args.cmd](args)
