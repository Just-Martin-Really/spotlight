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
from src.services.renderer_utils import wrap_text, draw_text_centered


class QuizRenderer(BaseRenderer):
    """
    Renderer for quiz-type tasks.

    Layout:
    - Large centered question
    - Optional note below in smaller, muted text
    - Blue accent color scheme
    - Blue glow effect behind content
    """

    def get_glow_config(self, task: QuizTask) -> dict:
        """
        Configure blue glow for quiz tasks.

        Args:
            task: QuizTask object

        Returns:
            Glow configuration dictionary
        """
        return {
            'color': settings.COLOR_ACCENT_QUIZ,
            'cache_key': 'quiz'
        }

    def render_content(self, task: QuizTask) -> None:
        """
        Render quiz question and optional note.

        Args:
            task: QuizTask object to render
        """
        # Type hint for better IDE support
        assert isinstance(task, QuizTask), "QuizRenderer requires QuizTask"

        # Calculate available width for text
        max_width = min(
            settings.CONTENT_MAX_WIDTH,
            self.screen_rect.width - (settings.PADDING_LARGE * 2)
        )

        # Wrap question text
        question_lines = wrap_text(task.question, self.font_title, max_width)

        # Calculate vertical position for question
        # Start higher on screen to leave room for note if present
        question_start_y = (
            self.screen_rect.height // 2 +
            settings.CONTENT_CENTER_Y_OFFSET -
            (len(question_lines) * settings.FONT_SIZE_TITLE // 2)
        )

        # Render question lines
        current_y = question_start_y
        for line in question_lines:
            draw_text_centered(
                self.screen,
                line,
                self.font_title,
                settings.COLOR_ACCENT_QUIZ,  # Blue accent for quiz
                current_y
            )
            current_y += settings.FONT_SIZE_TITLE + settings.PADDING_SMALL

        # Render note if present
        if task.note:
            current_y += settings.PADDING_MEDIUM

            # Wrap note text
            note_lines = wrap_text(task.note, self.font_body, max_width)

            for line in note_lines:
                draw_text_centered(
                    self.screen,
                    line,
                    self.font_body,
                    settings.QUIZ_NOTE_COLOR,  # Muted color for notes
                    current_y
                )
                current_y += settings.FONT_SIZE_BODY + settings.PADDING_SMALL