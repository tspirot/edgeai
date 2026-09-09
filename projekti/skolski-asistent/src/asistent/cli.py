"""Командна линија: `asistent ask | run | devices | index | download-model`."""

from __future__ import annotations

import argparse
import logging
import sys

from asistent import __version__
from asistent.config import load_config

log = logging.getLogger("asistent")


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
    p = argparse.ArgumentParser(prog="asistent", description="Школски асистент, без облака")
    p.add_argument("--version", action="version", version=f"asistent {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    ask = sub.add_parser("ask", help="Једно питање: слика + питање → одговор")
    ask.add_argument("-c", "--config", help="путања до config.yaml")
    ask.add_argument("--image", help="слика са диска (иначе: кадар са камере)")
    ask.add_argument("--question", help="питање као текст (иначе: слушај микрофон)")
    ask.add_argument("--vlm", choices=["qwen", "dummy"])
    ask.add_argument("--asr", choices=["faster-whisper", "dummy"])
    ask.add_argument("--tts", choices=["piper", "console"])
    ask.add_argument("--rag", dest="rag", action="store_true", help="укључи RAG")
    ask.add_argument("--no-rag", dest="rag", action="store_false")
    ask.add_argument("--no-speak", action="store_true", help="не изговарај одговор")
    ask.add_argument("-v", "--verbose", action="store_true")
    ask.set_defaults(rag=None)

    run = sub.add_parser("run", help="Петља: Enter → сними питање → одговор")
    run.add_argument("-c", "--config")
    run.add_argument("--vlm", choices=["qwen", "dummy"])
    run.add_argument("--asr", choices=["faster-whisper", "dummy"])
    run.add_argument("--tts", choices=["piper", "console"])
    run.add_argument("--rag", dest="rag", action="store_true")
    run.add_argument("--no-rag", dest="rag", action="store_false")
    run.add_argument("-v", "--verbose", action="store_true")
    run.set_defaults(rag=None)

    sub.add_parser("devices", help="Прикажи камере и аудио улазе")

    idx = sub.add_parser("index", help="RAG индекс над школским материјалима")
    idx_sub = idx.add_subparsers(dest="index_cmd", required=True)
    build = idx_sub.add_parser("build", help="Направи индекс из фолдера (.txt/.md)")
    build.add_argument("folder")
    build.add_argument("-c", "--config")
    build.add_argument("-o", "--out", help="путања излазног индекса (иначе из конфигурације)")
    show = idx_sub.add_parser("show", help="Кратак преглед индекса")
    show.add_argument("-c", "--config")

    dm = sub.add_parser("download-model", help="Преузми моделе унапред (тражи интернет)")
    dm.add_argument("-c", "--config")
    dm.add_argument("--what", choices=["asr", "vlm", "tts", "all"], default="all")
    return p


def _apply_overrides(cfg, args) -> None:
    if getattr(args, "vlm", None):
        cfg.vlm.backend = args.vlm
    if getattr(args, "asr", None):
        cfg.asr.backend = args.asr
    if getattr(args, "tts", None):
        cfg.tts.backend = args.tts
    if getattr(args, "rag", None) is not None:
        cfg.rag.enabled = args.rag
    if getattr(args, "no_speak", False):
        cfg.tts.speak = False


def _load_image(cfg, args):
    if getattr(args, "image", None):
        from asistent.capture import load_image

        return load_image(args.image)
    from asistent.capture import Camera

    with Camera(cfg.camera) as cam:
        return cam.grab()


def _get_question(cfg, args) -> str:
    if getattr(args, "question", None):
        return args.question
    if cfg.asr.backend == "dummy":
        return cfg.asr.dummy_text
    from asistent.audio import record_question

    print("Слушам питање… (говори, па застани)")
    audio = record_question(cfg.asr)
    return None if audio.size == 0 else audio


def cmd_ask(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)

    from asistent.pipeline import Assistant

    assistant = Assistant(cfg)
    try:
        image = _load_image(cfg, args)
        q = _get_question(cfg, args)
        question = q if isinstance(q, str) else (assistant.transcribe(q) if q is not None else "")
        if question:
            print(f"Питање: {question}")
        answer = assistant.ask(image, question)
        if not cfg.tts.speak:
            print(f"\nОдговор: {answer.text}\n")
        if answer.latency_ms:
            log.info("VLM: %.0f ms", answer.latency_ms)
    finally:
        assistant.close()
    return 0


def cmd_run(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)

    from asistent.audio import record_question
    from asistent.capture import Camera
    from asistent.pipeline import Assistant

    assistant = Assistant(cfg)
    print("Постави питање: покажи нешто камери, притисни Enter, изговори питање. Ctrl+C за крај.")
    try:
        with Camera(cfg.camera) as cam:
            while True:
                try:
                    input("\n[Enter за ново питање] ")
                except EOFError:
                    break
                image = cam.grab()
                audio = record_question(cfg.asr)
                question = assistant.transcribe(audio) if audio.size else ""
                print(f"Питање: {question or '(нисам чуо)'}")
                answer = assistant.ask(image, question)
                if not cfg.tts.speak:
                    print(f"Одговор: {answer.text}")
    except KeyboardInterrupt:
        pass
    finally:
        assistant.close()
    return 0


def cmd_devices(_args) -> int:
    try:
        from asistent.capture import list_cameras

        print("Камере:", list_cameras() or "нема")
    except Exception as exc:  # pragma: no cover
        print(f"Камере: грешка ({exc}). Инсталирај extras: pip install -e '.[kamera]'")
    try:
        from asistent.audio import print_devices

        print("Аудио улази:")
        print_devices()
    except Exception as exc:  # pragma: no cover
        print(f"Аудио: грешка ({exc}). Инсталирај extras: pip install -e '.[zvuk]'")
    return 0


def cmd_index(args) -> int:
    cfg = load_config(args.config)
    if args.index_cmd == "build":
        from asistent.rag import build_index

        idx = build_index(args.folder, cfg.rag)
        out = args.out or cfg.rag.index_path
        idx.save(out)
        print(f"Индекс: {len(idx.entries)} исечака → {out}")
        return 0

    from asistent.rag import load_index

    idx = load_index(cfg.rag.index_path)
    izvori = sorted({e.source for e in idx.entries})
    print(f"{len(idx.entries)} исечака, {len(izvori)} извора ({idx.embedder_name}):")
    for src in izvori:
        n = sum(1 for e in idx.entries if e.source == src)
        print(f"  {src}  ({n})")
    return 0


def cmd_download(args) -> int:
    cfg = load_config(args.config)
    what = args.what

    if what in ("asr", "all"):
        from faster_whisper import WhisperModel

        print(f"Whisper '{cfg.asr.whisper.model}' → {cfg.asr.whisper.download_root} …")
        WhisperModel(cfg.asr.whisper.model, download_root=cfg.asr.whisper.download_root or None)

    if what in ("vlm", "all"):
        from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

        print(f"VLM '{cfg.vlm.model}' → {cfg.vlm.download_root} …")
        AutoProcessor.from_pretrained(cfg.vlm.model, cache_dir=cfg.vlm.download_root or None)
        Qwen2VLForConditionalGeneration.from_pretrained(
            cfg.vlm.model, cache_dir=cfg.vlm.download_root or None
        )

    if what in ("tts", "all"):
        print(
            f"Piper глас '{cfg.tts.voice}': преузми .onnx и .onnx.json са "
            "https://huggingface.co/rhasspy/piper-voices у "
            f"{cfg.tts.model_path}/"
        )

    print("Готово где је било могуће. Систем сада ради офлајн.")
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    handlers = {
        "ask": cmd_ask,
        "run": cmd_run,
        "devices": cmd_devices,
        "index": cmd_index,
        "download-model": cmd_download,
    }
    return handlers[args.cmd](args)
