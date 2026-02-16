"""
Explain-to-audience task renderer for Spotlight.

Renders challenges where participants must explain technical topics
to specific audiences (grandmother, 5-year-old, etc.).

Design principle: Warm, approachable design emphasizing communication.
"""

from config import settings
from src.models.task import ExplainToTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import draw_text_centered_shadow, wrap_text


class ExplainToRenderer(BaseRenderer):
    """Renderer for explain-to-audience tasks."""

    def get_glow_config(self, task: ExplainToTask) -> dict:
        return {
            "color": settings.COLOR_ACCENT_EXPLAIN_TO,
            "cache_key": "explain_to",
        }

    def render_content(self, task: ExplainToTask) -> None:
        assert isinstance(task, ExplainToTask), "ExplainToRenderer requires ExplainToTask"

        center_y = self.screen_rect.height // 2 + settings.CONTENT_CENTER_Y_OFFSET

        instruction_y = center_y - 150
        instruction_text = f"Erkläre {task.audience}:"
        draw_text_centered_shadow(
            self.screen,
            instruction_text,
            self.font_subtitle,
            settings.COLOR_ACCENT_EXPLAIN_TO,
            instruction_y,
        )

        topic_y = instruction_y + settings.FONT_SIZE_SUBTITLE + settings.PADDING_MEDIUM

        max_width = min(
            settings.CONTENT_MAX_WIDTH,
            self.screen_rect.width - (settings.PADDING_LARGE * 2),
        )

        topic_lines = wrap_text(task.topic, self.font_title, max_width, hard_wrap=True)

        current_y = topic_y
        for line in topic_lines:
            draw_text_centered_shadow(
                self.screen,
                line,
                self.font_title,
                settings.COLOR_TEXT_PRIMARY,
                current_y,
            )
            current_y += settings.FONT_SIZE_TITLE + settings.PADDING_SMALL

        if task.note:
            note_y = current_y + settings.PADDING_LARGE
            note_lines = wrap_text(task.note, self.font_body, max_width, hard_wrap=True)

            for line in note_lines:
                draw_text_centered_shadow(
                    self.screen,
                    line,
                    self.font_body,
                    settings.COLOR_TEXT_MUTED,
                    note_y,
                )
                note_y += settings.FONT_SIZE_BODY + settings.PADDING_SMALL
