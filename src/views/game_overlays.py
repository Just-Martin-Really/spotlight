"""Game-show overlay rendering.

The functions in this module are intentionally simple and side-effect free
beyond drawing onto the provided surface.
"""

from __future__ import annotations

from typing import Optional

import pygame

from config import settings
from src.models.game_state import BuzzState, GameState
from src.models.session import Session
from src.services.renderer_utils import draw_text_centered_shadow
from src.services.ui_metrics import content_max_width, pad_large, border_width


def _format_ms(ms: int) -> str:
    total_s = max(0, ms) // 1000
    m = total_s // 60
    s = total_s % 60
    return f"{m:02d}:{s:02d}"


def draw_scoreboard(
    surface: pygame.Surface,
    font: pygame.font.Font,
    game_state: GameState,
    selected_team: Optional[int],
) -> None:
    """Draw a compact scoreboard as pill cards at the top."""
    pad = 14
    x = 16
    y = 14

    for idx, team in enumerate(game_state.teams):
        is_selected = selected_team == idx
        is_buzzed = game_state.buzz_state == BuzzState.LOCKED and game_state.buzz_locked_team == idx

        label = f"{idx + 1}  {team.name}:"
        score = str(team.score)

        # Measure
        label_s = font.render(label, True, settings.COLOR_TEXT_PRIMARY)
        score_s = font.render(score, True, settings.COLOR_TEXT_PRIMARY)

        card_h = max(label_s.get_height(), score_s.get_height()) + pad * 2
        card_w = label_s.get_width() + score_s.get_width() + pad * 3 + 10

        card = pygame.Rect(x, y, card_w, card_h)

        # Colors
        fill = settings.COLOR_SURFACE
        border = settings.COLOR_BORDER
        text_color = settings.COLOR_TEXT_PRIMARY

        if is_selected:
            border = settings.COLOR_ACCENT_QUIZ
        if is_buzzed:
            border = settings.COLOR_ACCENT_TABU

        # Draw card
        pygame.draw.rect(surface, fill, card, border_radius=14)
        pygame.draw.rect(surface, border, card, width=2, border_radius=14)

        # Text
        label_s = font.render(label, True, text_color)
        score_s = font.render(score, True, text_color)

        surface.blit(label_s, (card.x + pad, card.y + (card_h - label_s.get_height()) // 2))
        surface.blit(
            score_s,
            (
                card.right - pad - score_s.get_width(),
                card.y + (card_h - score_s.get_height()) // 2,
            ),
        )

        x += card_w + 12


def draw_buzz_status(surface: pygame.Surface, font: pygame.font.Font, game_state: GameState) -> None:
    state = game_state.buzz_state
    if state == BuzzState.CLOSED:
        text = "BUZZ: CLOSED (B=open)"
        color = settings.COLOR_TEXT_MUTED
    elif state == BuzzState.OPEN:
        text = "BUZZ: OPEN (press team #)"
        color = settings.COLOR_ACCENT_DISCUSSION
    else:
        locked = game_state.buzz_locked_team
        name = game_state.teams[locked].name if locked is not None else "?"
        text = f"BUZZ: LOCKED → {name}"
        color = settings.COLOR_ACCENT_TABU

    draw_text_centered_shadow(surface, text, font, color, y_position=20)


def draw_timer(surface: pygame.Surface, font: pygame.font.Font, game_state: GameState) -> None:
    ms = game_state.timer.elapsed_ms
    if game_state.timer.mode.value == "countdown" and game_state.timer.remaining_ms() is not None:
        ms = game_state.timer.remaining_ms() or 0

    state = "RUN" if game_state.timer.running else "PAUSE"
    text = f"{state} {_format_ms(ms)}"

    rendered = font.render(text, True, settings.COLOR_TEXT_SECONDARY)
    rect = rendered.get_rect(topright=(surface.get_width() - 20, 20))
    surface.blit(rendered, rect)


def draw_status_message(surface: pygame.Surface, font: pygame.font.Font, game_state: GameState) -> None:
    if not game_state.status_message:
        return
    draw_text_centered_shadow(
        surface,
        game_state.status_message,
        font,
        settings.COLOR_TEXT_PRIMARY,
        y_position=surface.get_height() - pad_large() - 120,
    )


def draw_roster_overlay(
    surface: pygame.Surface,
    font: pygame.font.Font,
    session: Session,
    visible_count: int = 8,
) -> None:
    """Draw a simple roster list of upcoming tasks with difficulty."""
    w, h = surface.get_size()
    box_w = min(content_max_width(), w - 2 * pad_large())
    box_h = int(h * 0.55)
    box_x = (w - box_w) // 2
    box_y = int(pad_large() * 1.2)

    box = pygame.Rect(box_x, box_y, box_w, box_h)
    overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    surface.blit(overlay, (box_x, box_y))
    pygame.draw.rect(surface, settings.COLOR_BORDER, box, border_width())

    title = "ROSTER (Tab to close)"
    title_s = font.render(title, True, settings.COLOR_TEXT_PRIMARY)
    surface.blit(title_s, (box_x + 20, box_y + 20))

    start = session.current_index
    y = box_y + 70

    for offset in range(visible_count):
        idx = (start + offset) % len(session.tasks)
        task = session.tasks[idx]
        marker = "→" if idx == session.current_index else " "
        line = f"{marker} {idx + 1:02d}. [{task.type}] diff={task.difficulty}"
        s = font.render(line, True, settings.COLOR_TEXT_SECONDARY)
        surface.blit(s, (box_x + 20, y))
        y += s.get_height() + 6


def draw_help_overlay(surface: pygame.Surface, font: pygame.font.Font) -> None:
    w, h = surface.get_size()
    box_w = min(content_max_width(), w - 2 * pad_large())
    box_h = int(h * 0.55)
    box_x = (w - box_w) // 2
    box_y = int(pad_large() * 1.2)

    box = pygame.Rect(box_x, box_y, box_w, box_h)
    overlay = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (box_x, box_y))
    pygame.draw.rect(surface, settings.COLOR_BORDER, box, border_width())

    lines = [
        "HELP (H to close)",
        "← / →  : previous / next task",
        "1..9   : select team (disabled while BUZZ LOCKED)",
        "B      : open buzz",
        "R      : reset buzz",
        "F      : fail (reopen buzz + block team for this task)",
        "V      : reveal/hide (Tabu)",
        "ENTER  : award points (= task difficulty)",
        "\\     : penalty (subtract difficulty)",
        "SPACE  : timer start/pause",
        "BACKSP : timer reset",
        "TAB    : roster",
        "S / L  : save / load",
        "ESC    : quit",
    ]

    y = box_y + 20
    for i, line in enumerate(lines):
        color = settings.COLOR_TEXT_PRIMARY if i == 0 else settings.COLOR_TEXT_SECONDARY
        s = font.render(line, True, color)
        surface.blit(s, (box_x + 20, y))
        y += s.get_height() + 10


def draw_help_hint(surface: pygame.Surface, font: pygame.font.Font) -> None:
    text = "H for help"
    s = font.render(text, True, settings.COLOR_TEXT_MUTED)
    rect = s.get_rect(bottomright=(surface.get_width() - 18, surface.get_height() - 18))
    surface.blit(s, rect)
