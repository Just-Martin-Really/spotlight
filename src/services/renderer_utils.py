"""
Rendering utility functions for Spotlight.

Provides reusable text wrapping, centering, and drawing functions.
Implements DRY principle - shared rendering logic used by all renderers.

Design principle: Pure utility functions, no state, no side effects.
"""

from typing import List, Tuple
import pygame


def _split_long_word(word: str, font: pygame.font.Font, max_width: int) -> List[str]:
    """Split a single long token into chunks that fit max_width."""
    if not word:
        return [""]

    chunks: List[str] = []
    current = ""
    for ch in word:
        test = current + ch
        if current and font.size(test)[0] > max_width:
            chunks.append(current)
            current = ch
        else:
            current = test

    if current:
        chunks.append(current)

    return chunks


def wrap_text(text: str, font: pygame.font.Font, max_width: int, hard_wrap: bool = False) -> List[str]:
    """
    Wrap text to fit within a maximum width.

    Breaks text into multiple lines at word boundaries to ensure
    no line exceeds max_width when rendered with the given font.

    If hard_wrap is True, a single word/token that exceeds max_width
    will be split into smaller chunks.

    Args:
        text: Text to wrap
        font: Pygame font object to use for width calculation
        max_width: Maximum width in pixels
        hard_wrap: Whether to split long tokens that exceed max_width

    Returns:
        List of text lines that fit within max_width
    """
    words = text.split(" ")
    lines: List[str] = []
    current_line: List[str] = []

    for word in words:
        # Optional: split long tokens up-front so they can be wrapped
        word_parts = [word]
        if hard_wrap and word and font.size(word)[0] > max_width:
            word_parts = _split_long_word(word, font, max_width)

        for part in word_parts:
            # Try adding this word to current line
            test_line = " ".join(current_line + [part]) if current_line else part
            test_width = font.size(test_line)[0]

            if test_width <= max_width:
                current_line.append(part)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [part]
                else:
                    # Single word is too long - add it anyway (legacy behavior)
                    lines.append(part)

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def center_text_block(
    lines: List[str],
    font: pygame.font.Font,
    screen_rect: pygame.Rect,
    y_offset: int = 0
) -> List[Tuple[pygame.Surface, pygame.Rect]]:
    """
    Center a block of text lines on screen.

    Calculates vertical and horizontal centering for multiple lines
    of text, treating them as a cohesive block.

    Args:
        lines: List of text strings to center
        font: Font to render text with
        screen_rect: Screen rectangle for centering calculation
        y_offset: Vertical offset from center (positive = down)

    Returns:
        List of (text_surface, rect) tuples ready to blit
    """
    if not lines:
        return []

    # Render all lines to get their dimensions
    rendered_lines = []
    total_height = 0
    max_width = 0

    for line in lines:
        surface = font.render(line, True, (255, 255, 255))  # Color will be set later
        rendered_lines.append(surface)
        total_height += surface.get_height()
        max_width = max(max_width, surface.get_width())

    # Calculate starting Y position for vertical centering
    start_y = (screen_rect.height - total_height) // 2 + y_offset

    # Position each line
    result = []
    current_y = start_y

    for surface in rendered_lines:
        # Center horizontally
        x = (screen_rect.width - surface.get_width()) // 2
        rect = surface.get_rect(topleft=(x, current_y))
        result.append((surface, rect))
        current_y += surface.get_height()

    return result


def draw_text_centered(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    y_position: int
) -> None:
    """Draw a single line of text centered horizontally."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(centerx=surface.get_width() // 2, top=y_position)
    surface.blit(text_surface, text_rect)


def draw_text_centered_shadow(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    y_position: int,
    shadow_color: Tuple[int, int, int] = (0, 0, 0),
    shadow_offset: Tuple[int, int] = (2, 2),
) -> None:
    """Draw centered text with a subtle drop shadow for better projector readability."""
    shadow_surface = font.render(text, True, shadow_color)
    shadow_rect = shadow_surface.get_rect(
        centerx=surface.get_width() // 2,
        top=y_position,
    )
    shadow_rect.move_ip(shadow_offset)
    surface.blit(shadow_surface, shadow_rect)

    draw_text_centered(surface, text, font, color, y_position)


def draw_bordered_box(
    surface: pygame.Surface,
    rect: pygame.Rect,
    fill_color: Tuple[int, int, int],
    border_color: Tuple[int, int, int],
    border_width: int = 2
) -> None:
    """Draw a filled rectangle with a border."""
    pygame.draw.rect(surface, fill_color, rect)
    pygame.draw.rect(surface, border_color, rect, border_width)


def get_multiline_text_height(lines: List[str], font: pygame.font.Font) -> int:
    """Calculate total height of multiple lines of text."""
    if not lines:
        return 0

    line_height = font.size(lines[0])[1]
    return line_height * len(lines)
