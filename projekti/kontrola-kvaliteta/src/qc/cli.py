"""Командна линија: `qc fit | check | eval | sim`."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from qc import __version__
from qc.config import load_config


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        rc = getattr(stream, "reconfigure", None)
        if rc:
            try:
                rc(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="qc", description="Контрола квалитета — детекција аномалија")
    p.add_argument("--version", action="version", version=f"qc {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    fit = sub.add_parser("fit", help="Научи модел на исправним комадима")
    fit.add_argument("ok_dir")
    fit.add_argument("--val", help="фасцикла за калибрацију прага (иначе ok_dir)")
    fit.add_argument("-c", "--config")
    fit.add_argument("-o", "--out", default="model.npz")

    ch = sub.add_parser("check", help="Провери једну слику")
    ch.add_argument("image")
    ch.add_argument("-c", "--config")
    ch.add_argument("-m", "--model", default="model.npz")

    ev = sub.add_parser("eval", help="Оцени на тест скупу (test_dir/ok, test_dir/defect)")
    ev.add_argument("test_dir")
    ev.add_argument("-c", "--config")
    ev.add_argument("-m", "--model", default="model.npz")

    sm = sub.add_parser("sim", help="Синтетички узорци: научи и оцени, без фајлова")
    sm.add_argument("-c", "--config")
    sm.add_argument("--n-ok", type=int, default=30)
    return p


def cmd_fit(args) -> int:
    from qc.app import train
    from qc.data import load_folder

    cfg = load_config(args.config)
    ok = load_folder(args.ok_dir)
    val = load_folder(args.val) if args.val else None
    det = train(cfg, ok, val)
    det.save(args.out)
    print(f"Модел сачуван: {args.out}   праг: {det.threshold:.4f}   исправних: {len(ok)}")
    return 0


def cmd_check(args) -> int:
    import cv2

    from qc.detect import AnomalyDetector

    cfg = load_config(args.config)
    det = AnomalyDetector.load(args.model, cfg)
    img = cv2.imread(args.image)
    if img is None:
        raise SystemExit(f"Не могу да учитам слику: {args.image}")
    r = det.predict(img)
    verdict = "МАНА" if r.is_anomaly else "исправно"
    print(f"{verdict}   score {r.score:.4f}   праг {r.threshold:.4f}")
    return 1 if r.is_anomaly else 0


def cmd_eval(args) -> int:
    from qc.app import evaluate
    from qc.data import load_folder
    from qc.detect import AnomalyDetector

    cfg = load_config(args.config)
    det = AnomalyDetector.load(args.model, cfg)
    base = Path(args.test_dir)
    ok = load_folder(base / "ok")
    defect = load_folder(base / "defect")
    res = evaluate(det, ok, defect)
    print(
        f"мане нађене: {res.true_pos}/{res.defect_total} ({res.recall:.0%})   "
        f"лажни аларми: {res.false_pos}/{res.ok_total} ({res.false_alarm_rate:.0%})"
    )
    return 0


def cmd_sim(args) -> int:
    from qc.app import evaluate, train
    from qc.data import synthetic_defect, synthetic_ok

    cfg = load_config(args.config)
    size = cfg.features.image_size
    ok_train = synthetic_ok(args.n_ok, size, seed=0)
    ok_val = synthetic_ok(10, size, seed=500)
    defects = [synthetic_defect(size, seed=100 + i, kind=k)
               for i, k in enumerate(["hole", "foreign", "smudge"] * 3)]

    det = train(cfg, ok_train, ok_val)
    res = evaluate(det, ok_val, defects)
    print(
        f"праг {res.threshold:.4f}   "
        f"мане: {res.true_pos}/{res.defect_total}   "
        f"лажни аларми: {res.false_pos}/{res.ok_total}"
    )
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _parser().parse_args(argv)
    return {
        "fit": cmd_fit, "check": cmd_check, "eval": cmd_eval, "sim": cmd_sim,
    }[args.cmd](args)
