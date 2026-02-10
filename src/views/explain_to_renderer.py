"""
Explain-to-audience task renderer for TIA25 Spotlight.

Renders challenges where participants must explain technical topics
to specific audiences (grandmother, 5-year-old, etc.).

Design principle: Warm, approachable design emphasizing communication.
"""

import pygame
from config import settings
from src.models.task import ExplainToTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import draw_text_centered, wrap_text


class ExplainToRenderer(BaseRenderer):
    """
    Renderer for explain-to-audience tasks.

    Layout:
    - "Erkläre..." instruction with audience prominently
    - Topic in large text
    - Optional note with hints
    - Purple accent color for creative/communication theme
    """

    def render_content(self, task: ExplainToTask) -> None:
        """
        Render explain-to challenge.

        Args:
            task: ExplainToTask object to render
        """
        # Type hint for better IDE support
        assert isinstance(task, ExplainToTask), "ExplainToRenderer requires ExplainToTask"

        # Purple/violet accent for communication theme
        EXPLAIN_ACCENT_COLOR = (168, 85, 247)  # Purple-500

        # Calculate vertical spacing
        center_y = self.screen_rect.height // 2 + settings.CONTENT_CENTER_Y_OFFSET

        # Render "Erkläre [audience]:" instruction
        instruction_y = center_y - 150

        instruction_text = f"Erkläre {task.audience}:"
        draw_text_centered(
            self.screen,
            instruction_text,
            self.font_subtitle,
            EXPLAIN_ACCENT_COLOR,
            instruction_y
        )

        # Render topic prominently
        topic_y = instruction_y + settings.FONT_SIZE_SUBTITLE + settings.PADDING_MEDIUM

        # Calculate available width
        max_width = min(
            settings.CONTENT_MAX_WIDTH,
            self.screen_rect.width - (settings.PADDING_LARGE * 2)
        )

        # Wrap topic if too long
        topic_lines = wrap_text(task.topic, self.font_title, max_width)

        current_y = topic_y
        for line in topic_lines:
            draw_text_centered(
                self.screen,
                line,
                self.font_title,
                settings.COLOR_TEXT_PRIMARY,
                current_y
            )
            current_y += settings.FONT_SIZE_TITLE + settings.PADDING_SMALL

        # Render note if present
        if task.note:
            note_y = current_y + settings.PADDING_LARGE

            # Wrap note
            note_lines = wrap_text(task.note, self.font_body, max_width)

            for line in note_lines:
                draw_text_centered(
                    self.screen,
                    line,
                    self.font_body,
                    settings.COLOR_TEXT_MUTED,
                    note_y
                )
                note_y += settings.FONT_SIZE_BODY + settings.PADDING_SMALL