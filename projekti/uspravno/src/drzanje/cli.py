"""Командна линија: `drzanje sim | run | calibrate | report | devices`."""

from __future__ import annotations

import argparse
import logging
import sys

from drzanje import __version__
from drzanje.config import load_config

log = logging.getLogger("drzanje")


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        rc = getattr(stream, "reconfigure", None)
        if rc is not None:
            try:
                rc(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="drzanje", description="Усправно — надзор држања кичме")
    p.add_argument("--version", action="version", version=f"drzanje {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Надзор уживо (камера + поза)")
    run.add_argument("-c", "--config")
    run.add_argument("--seconds", type=float, help="колико дуго (иначе до Ctrl+C)")
    run.add_argument("--no-reference", action="store_true", help="без личне калибрације")
    run.add_argument("-v", "--verbose", action="store_true")

    sim = sub.add_parser("sim", help="Симулација без камере и модела")
    sim.add_argument("-c", "--config")
    sim.add_argument("--steps", type=int, default=180)
    sim.add_argument("-v", "--verbose", action="store_true")

    cal = sub.add_parser("calibrate", help="Сними усправан положај као личну референцу")
    cal.add_argument("-c", "--config")
    cal.add_argument("--samples", type=int, default=30)

    rep = sub.add_parser("report", help="Извештај из записника")
    rep.add_argument("-c", "--config")
    rep.add_argument("--screening", action="store_true", help="извештај асиметрије (skrining.csv)")

    sub.add_parser("devices", help="Прикажи камере")
    return p


def _sim_cfg(cfg):
    cfg.camera.backend = "dummy"
    cfg.pose.backend = "dummy"
    cfg.feedback.backend = "console"
    return cfg


def cmd_sim(args) -> int:
    cfg = _sim_cfg(load_config(args.config))
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else "INFO")
    from drzanje.pipeline import Monitor

    mon = Monitor(cfg)
    dt = 1.0 / cfg.camera.fps
    try:
        for i in range(args.steps):
            st = mon.step(t=i * dt)
            if st is None:
                continue
            if i % 15 == 0:
                mark = "ЛОШЕ" if st.bad else "ок  "
                print(f"{i * dt:5.1f}s  {mark}  врат Δ{st.neck_dev:4.1f}°  труп Δ{st.trunk_dev:4.1f}°"
                      + ("   🔔 подсетник" if st.alert else ""))
    finally:
        mon.close()
    s = mon.session_summary()
    print(f"\nСесија {s['duration_s']}s: погрбљеност {s['total_bad_s']}s у {s['events']} епизода; "
          f"највеће Δ врат {s['max_neck_dev']}° / труп {s['max_trunk_dev']}°")
    return 0


def cmd_run(args) -> int:
    cfg = load_config(args.config)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)
    from drzanje.logbook import log_screening, log_session
    from drzanje.pipeline import Monitor
    from drzanje.posture import Reference

    ref = None
    if not args.no_reference:
        try:
            ref = Reference.load(cfg.reference_path)
            print(f"Референца: врат {ref.neck_deg:.1f}°, труп {ref.trunk_deg:.1f}°")
        except FileNotFoundError:
            print("Нема референце — пратим апсолутне углове. `drzanje calibrate` за личну.")

    mon = Monitor(cfg, reference=ref)
    print("Надзор ради. Ctrl+C за крај." + (f" ({args.seconds:.0f}s)" if args.seconds else ""))
    try:
        mon.run(seconds=args.seconds)
    finally:
        mon.close()
    s = mon.session_summary()
    log_session(cfg.log_path, s["duration_s"], s["total_bad_s"], s["events"],
                s["max_neck_dev"], s["max_trunk_dev"])
    if cfg.screening.enabled and "shoulder_tilt" in s:
        log_screening(cfg.screening.log_path, s["shoulder_tilt"], s["hip_tilt"])
    print(f"Уписано у {cfg.log_path}: погрбљеност {s['total_bad_s']}s / {s['events']} епизода.")
    return 0


def cmd_calibrate(args) -> int:
    cfg = load_config(args.config)
    from drzanje.pipeline import calibrate

    print("Седи усправно и мирно ~5 секунди…")
    ref = calibrate(cfg, samples=args.samples)
    ref.save(cfg.reference_path)
    print(f"Референца сачувана у {cfg.reference_path}: врат {ref.neck_deg:.1f}°, труп {ref.trunk_deg:.1f}°")
    return 0


def cmd_report(args) -> int:
    cfg = load_config(args.config)
    from drzanje.logbook import read_csv

    if args.screening:
        from drzanje.screening import summarize

        rows = read_csv(cfg.screening.log_path)
        r = summarize(rows, cfg.screening.asymmetry_flag_deg)
        print(f"Скрининг ({r['n']} мерења, {r.get('period', '-')}):")
        if r["n"]:
            print(f"  рамена: |просек| {r['shoulder']['abs_mean']}°  прелази праг {r['shoulder']['n_over']}×")
            print(f"  кукови: |просек| {r['hip']['abs_mean']}°  прелази праг {r['hip']['n_over']}×")
        print(f"  {r['note']}")
        return 0

    rows = read_csv(cfg.log_path)
    tot_bad = sum(float(r["bad_s"]) for r in rows)
    tot_dur = sum(float(r["duration_s"]) for r in rows)
    print(f"Записник: {len(rows)} сесија, укупно {tot_dur / 60:.0f} min")
    if tot_dur > 0:
        print(f"  погрбљеност: {tot_bad / 60:.1f} min ({100 * tot_bad / tot_dur:.0f}% времена)")
        print(f"  епизода укупно: {sum(int(r['events']) for r in rows)}")
    return 0


def cmd_devices(_args) -> int:
    try:
        import cv2

        found = [i for i in range(6) if cv2.VideoCapture(i).isOpened()]
        print("Камере:", found or "нема")
    except Exception as exc:  # pragma: no cover
        print(f"Камере: грешка ({exc}). Инсталирај: pip install -e '.[kamera]'")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    handlers = {
        "sim": cmd_sim, "run": cmd_run, "calibrate": cmd_calibrate,
        "report": cmd_report, "devices": cmd_devices,
    }
    return handlers[args.cmd](args)
