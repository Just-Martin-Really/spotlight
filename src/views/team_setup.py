"""Startup team setup screen.

This is intentionally simple: choose number of teams and enter names
before the session starts.

Controls
- Up/Down: change team count (2..8)
- Enter: confirm
- Esc: quit
- Type: edit current team name
- Tab: switch to next team name field
- Backspace: delete

Contract
- Inputs: pygame screen, clock
- Output: list[str] team names (len 2..8)
- Side effects: draws to screen, consumes pygame events
"""

from __future__ import annotations

import pygame

from config import settings
from src.services.renderer_utils import draw_text_centered_shadow


def run_team_setup(screen: pygame.Surface, clock: pygame.time.Clock) -> list[str] | None:
    pygame.key.set_repeat(250, 35)

    count = 4
    names = ["Team A", "Team B", "Team C", "Team D"]
    active_idx = 0

    font_title = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, 56, bold=True)
    font_body = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return None

            # More intuitive: DOWN = more teams, UP = fewer teams
            if event.key == pygame.K_DOWN:
                count = min(8, count + 1)
                while len(names) < count:
                    names.append(f"Team {chr(ord('A') + len(names))}")
                active_idx = min(active_idx, count - 1)

            elif event.key == pygame.K_UP:
                count = max(2, count - 1)
                active_idx = min(active_idx, count - 1)

            elif event.key in (pygame.K_TAB, pygame.K_RETURN):
                if event.key == pygame.K_RETURN:
                    cleaned = [n.strip() for n in names[:count]]
                    if any(not n for n in cleaned):
                        # refuse empty
                        pass
                    else:
                        return cleaned
                else:
                    active_idx = (active_idx + 1) % count

            elif event.key == pygame.K_BACKSPACE:
                names[active_idx] = names[active_idx][:-1]

            else:
                if event.unicode and event.unicode.isprintable():
                    # small cap to avoid ridiculous inputs
                    if len(names[active_idx]) < 20:
                        names[active_idx] += event.unicode

        # --- render ---
        screen.fill(settings.COLOR_BACKGROUND)
        draw_text_centered_shadow(screen, "WOW MODE — Team Setup", font_title, settings.COLOR_TEXT_PRIMARY, 60)

        hint = "↓/↑ Teams   TAB Next name   ENTER Start   ESC Quit"
        draw_text_centered_shadow(screen, hint, font_body, settings.COLOR_TEXT_MUTED, 120)

        draw_text_centered_shadow(
            screen,
            f"Teams: {count}",
            font_body,
            settings.COLOR_TEXT_SECONDARY,
            180,
        )

        y = 260
        for i in range(count):
            prefix = ">" if i == active_idx else " "
            text = f"{prefix} {i+1}. {names[i]}"
            color = settings.COLOR_ACCENT_QUIZ if i == active_idx else settings.COLOR_TEXT_PRIMARY
            draw_text_centered_shadow(screen, text, font_body, color, y)
            y += 48

        pygame.display.flip()
        clock.tick(settings.FPS)

