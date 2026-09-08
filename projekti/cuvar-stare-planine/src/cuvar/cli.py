"""Командна линија: `cuvar run | power | gallery`."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from cuvar import __version__
from cuvar.config import load_config


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        rc = getattr(stream, "reconfigure", None)
        if rc:
            try:
                rc(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cuvar", description="Чувар Старе планине — фотозамка")
    p.add_argument("--version", action="version", version=f"cuvar {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Покрени фотозамку")
    run.add_argument("-c", "--config")
    run.add_argument("--source")
    run.add_argument("--classify", choices=["imx500", "onnx", "dummy"])
    run.add_argument("--climate", choices=["bme688", "dummy"])
    run.add_argument("--sim", action="store_true", help="--source sim --classify dummy --climate dummy")
    run.add_argument("--no-save", action="store_true")
    run.add_argument("--max-frames", type=int)
    run.add_argument("-v", "--verbose", action="store_true")

    pw = sub.add_parser("power", help="Процена трајања батерије")
    pw.add_argument("-c", "--config")
    pw.add_argument("--triggers-per-hour", type=float, default=4.0)
    pw.add_argument("--seconds-per-trigger", type=float, default=6.0)

    gl = sub.add_parser("gallery", help="Сажетак сачуваних догађаја")
    gl.add_argument("-c", "--config")
    gl.add_argument("--dir")
    return p


def cmd_run(args) -> int:
    cfg = load_config(args.config)
    if args.sim:
        cfg.camera.source, cfg.classify.backend, cfg.climate.backend = "sim", "dummy", "dummy"
    if args.source:
        cfg.camera.source = args.source
    if args.classify:
        cfg.classify.backend = args.classify
    if args.climate:
        cfg.climate.backend = args.climate
    if args.no_save:
        cfg.storage.save_images = False
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)

    from cuvar.app import App

    s = App(cfg).run(max_frames=args.max_frames)
    print(
        f"кадрова: {s.frames}   окидача: {s.triggers}   снимака: {s.saved}   "
        f"врсте: {s.species_counts or '—'}"
    )
    return 0


def cmd_power(args) -> int:
    from cuvar.power import estimated_runtime_h

    cfg = load_config(args.config)
    hours = estimated_runtime_h(
        cfg.power.battery_wh, cfg.power.active_w, cfg.power.sleep_w,
        args.triggers_per_hour, args.seconds_per_trigger,
    )
    print(
        f"Батерија {cfg.power.battery_wh} Wh, {args.triggers_per_hour}/h догађаја "
        f"по {args.seconds_per_trigger} s → ~{hours:.0f} h ({hours / 24:.1f} дана)"
    )
    return 0


def cmd_gallery(args) -> int:
    cfg = load_config(args.config)
    d = Path(args.dir or cfg.storage.dir)
    if not d.exists():
        print(f"Нема фасцикле {d}")
        return 0
    counts: dict = {}
    for jf in sorted(d.glob("*.json")):
        try:
            counts[json.loads(jf.read_text(encoding="utf-8"))["species"]] = counts.get(
                json.loads(jf.read_text(encoding="utf-8"))["species"], 0
            ) + 1
        except Exception:  # noqa: BLE001
            pass
    total = sum(counts.values())
    print(f"{d}: {total} догађаја")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:20s} {v}")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _parser().parse_args(argv)
    return {"run": cmd_run, "power": cmd_power, "gallery": cmd_gallery}[args.cmd](args)
