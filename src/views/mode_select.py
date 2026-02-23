"""Startup mode selection screen.

Lets the presenter choose between:
- Game show mode: teams + buzzer + scoring
- Presenter mode: no teams/buzzer/scoring (timer still available)

Contract
- Inputs: pygame screen, clock
- Output: bool | None
  - True  => enable game show mode
  - False => presenter mode
  - None  => user aborted

Side effects: draws to screen, consumes pygame events
"""

from __future__ import annotations

import pygame

from config import settings
from src.services.renderer_utils import draw_text_centered_shadow


def run_mode_select(screen: pygame.Surface, clock: pygame.time.Clock) -> bool | None:
    font_title = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, 56, bold=True)
    font_body = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, 32)

    # Default to full game-show mode.
    enable_game_show = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return None

            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
                enable_game_show = not enable_game_show

            if event.key == pygame.K_RETURN:
                return enable_game_show

        # --- render ---
        screen.fill(settings.COLOR_BACKGROUND)
        draw_text_centered_shadow(screen, "Spotlight — Startup Mode", font_title, settings.COLOR_TEXT_PRIMARY, 60)

        hint = "UP/DOWN toggle   ENTER confirm   ESC quit"
        draw_text_centered_shadow(screen, hint, font_body, settings.COLOR_TEXT_MUTED, 120)

        y = 240
        a_prefix = ">" if enable_game_show else " "
        b_prefix = ">" if not enable_game_show else " "

        draw_text_centered_shadow(
            screen,
            f"{a_prefix} Game show mode (teams + buzzer + scoring)",
            font_body,
            settings.COLOR_TEXT_PRIMARY,
            y,
        )
        y += 70
        draw_text_centered_shadow(
            screen,
            f"{b_prefix} Presenter mode (no teams / no points)",
            font_body,
            settings.COLOR_TEXT_PRIMARY,
            y,
        )

        y += 90
        msg = "You can still use: ←/→, SPACE, BACKSP, V, H"
        draw_text_centered_shadow(screen, msg, font_body, settings.COLOR_TEXT_SECONDARY, y)

        pygame.display.flip()
        clock.tick(settings.FPS)

