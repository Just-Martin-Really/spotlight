"""
Quiz task renderer for Spotlight.

Renders quiz questions with optional notes in a clean, focused layout.
Uses blue accent color to distinguish from other task types.

Design principle: Single responsibility - only renders quiz tasks.
"""

import pygame
from config import settings
from src.models.task import QuizTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import wrap_text, draw_text_centered_shadow


class QuizRenderer(BaseRenderer):
    """Renderer for quiz-type tasks."""

    def get_glow_config(self, task: QuizTask) -> dict:
        return {
            "color": settings.COLOR_ACCENT_QUIZ,
            "cache_key": "quiz",
        }

    def render_content(self, task: QuizTask) -> None:
        assert isinstance(task, QuizTask), "QuizRenderer requires QuizTask"

        max_width = min(
            settings.CONTENT_MAX_WIDTH,
            self.screen_rect.width - (settings.PADDING_LARGE * 2),
        )

        # Hard-wrap to avoid projector overflow on long tokens/URLs
        question_lines = wrap_text(task.question, self.font_title, max_width, hard_wrap=True)

        question_start_y = (
            self.screen_rect.height // 2
            + settings.CONTENT_CENTER_Y_OFFSET
            - (len(question_lines) * settings.FONT_SIZE_TITLE // 2)
        )

        current_y = question_start_y
        for line in question_lines:
            draw_text_centered_shadow(
                self.screen,
                line,
                self.font_title,
                settings.COLOR_ACCENT_QUIZ,
                current_y,
            )
            current_y += settings.FONT_SIZE_TITLE + settings.PADDING_SMALL

        if task.note:
            current_y += settings.PADDING_MEDIUM
            note_lines = wrap_text(task.note, self.font_body, max_width, hard_wrap=True)

            for line in note_lines:
                draw_text_centered_shadow(
                    self.screen,
                    line,
                    self.font_body,
                    settings.QUIZ_NOTE_COLOR,
                    current_y,
                )
                current_y += settings.FONT_SIZE_BODY + settings.PADDING_SMALL