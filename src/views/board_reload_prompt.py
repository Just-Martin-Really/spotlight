"""Board reload prompt screen.

Contract
- Inputs: pygame screen, clock
- Output: bool | None
  - True  => reload previous board
  - False => start a new board
  - None  => user aborted

Side effects: draws to screen, consumes pygame events

Why this exists
- The board reload prompt previously lived inside the main game loop.
  On some systems/window-focus situations it could appear "stuck".
  This screen uses the same dedicated-loop pattern as other startup screens.
"""

from __future__ import annotations

import pygame

from config import settings
from src.services.renderer_utils import draw_text_centered_shadow
from src.services.ui_scale import ui_scale


def run_board_reload_prompt(screen: pygame.Surface, clock: pygame.time.Clock) -> bool | None:
    # Flush any queued events from prior startup screens so we don't accidentally
    # process stale KEYDOWNs here.
    pygame.event.clear()

    font_title = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(56), bold=True)
    font_body = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(32))

    # Default to reload (safer against reshuffle).
    reload_choice = True

    # Some systems can deliver repeated KEYDOWNs (or suppressed KEYUPs) depending
    # on key repeat settings. Avoid this by disabling repeat while the prompt is
    # active, and by requiring ENTER to be released before we accept another.
    pygame.key.set_repeat()  # disable
    enter_is_down = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    enter_is_down = False
                continue

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return None

            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
                reload_choice = not reload_choice

            if event.key == pygame.K_RETURN:
                if enter_is_down:
                    continue
                enter_is_down = True
                return reload_choice

        # Keep pygame's event system responsive.
        pygame.event.pump()

        screen.fill(settings.COLOR_BACKGROUND)
        draw_text_centered_shadow(screen, "Reload previous board?", font_title, settings.COLOR_TEXT_PRIMARY, ui_scale(80))
        draw_text_centered_shadow(
            screen,
            "UP/DOWN toggle   ENTER confirm   ESC quit",
            font_body,
            settings.COLOR_TEXT_SECONDARY,
            ui_scale(150),
        )

        y = ui_scale(260)
        a_prefix = ">" if reload_choice else " "
        b_prefix = ">" if not reload_choice else " "
        draw_text_centered_shadow(
            screen,
            f"{a_prefix} Reload last board (keeps random tasks)",
            font_body,
            settings.COLOR_TEXT_PRIMARY,
            y,
        )
        y += ui_scale(70)
        draw_text_centered_shadow(
            screen,
            f"{b_prefix} Start new board (reshuffle once)",
            font_body,
            settings.COLOR_TEXT_PRIMARY,
            y,
        )

        pygame.display.flip()
        clock.tick(settings.FPS)
