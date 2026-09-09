"""Испиши одговор у терминал уместо да га изговори — за пробу и рад без звучника."""

from __future__ import annotations

from asistent.tts.base import TtsBackend


class ConsoleTts(TtsBackend):
    def __init__(self, tts_cfg=None) -> None:
        pass

    def say(self, text: str) -> None:
        print(f"\n🔊 {text}\n")
