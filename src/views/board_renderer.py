"""Board renderer (Jeopardy-style selection grid)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import pygame

from config import settings
from src.models.board_selection import POINT_ROWS, BoardSelection, Slot
from src.services.ui_metrics import pad_large, pad_medium, pad_small, border_width


@dataclass(frozen=True)
class BoardHitMap:
    rect_slots: List[Tuple[pygame.Rect, Slot]]


def render_board(
    screen: pygame.Surface,
    font_header: pygame.font.Font,
    font_cell: pygame.font.Font,
    selection: BoardSelection,
    solved_task_ids: set[int],
    hover_slot: Slot | None = None,
) -> BoardHitMap:
    screen.fill(settings.COLOR_BACKGROUND)

    w, h = screen.get_size()

    cols = selection.categories
    rows = POINT_ROWS

    top = pad_large()
    left = pad_large()
    right = pad_large()
    bottom = pad_large()

    header_h = font_header.get_linesize() + pad_small() * 2

    grid_w = w - left - right
    grid_h = h - top - bottom - header_h - pad_medium()

    col_w = grid_w // max(1, len(cols))
    row_h = grid_h // max(1, len(rows))

    # Header row
    header_y = top
    for i, cat in enumerate(cols):
        x = left + i * col_w
        rect = pygame.Rect(x, header_y, col_w, header_h)
        pygame.draw.rect(screen, settings.COLOR_SURFACE, rect)
        pygame.draw.rect(screen, settings.COLOR_BORDER, rect, border_width())
        # Center *within the header cell* so it doesn't appear centered across the screen.
        text_s = font_header.render(cat, True, settings.COLOR_TEXT_PRIMARY)
        text_r = text_s.get_rect(center=(rect.centerx, rect.y + rect.height // 2))
        screen.blit(text_s, text_r)

    rect_slots: List[Tuple[pygame.Rect, Slot]] = []

    grid_y0 = top + header_h + pad_medium()

    for r, pts in enumerate(rows):
        for c, cat in enumerate(cols):
            x = left + c * col_w
            y = grid_y0 + r * row_h
            rect = pygame.Rect(x, y, col_w, row_h)

            task_id = selection.task_id_for(cat, pts)
            solved = task_id in solved_task_ids
            hovered = hover_slot == (cat, pts)

            fill = settings.COLOR_SURFACE
            border = settings.COLOR_BORDER
            text_color = settings.COLOR_TEXT_PRIMARY

            if solved:
                fill = (40, 50, 65)
                border = (80, 90, 105)
                text_color = settings.COLOR_TEXT_MUTED
            elif hovered:
                # Subtle hover: brighten border & slightly brighten fill.
                fill = (45, 60, 85)
                border = settings.COLOR_HIGHLIGHT

            pygame.draw.rect(screen, fill, rect)
            pygame.draw.rect(screen, border, rect, border_width())

            # Center points in cell
            label = str(pts)
            text_s = font_cell.render(label, True, text_color)
            text_rect = text_s.get_rect(center=rect.center)
            screen.blit(text_s, text_rect)

            rect_slots.append((rect, (cat, pts)))

    return BoardHitMap(rect_slots=rect_slots)
