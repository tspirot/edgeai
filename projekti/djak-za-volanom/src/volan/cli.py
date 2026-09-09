"""Командна линија: `volan sim | drive | record | train | check | devices`."""

from __future__ import annotations

import argparse
import logging
import sys
import time

from volan import __version__
from volan.config import load_config

log = logging.getLogger("volan")


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        rc = getattr(stream, "reconfigure", None)
        if rc is not None:
            try:
                rc(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="volan", description="Ђак за воланом — аутономна вожња 1:10")
    p.add_argument("--version", action="version", version=f"volan {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    for name, helptext in [
        ("drive", "Аутономна вожња (камера + модел + лидар)"),
        ("sim", "Симулација без хардвера — испиши одлуке"),
    ]:
        sp = sub.add_parser(name, help=helptext)
        sp.add_argument("-c", "--config")
        sp.add_argument("--model", choices=["tflite", "heuristic", "dummy"])
        sp.add_argument("--steps", type=int, help="ограничи број циклуса (sim: подразумевано 100)")
        sp.add_argument("-v", "--verbose", action="store_true")

    rec = sub.add_parser("record", help="Ручна вожња + снимање скупа података")
    rec.add_argument("-c", "--config")
    rec.add_argument("--gamepad", choices=["auto", "evdev", "dummy"], default="auto")
    rec.add_argument("--seconds", type=float, default=60.0)
    rec.add_argument("--session", default="")
    rec.add_argument("-v", "--verbose", action="store_true")

    tr = sub.add_parser("train", help="Обука CNN-а из снимака → pilot.tflite")
    tr.add_argument("data", help="фолдер са снимцима (tub)")
    tr.add_argument("-c", "--config")
    tr.add_argument("-o", "--out", default="models/pilot.tflite")
    tr.add_argument("--epochs", type=int, default=20)

    ch = sub.add_parser("check", help="Брза провера камере, лидара и актуатора")
    ch.add_argument("-c", "--config")

    sub.add_parser("devices", help="Прикажи камере и серијске портове")
    return p


def _apply(cfg, args) -> None:
    if getattr(args, "model", None):
        cfg.model.backend = args.model


def _make_loop(cfg, sim: bool):
    from volan.pipeline import DriveLoop

    if sim:
        from volan.actuators import DummyActuator
        from volan.camera import DummyCamera
        from volan.lidar import DummyLidar

        if cfg.model.backend == "tflite":
            cfg.model.backend = "heuristic"
        return DriveLoop(
            cfg,
            camera=DummyCamera(cfg.camera),
            lidar=DummyLidar(),
            actuator=DummyActuator(),
        )
    return DriveLoop(cfg)


def cmd_drive(args) -> int:
    cfg = load_config(args.config)
    _apply(cfg, args)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)
    loop = _make_loop(cfg, sim=False)
    print(f"Аутономна вожња, {cfg.drive.hz:.0f} Hz, макс гас {cfg.drive.max_throttle}. Ctrl+C за стоп.")
    steps = loop.run(max_steps=args.steps)
    print(f"Заустављено после {steps} циклуса.")
    return 0


def cmd_sim(args) -> int:
    cfg = load_config(args.config)
    _apply(cfg, args)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else "INFO")
    loop = _make_loop(cfg, sim=True)
    n = args.steps or 100
    braked = 0
    for i in range(n):
        d = loop.step()
        braked += int(d.braking)
        if i % 10 == 0:
            print(f"{i:4d}  волан {d.steer:+.2f}  гас {d.throttle:.2f}  {d.reason}")
        if i == n // 2:
            loop.lidar.set_obstacle(400.0)  # убаци препреку на пола
            print("  → препрека на 400 mm")
    loop.close()
    print(f"Кочница активна у {braked}/{n} циклуса.")
    return 0


def cmd_record(args) -> int:
    cfg = load_config(args.config)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)

    from volan.camera import build_camera
    from volan.gamepad import build_gamepad
    from volan.recorder import TubWriter

    cam = build_camera(cfg.camera)
    pad = build_gamepad(args.gamepad)
    tub = TubWriter(cfg.record.out_dir, cfg.record.jpg_quality, args.session)
    period = 1.0 / cfg.camera.fps
    print(f"Снимам у {tub.dir} — {args.seconds:.0f} s. Вози!")
    t_end = time.monotonic() + args.seconds
    try:
        while time.monotonic() < t_end:
            t0 = time.monotonic()
            steer, throttle = pad.read()
            tub.add(cam.read(), steer, throttle)
            dt = time.monotonic() - t0
            if dt < period:
                time.sleep(period - dt)
    except KeyboardInterrupt:  # pragma: no cover
        pass
    finally:
        cam.close()
        pad.close()
    print(f"Сачувано {tub.count} кадрова.")
    return 0


def cmd_train(args) -> int:
    cfg = load_config(args.config)
    from volan.train import train

    train(args.data, args.out, cfg.model.input_width, cfg.model.input_height,
          cfg.model.predicts_throttle, args.epochs)
    return 0


def cmd_check(args) -> int:
    cfg = load_config(args.config)
    from volan.camera import build_camera
    from volan.lidar import build_lidar, nearest_in_cone

    cam = build_camera(cfg.camera)
    img = cam.read()
    print(f"Камера: кадар {img.shape}, просечна светлина {img.mean():.0f}")
    cam.close()

    lidar = build_lidar(cfg.lidar)
    time.sleep(1.0)
    scan, ts = lidar.latest()
    nearest = nearest_in_cone(scan, cfg.lidar.cone_deg, cfg.lidar.forward_offset_deg,
                              cfg.lidar.min_valid_mm, cfg.lidar.max_range_mm)
    print(f"Лидар: {len(scan)} тачака, најближа испред {nearest:.0f} mm")
    lidar.close()

    from volan.actuators import build_actuator

    act = build_actuator(cfg.actuator)
    print("Актуатор: волан лево → центар → десно (без гаса)")
    for s in (-0.6, 0.0, 0.6, 0.0):
        act.drive(s, 0.0)
        time.sleep(0.4)
    act.close()
    return 0


def cmd_devices(_args) -> int:
    try:
        import glob

        ports = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
        print("Серијски портови:", ports or "нема (Windows: проверите Device Manager)")
    except Exception as exc:  # pragma: no cover
        print(f"Портови: грешка ({exc})")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    handlers = {
        "drive": cmd_drive, "sim": cmd_sim, "record": cmd_record,
        "train": cmd_train, "check": cmd_check, "devices": cmd_devices,
    }
    return handlers[args.cmd](args)
