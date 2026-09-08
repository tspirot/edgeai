"""Приказ у терминалу — за пробу и рад без екрана."""

from __future__ import annotations

import sys

from titlovi.display.base import Display


class ConsoleDisplay(Display):
    def __init__(self, cfg=None) -> None:
        self._width = 110

    def render(self, committed: str, partial: str) -> None:
        line = f"{committed} {partial}".strip()
        if len(line) > self._width:
            line = "…" + line[-(self._width - 1):]
        sys.stdout.write("\r\033[2K" + line)
        sys.stdout.flush()

    def stop(self) -> None:
        sys.stdout.write("\n")
        sys.stdout.flush()
