"""Командна линија: `zebra run | calibrate | devices | download-model`."""

from __future__ import annotations

import argparse
import logging
import sys

from zebra import __version__
from zebra.config import load_config

log = logging.getLogger("zebra")


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        rc = getattr(stream, "reconfigure", None)
        if rc:
            try:
                rc(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="zebra", description="Паметна зебра — бројач и упозорење")
    p.add_argument("--version", action="version", version=f"zebra {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Покрени обраду")
    run.add_argument("-c", "--config")
    run.add_argument("--source", help="'sim', индекс камере ('0'), или видео фајл")
    run.add_argument("--backend", choices=["yolo", "hailo", "dummy"])
    run.add_argument("--model")
    run.add_argument("--zones", help="путања до zones.json")
    run.add_argument("--sim", action="store_true", help="--source sim --backend dummy")
    run.add_argument("--display", action="store_true", help="прикажи прозор (OpenCV)")
    run.add_argument("--no-gpio", action="store_true")
    run.add_argument("--max-frames", type=int)
    run.add_argument("-v", "--verbose", action="store_true")

    cal = sub.add_parser("calibrate", help="Означи зоне и сними zones.json")
    cal.add_argument("-c", "--config")
    cal.add_argument("--source")
    cal.add_argument("-o", "--out", default="zones.json")

    sub.add_parser("devices", help="Прикажи камере (OpenCV индекси)")

    dm = sub.add_parser("download-model", help="Преузми YOLO модел унапред")
    dm.add_argument("--model", default="yolov8n.pt")
    return p


def _apply(cfg, args) -> None:
    if getattr(args, "sim", False):
        cfg.video.source = "sim"
        cfg.detect.backend = "dummy"
    if getattr(args, "source", None):
        cfg.video.source = args.source
    if getattr(args, "backend", None):
        cfg.detect.backend = args.backend
    if getattr(args, "model", None):
        cfg.detect.model = args.model
    if getattr(args, "zones", None):
        cfg.zone.file = args.zones
    if getattr(args, "no_gpio", False):
        cfg.io.gpio = False


def cmd_run(args) -> int:
    cfg = load_config(args.config)
    _apply(cfg, args)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)

    from zebra.app import App

    display = None
    if args.display:
        from zebra.display import Display

        display = Display(cfg)

    stats = App(cfg, display=display).run(max_frames=args.max_frames)
    print(
        f"кадрова: {stats.frames}   "
        f"пешаци: {stats.counts.get('person', 0)}   "
        f"возила: {stats.counts.get('vehicle', 0)}   "
        f"упозорења: {stats.warning_events}"
    )
    return 0


def cmd_calibrate(args) -> int:
    cfg = load_config(args.config)
    if args.source:
        cfg.video.source = args.source
    from zebra.calibrate import calibrate

    calibrate(cfg, args.out)
    return 0


def cmd_devices(_args) -> int:
    import cv2

    found = []
    for i in range(6):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            found.append(i)
            cap.release()
    print("Камере (индекси):", found or "ниједна")
    return 0


def cmd_download(args) -> int:
    from ultralytics import YOLO

    print(f"Преузимам {args.model} …")
    YOLO(args.model)
    print("Готово.")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _parser().parse_args(argv)
    return {
        "run": cmd_run,
        "calibrate": cmd_calibrate,
        "devices": cmd_devices,
        "download-model": cmd_download,
    }[args.cmd](args)
