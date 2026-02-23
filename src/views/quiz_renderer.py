"""
Quiz task renderer for Spotlight.

Renders quiz questions with optional notes in a clean, focused layout.
Uses blue accent color to distinguish from other task types.

Design principle: Single responsibility - only renders quiz tasks.
"""

from config import settings

from src.models.task import QuizTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import wrap_text, draw_text_centered_shadow, extract_matrix_block
from src.services.ui_metrics import content_center_y_offset, content_max_width, pad_large, pad_medium, pad_small, border_width
from src.services.ui_scale import ui_scale
import pygame


class QuizRenderer(BaseRenderer):
    """Renderer for quiz-type tasks."""

    def get_glow_config(self, task: QuizTask) -> dict:
        return {
            "color": settings.COLOR_ACCENT_QUIZ,
            "cache_key": "quiz",
        }

    def render_content(self, task: QuizTask, show_note: bool = False) -> None:
        assert isinstance(task, QuizTask), "QuizRenderer requires QuizTask"

        max_width = min(
            content_max_width(),
            self.screen_rect.width - (pad_large() * 2),
        )

        prefix, matrix_lines = extract_matrix_block(task.question)

        # Hard-wrap to avoid projector overflow on long tokens/URLs
        question_lines = wrap_text(prefix or task.question, self.font_title, max_width, hard_wrap=True)

        question_start_y = (
            self.screen_rect.height // 2
            + content_center_y_offset()
            - (len(question_lines) * self.font_title.get_linesize() // 2)
        )

        current_y = question_start_y
        line_h = self.font_title.get_linesize()
        for line in question_lines:
            draw_text_centered_shadow(
                self.screen,
                line,
                self.font_title,
                settings.COLOR_ACCENT_QUIZ,
                current_y,
            )
            current_y += line_h + pad_small()

        if matrix_lines:
            current_y += pad_medium()
            self._render_matrix_box(matrix_lines, current_y, max_width)
            # advance cursor roughly by box height
            current_y += ui_scale(220)

        if show_note and task.note:
            current_y += pad_medium()
            note_lines = wrap_text(task.note, self.font_body, max_width, hard_wrap=True)
            body_h = self.font_body.get_linesize()

            for line in note_lines:
                draw_text_centered_shadow(
                    self.screen,
                    line,
                    self.font_body,
                    settings.QUIZ_NOTE_COLOR,
                    current_y,
                )
                current_y += body_h + pad_small()

    def _render_matrix_box(self, lines: list[str], start_y: int, max_width: int) -> None:
        """Render a matrix-like text block in monospace so columns align."""
        if not hasattr(self, "font_mono"):
            try:
                self.font_mono = pygame.font.SysFont(
                    settings.FONT_FAMILY_MONO,
                    ui_scale(settings.FONT_SIZE_BODY),
                    bold=False,
                )
            except Exception:
                self.font_mono = pygame.font.Font(None, ui_scale(settings.FONT_SIZE_BODY))

        box_padding = pad_small()
        rendered = []
        max_line_w = 0
        for line in lines:
            display_line = line if line.strip() else " "
            s = self.font_mono.render(display_line, True, settings.COLOR_TEXT_PRIMARY)
            rendered.append(s)
            max_line_w = max(max_line_w, s.get_width())

        box_w = min(max_line_w + (box_padding * 2), max_width)
        box_h = sum(s.get_height() for s in rendered) + (box_padding * 2)
        box_x = (self.screen_rect.width - box_w) // 2

        rect = pygame.Rect(box_x, start_y, box_w, box_h)
        pygame.draw.rect(self.screen, settings.COLOR_SURFACE, rect)
        pygame.draw.rect(self.screen, settings.COLOR_ACCENT_QUIZ, rect, border_width())

        y = start_y + box_padding
        for s in rendered:
            self.screen.blit(s, (box_x + box_padding, y))
            y += s.get_height()

