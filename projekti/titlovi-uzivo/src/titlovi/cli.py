"""Командна линија: `titlovi run | devices | download-model`."""

from __future__ import annotations

import argparse
import logging
import sys

from titlovi import __version__
from titlovi.config import load_config

log = logging.getLogger("titlovi")


def _force_utf8() -> None:
    """Windows конзола ума подразумевано cp1252 — ћирилица тада руши испис."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except Exception:  # pragma: no cover
                pass


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="titlovi", description="Титлови уживо, без облака")
    p.add_argument("--version", action="version", version=f"titlovi {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Покрени титловање уживо")
    run.add_argument("-c", "--config", help="путања до config.yaml")
    run.add_argument("--backend", choices=["faster-whisper", "vosk", "dummy"])
    run.add_argument("--model", help="Whisper модел (tiny/base/small/…)")
    run.add_argument("--language", help="језик, подразумевано 'sr'")
    run.add_argument("--script", choices=["cyrillic", "latin", "as-is"])
    run.add_argument("--device", help="аудио улаз: индекс или назив")
    run.add_argument("--wav", help="читај WAV фајл уместо микрофона")
    run.add_argument("--display", choices=["pygame", "web", "console"])
    run.add_argument("--console", action="store_true", help="скраћеница за --display console")
    run.add_argument("--windowed", action="store_true", help="не преко целог екрана")
    run.add_argument("-v", "--verbose", action="store_true")

    sub.add_parser("devices", help="Прикажи доступне аудио улазе")

    dm = sub.add_parser("download-model", help="Преузми модел унапред (тражи интернет)")
    dm.add_argument("-c", "--config")
    dm.add_argument("--backend", choices=["faster-whisper", "vosk"], default="faster-whisper")
    dm.add_argument("--model", default="base")
    dm.add_argument("--vosk-url", help="URL .zip Vosk модела")
    dm.add_argument("--vosk-path", help="одредишна фасцикла за Vosk модел")
    return p


def _apply_overrides(cfg, args) -> None:
    if getattr(args, "backend", None):
        cfg.asr.backend = args.backend
    if getattr(args, "model", None):
        cfg.asr.whisper.model = args.model
    if getattr(args, "language", None):
        cfg.asr.whisper.language = args.language
    if getattr(args, "script", None):
        cfg.text.script = args.script
    if getattr(args, "device", None):
        cfg.audio.device = int(args.device) if str(args.device).isdigit() else args.device
    if getattr(args, "display", None):
        cfg.display.backend = args.display
    if getattr(args, "console", False):
        cfg.display.backend = "console"
    if getattr(args, "windowed", False):
        cfg.display.fullscreen = False


def cmd_run(args) -> int:
    cfg = load_config(args.config)
    _apply_overrides(cfg, args)
    logging.getLogger().setLevel(logging.DEBUG if args.verbose else cfg.log_level)

    from titlovi.pipeline import Pipeline

    frames = None
    if args.wav:
        from titlovi.audio import wav_frames

        frames = wav_frames(args.wav, cfg.audio.samplerate, cfg.audio.block_ms, realtime=True)

    try:
        Pipeline(cfg, frames=frames).run()
    except KeyboardInterrupt:
        pass
    return 0


def cmd_devices(_args) -> int:
    from titlovi.audio import print_devices

    print_devices()
    return 0


def _download_vosk(args, cfg) -> None:
    import io
    import pathlib
    import urllib.request
    import zipfile

    if not args.vosk_url:
        raise SystemExit(
            "Vosk нема званичан модел за српски. Наведи --vosk-url ка .zip моделу "
            "(нпр. са https://alphacephei.com/vosk/models)."
        )
    dest = pathlib.Path(args.vosk_path or cfg.asr.vosk.model_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Преузимам {args.vosk_url} …")
    with urllib.request.urlopen(args.vosk_url) as resp:  # noqa: S310
        data = resp.read()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        archive.extractall(dest.parent)
    print(f"Распаковано у {dest.parent}. Провери да путања одговара vosk.model_path.")


def cmd_download(args) -> int:
    cfg = load_config(args.config)
    if args.backend == "faster-whisper":
        from faster_whisper import WhisperModel

        root = cfg.asr.whisper.download_root
        print(f"Преузимам Whisper '{args.model}' у {root} …")
        WhisperModel(args.model, download_root=root or None)
        print("Готово. Систем сада ради офлајн.")
    else:
        _download_vosk(args, cfg)
    return 0


def main(argv=None) -> int:
    _force_utf8()
    logging.basicConfig(format="%(levelname)s %(name)s: %(message)s", level="INFO")
    args = _build_parser().parse_args(argv)
    handlers = {"run": cmd_run, "devices": cmd_devices, "download-model": cmd_download}
    return handlers[args.cmd](args)
