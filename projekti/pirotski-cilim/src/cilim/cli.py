"""Командна линија: `cilim motivi | procitaj | smisli | karton | devices`."""

from __future__ import annotations

import argparse
import logging
import sys

from cilim import OGRADA, __version__
from cilim.config import load_config

log = logging.getLogger("cilim")


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
        prog="cilim",
        description="Шара у духу пиротског ћилима — препознавање и предлог, на уређају",
        epilog=OGRADA,
    )
    p.add_argument("--version", action="version", version=f"cilim {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    mot = sub.add_parser("motivi", help="Каталог шара: шта уређај зна и шта је потврђено")
    mot.add_argument("-c", "--config")
    mot.add_argument("--sve", action="store_true", help="испиши и значења")

    pro = sub.add_parser("procitaj", help="Препознај шару на слици или са камере")
    pro.add_argument("-c", "--config")
    pro.add_argument("--image", help="слика са диска (иначе: кадар са камере)")
    pro.add_argument("--klasifikator", choices=["vit", "dummy"])
    pro.add_argument("-v", "--verbose", action="store_true")

    smi = sub.add_parser("smisli", help="Скица → предлог шаре → картон за ткање")
    smi.add_argument("-c", "--config")
    smi.add_argument("--skica", help="груб цртеж ученика (слика); без ње модел бира сам")
    smi.add_argument("--motiv", help="шара из каталога на коју се предлог ослања")
    smi.add_argument("--seed", type=int, default=0)
    smi.add_argument("--generator", choices=["difuzija", "pravila"])
    smi.add_argument("-o", "--out", default="izlaz", help="фолдер за резултате")
    smi.add_argument("-v", "--verbose", action="store_true")

    kar = sub.add_parser("karton", help="Готова шара са слике → картон за ткање")
    kar.add_argument("image")
    kar.add_argument("-c", "--config")
    kar.add_argument("-o", "--out", default="izlaz")

    sub.add_parser("devices", help="Прикажи камере")

    dm = sub.add_parser("download-model", help="Преузми моделе унапред (тражи интернет)")
    dm.add_argument("-c", "--config")
    return p


def _apply_overrides(cfg, args) -> None:
    if getattr(args, "klasifikator", None):
        cfg.klasifikator.backend = args.klasifikator
    if getattr(args, "generator", None):
        cfg.generator.backend = args.generator


def _nivo(cfg, args) -> None:
    logging.getLogger().setLevel(
        logging.DEBUG if getattr(args, "verbose", False) else cfg.log_level
    )


def cmd_motivi(args) -> int:
    from cilim import motivi as mot

    cfg = load_config(args.config)
    katalog = mot.ucitaj(cfg.katalog or None)
    print(f"Каталог: {len(katalog)} шара, потврђених у радионици: {katalog.potvrdjenih}\n")
    for m in katalog:
        oznaka = "✓" if m.potvrdila_radionica else "?"
        print(f"  {oznaka} {m.id:<20} {m.naziv}")
        if args.sve:
            print(f"      {m.znacenje}")
            print(f"      извор: {', '.join(m.izvor) or '—'} · део: {m.deo}")
    upozorenje = katalog.upozorenje()
    if upozorenje:
        print(f"\n{upozorenje}")
    return 0


def _slika(cfg, args):
    if getattr(args, "image", None):
        from cilim.capture import load_image

        return load_image(args.image)
    from cilim.capture import Camera

    with Camera(cfg.camera) as cam:
        return cam.grab()


def cmd_procitaj(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    _nivo(cfg, args)

    from cilim.pipeline import Radionica

    radionica = Radionica(cfg)
    try:
        nalaz, tekst = radionica.procitaj(_slika(cfg, args))
        print(tekst)
        if args.verbose and nalaz.ostali:
            print("Остале могућности:")
            for mid, p in nalaz.ostali:
                print(f"  {mid:<20} {p:.0%}")
        if nalaz.latencija_ms:
            log.info("Класификатор: %.0f ms", nalaz.latencija_ms)
    finally:
        radionica.close()
    return 0


def _sacuvaj(predlog, out: str) -> None:
    from pathlib import Path

    from cilim.capture import save_image

    folder = Path(out)
    save_image(predlog.slika, folder / "sara.png")
    predlog.karton.u_csv(folder / "karton.csv")
    predlog.karton.u_png(folder / "karton.png")
    print(f"\nУписано у {folder}/: sara.png, karton.csv, karton.png")


def cmd_smisli(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    _nivo(cfg, args)

    from cilim.capture import load_image
    from cilim.pipeline import Radionica

    skica = load_image(args.skica) if args.skica else None
    radionica = Radionica(cfg)
    try:
        predlog = radionica.smisli(skica=skica, motiv_id=args.motiv, seed=args.seed)
        print(predlog)
        _sacuvaj(predlog, args.out)
        if not predlog.izvestaj.izvodljivo():
            print("\nОвај предлог тешко да се исктка овакав. Промени seed или скицу.")
    finally:
        radionica.close()
    return 0


def cmd_karton(args) -> int:
    cfg = load_config(args.config)
    from cilim import pravila as prv
    from cilim.capture import load_image
    from cilim.karton import Karton

    indeksi = prv.primeni(load_image(args.image), cfg.pravila)
    k = cfg.karton
    karton = Karton.iz_indeksa(indeksi, k.redova, k.kolona, niti_po_celiji=k.niti_po_celiji)
    print(OGRADA)
    print()
    print(prv.proveri(karton.mreza, cfg.pravila.min_niti))
    print()
    print(karton.rezime())

    from pathlib import Path

    folder = Path(args.out)
    karton.u_csv(folder / "karton.csv")
    karton.u_png(folder / "karton.png")
    print(f"\nУписано у {folder}/: karton.csv, karton.png")
    return 0


def cmd_devices(_args) -> int:
    try:
        from cilim.capture import list_cameras

        print("Камере:", list_cameras() or "нема")
    except Exception as exc:  # pragma: no cover
        print(f"Камере: грешка ({exc}). Инсталирај extras: pip install -e '.[kamera]'")
    return 0


def cmd_download(args) -> int:  # pragma: no cover
    cfg = load_config(args.config)
    from diffusers import ControlNetModel, StableDiffusionControlNetPipeline

    print(f"ControlNet '{cfg.generator.controlnet}' → {cfg.generator.download_root} …")
    ControlNetModel.from_pretrained(
        cfg.generator.controlnet, cache_dir=cfg.generator.download_root or None
    )
    print(f"Stable Diffusion '{cfg.generator.model}' …")
    StableDiffusionControlNetPipeline.from_pretrained(
        cfg.generator.model,
        controlnet=ControlNetModel.from_pretrained(
            cfg.generator.controlnet, cache_dir=cfg.generator.download_root or None
        ),
        cache_dir=cfg.generator.download_root or None,
        safety_checker=None,
    )
    print(
        "Готово. LoRA и тежине класификатора се НЕ преузимају — оне настају "
        "обуком на школском скупу шара (docs/obuka.md)."
    )
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    handlers = {
        "motivi": cmd_motivi,
        "procitaj": cmd_procitaj,
        "smisli": cmd_smisli,
        "karton": cmd_karton,
        "devices": cmd_devices,
        "download-model": cmd_download,
    }
    return handlers[args.cmd](args)
