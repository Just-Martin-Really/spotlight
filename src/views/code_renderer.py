"""
Code task renderer for Spotlight.

Renders code snippets with questions like "Find the bug" or
"Which programming language is this?". Uses monospace font without
syntax highlighting for simplicity.

Design principle: Clean code display, easy JSON integration.
"""

import pygame
from config import settings
from src.models.task import CodeTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import draw_text_centered_shadow


class CodeRenderer(BaseRenderer):
    """Renderer for code analysis tasks."""

    def get_glow_config(self, task: CodeTask) -> dict:
        return {
            "color": settings.COLOR_ACCENT_CODE,
            "cache_key": "code",
        }

    def render_content(self, task: CodeTask) -> None:
        assert isinstance(task, CodeTask), "CodeRenderer requires CodeTask"

        if not hasattr(self, "font_mono"):
            self._init_mono_font()

        start_y = settings.PADDING_LARGE + 50

        draw_text_centered_shadow(
            self.screen,
            task.question,
            self.font_subtitle,
            settings.COLOR_TEXT_PRIMARY,
            start_y,
        )

        code_start_y = start_y + settings.FONT_SIZE_SUBTITLE + settings.PADDING_LARGE
        self._render_code_box(task.code, code_start_y)

        if task.note:
            note_y = self.screen_rect.height - settings.PADDING_LARGE - 150
            draw_text_centered_shadow(
                self.screen,
                f"💡 {task.note}",
                self.font_body,
                settings.COLOR_TEXT_MUTED,
                note_y,
            )

    def _init_mono_font(self) -> None:
        """Initialize monospace font for code display."""
        try:
            self.font_mono = pygame.font.SysFont(
                settings.FONT_FAMILY_MONO,
                settings.FONT_SIZE_BODY,
                bold=False,
            )
        except Exception:
            self.font_mono = pygame.font.Font(None, settings.FONT_SIZE_BODY)

    def _render_code_box(self, code: str, start_y: int) -> None:
        """Render code in a bordered box with monospace font."""
        code_lines = code.split("\n")

        line_height = self.font_mono.get_linesize()
        box_padding = settings.PADDING_MEDIUM

        rendered_lines = []
        max_line_width = 0

        for line in code_lines:
            display_line = line if line.strip() else " "
            surface = self.font_mono.render(display_line, True, settings.COLOR_TEXT_PRIMARY)
            rendered_lines.append(surface)
            max_line_width = max(max_line_width, surface.get_width())

        box_width = min(
            max_line_width + (box_padding * 2),
            self.screen_rect.width - (settings.PADDING_LARGE * 2),
        )
        box_height = (len(code_lines) * line_height) + (box_padding * 2)

        box_x = (self.screen_rect.width - box_width) // 2
        box_rect = pygame.Rect(box_x, start_y, box_width, box_height)

        pygame.draw.rect(self.screen, settings.COLOR_SURFACE, box_rect)
        pygame.draw.rect(
            self.screen,
            settings.COLOR_ACCENT_CODE,
            box_rect,
            settings.BORDER_WIDTH,
        )

        current_y = start_y + box_padding
        for line_surface in rendered_lines:
            line_x = box_x + box_padding
            self.screen.blit(line_surface, (line_x, current_y))
            current_y += line_height

