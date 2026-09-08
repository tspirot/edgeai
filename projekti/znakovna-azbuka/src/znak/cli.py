"""Командна линија: `znak record | train | run | sim`."""

from __future__ import annotations

import argparse
import logging
import sys

from znak import __version__
from znak.config import load_config


def _force_utf8() -> None:
    for stream in (sys.stdout, sys.stderr):
        rc = getattr(stream, "reconfigure", None)
        if rc:
            try:
                rc(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="znak", description="Знаковна азбука — препознавање слова")
    p.add_argument("--version", action="version", version=f"znak {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    rec = sub.add_parser("record", help="Снимај узорке за једно слово")
    rec.add_argument("--label", required=True)
    rec.add_argument("-c", "--config")
    rec.add_argument("-n", "--num", type=int, default=60)
    rec.add_argument("-o", "--out")

    tr = sub.add_parser("train", help="Скуп података → модел")
    tr.add_argument("-c", "--config")
    tr.add_argument("--data")
    tr.add_argument("-o", "--out")

    run = sub.add_parser("run", help="Препознавање уживо")
    run.add_argument("-c", "--config")
    run.add_argument("--source")
    run.add_argument("-m", "--model")

    sm = sub.add_parser("sim", help="Синтетички узорци: научи и препознај, без камере")
    sm.add_argument("-c", "--config")
    sm.add_argument("--per-letter", type=int, default=40)
    return p


def cmd_record(args) -> int:
    import cv2

    from znak.dataset import append_sample, counts
    from znak.hands import build_detector

    cfg = load_config(args.config)
    out = args.out or cfg.dataset_file
    det = build_detector(cfg.hands)
    cap = cv2.VideoCapture(int(cfg.camera.source) if str(cfg.camera.source).isdigit()
                           else cfg.camera.source)
    got = 0
    print(f"Показуј слово '{args.label}'. SPACE = сними, Q = крај.")
    while got < args.num:
        ok, frame = cap.read()
        if not ok:
            break
        pts = det.detect(frame)
        if pts is not None:
            cv2.putText(frame, f"{args.label}: {got}/{args.num}", (12, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 120), 2)
        cv2.imshow("znak record", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == 32 and pts is not None:  # SPACE
            append_sample(out, args.label, pts)
            got += 1
    cap.release()
    cv2.destroyAllWindows()
    print(f"Сачувано {got} узорака у {out}. Стање: {counts(out)}")
    return 0


def cmd_train(args) -> int:
    from znak.classifier import KnnClassifier
    from znak.dataset import load_dataset

    cfg = load_config(args.config)
    data = args.data or cfg.dataset_file
    out = args.out or cfg.model_file
    X, y = load_dataset(data)
    if len(y) < cfg.classifier.k:
        raise SystemExit(f"Премало узорака ({len(y)}). Сними више са `znak record`.")
    KnnClassifier(k=cfg.classifier.k).fit(X, y).save(out)
    from collections import Counter

    print(f"Модел: {out}   узорака: {len(y)}   по слову: {dict(Counter(y))}")
    return 0


def cmd_run(args) -> int:
    from znak.app import App
    from znak.classifier import KnnClassifier

    cfg = load_config(args.config)
    if args.source:
        cfg.camera.source = args.source
    model = args.model or cfg.model_file
    clf = KnnClassifier.load(model)
    stats = App(cfg, clf).run()
    print(f"кадрова: {stats.frames}   исписано: {' '.join(stats.recognized) or '—'}")
    return 0


def cmd_sim(args) -> int:
    import numpy as np

    from znak.app import App
    from znak.classifier import KnnClassifier
    from znak.hands.dummy_backend import DummyHands
    from znak.normalize import normalize_landmarks
    from znak.poses import POSES, sample

    cfg = load_config(args.config)
    cfg.camera.source = "sim"
    letters = list(POSES.keys())

    rng = np.random.default_rng(0)
    X = [normalize_landmarks(sample(l, rng)) for l in letters for _ in range(args.per_letter)]
    y = [l for l in letters for _ in range(args.per_letter)]
    clf = KnnClassifier(k=cfg.classifier.k).fit(X, y)

    seq = ["B", "A", "D", "O", "L", "V"]
    from znak.camera import SimSource

    stats = App(cfg, clf,
                source=SimSource(frames=len(seq) * 14),
                detector=DummyHands(sequence=seq, hold=14, seed=7)).run()

    hit = sum(1 for a, b in zip(stats.recognized, seq) if a == b)
    print(f"тражено: {' '.join(seq)}")
    print(f"исписано: {' '.join(stats.recognized) or '—'}   тачно: {hit}/{len(seq)}")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _parser().parse_args(argv)
    return {
        "record": cmd_record, "train": cmd_train, "run": cmd_run, "sim": cmd_sim,
    }[args.cmd](args)
