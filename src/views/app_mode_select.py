"""App mode selection screen.

Lets the presenter choose between:
- Board mode: Jeopardy-style selection board (mouse + fixed points rows)
- Slideshow mode: classic next/prev task flow

Contract
- Inputs: pygame screen, clock
- Output: str | None
  - "board" | "slideshow"
  - None => user aborted

Side effects: draws to screen, consumes pygame events
"""

from __future__ import annotations

import pygame

from config import settings
from src.services.renderer_utils import draw_text_centered_shadow


def run_app_mode_select(screen: pygame.Surface, clock: pygame.time.Clock) -> str | None:
    font_title = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, 56, bold=True)
    font_body = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, 32)

    app_mode = "board" if getattr(settings, "APP_MODE", "slideshow") == "board" else "slideshow"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return None

            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
                app_mode = "slideshow" if app_mode == "board" else "board"

            if event.key == pygame.K_RETURN:
                return app_mode

        screen.fill(settings.COLOR_BACKGROUND)
        draw_text_centered_shadow(screen, "Spotlight — App Mode", font_title, settings.COLOR_TEXT_PRIMARY, 60)

        hint = "UP/DOWN toggle   ENTER confirm   ESC quit"
        draw_text_centered_shadow(screen, hint, font_body, settings.COLOR_TEXT_MUTED, 120)

        y = 240
        a_prefix = ">" if app_mode == "board" else " "
        b_prefix = ">" if app_mode == "slideshow" else " "

        draw_text_centered_shadow(
            screen,
            f"{a_prefix} Board mode (click points tiles)",
            font_body,
            settings.COLOR_TEXT_PRIMARY,
            y,
        )
        y += 70
        draw_text_centered_shadow(
            screen,
            f"{b_prefix} Slideshow mode (←/→ through tasks)",
            font_body,
            settings.COLOR_TEXT_PRIMARY,
            y,
        )

        y += 90
        msg = "Tip: Board mode supports BACKSPACE=board, M=solved, V=reveal"
        draw_text_centered_shadow(screen, msg, font_body, settings.COLOR_TEXT_SECONDARY, y)

        pygame.display.flip()
        clock.tick(settings.FPS)

