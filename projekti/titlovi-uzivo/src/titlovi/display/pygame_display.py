"""Приказ титлова преко целог екрана (HDMI) помоћу pygame-а.

Потврђен текст је бео, несигуран „реп" сив. Тастери: ESC/Q излаз, F fullscreen.
"""

from __future__ import annotations

import logging

from titlovi.display.base import Display

log = logging.getLogger(__name__)


class PygameDisplay(Display):
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._quit = False

    def start(self) -> None:
        import pygame

        self._pg = pygame
        pygame.init()
        pygame.display.set_caption("Титлови уживо — без облака")

        if self.cfg.fullscreen:
            info = pygame.display.Info()
            self._screen = pygame.display.set_mode(
                (info.current_w, info.current_h), pygame.FULLSCREEN
            )
            pygame.mouse.set_visible(False)
        else:
            self._screen = pygame.display.set_mode(
                (self.cfg.width, self.cfg.height), pygame.RESIZABLE
            )

        path = self.cfg.font_path or pygame.font.match_font(
            "dejavusans,notosans,freesans,arial,liberationsans"
        )
        self._font = pygame.font.Font(path, self.cfg.font_size)
        self._badge_font = pygame.font.Font(path, max(13, self.cfg.font_size // 3))
        self._fg = pygame.Color(self.cfg.fg)
        self._dim = pygame.Color(self.cfg.dim)
        self._bg = pygame.Color(self.cfg.bg)
        self._clock = pygame.time.Clock()

    def _pump(self) -> None:
        for event in self._pg.event.get():
            if event.type == self._pg.QUIT:
                self._quit = True
            elif event.type == self._pg.KEYDOWN:
                if event.key in (self._pg.K_ESCAPE, self._pg.K_q):
                    self._quit = True
                elif event.key == self._pg.K_f:
                    self._pg.display.toggle_fullscreen()

    def render(self, committed: str, partial: str) -> None:
        self._pump()
        screen = self._screen
        width, height = screen.get_size()
        screen.fill(self._bg)

        margin = self.cfg.margin
        space_w = self._font.size(" ")[0]
        max_w = width - 2 * margin

        tokens = [(w, True) for w in committed.split()] + [(w, False) for w in partial.split()]
        lines: list[list[tuple[str, bool, int]]] = []
        row: list[tuple[str, bool, int]] = []
        row_w = 0
        for word, is_committed in tokens:
            word_w = self._font.size(word)[0]
            advance = word_w + (space_w if row else 0)
            if row and row_w + advance > max_w:
                lines.append(row)
                row, row_w = [], 0
                advance = word_w
            row.append((word, is_committed, word_w))
            row_w += advance
        if row:
            lines.append(row)
        lines = lines[-self.cfg.lines:]

        line_h = self._font.get_linesize()
        y = height - margin - line_h * len(lines)
        for row in lines:
            x = margin
            for word, is_committed, word_w in row:
                surface = self._font.render(word, True, self._fg if is_committed else self._dim)
                screen.blit(surface, (x, y))
                x += word_w + space_w
            y += line_h

        if self.cfg.badge:
            badge = self._badge_font.render("●  ЛОКАЛНО · БЕЗ ОБЛАКА", True, self._dim)
            screen.blit(badge, (margin, margin))

        self._pg.display.flip()
        self._clock.tick(30)

    def should_quit(self) -> bool:
        return self._quit

    def stop(self) -> None:
        try:
            self._pg.quit()
        except Exception:  # pragma: no cover
            pass
