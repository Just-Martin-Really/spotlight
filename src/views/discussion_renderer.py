"""
Discussion task renderer for Spotlight.

Renders open discussion prompts with optional time allocation.
Uses green accent color to indicate collaborative format.

Design principle: Inviting, open layout for audience participation.
"""

from config import settings
from src.models.task import DiscussionTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import wrap_text, draw_text_centered
from src.services.ui_metrics import content_center_y_offset, content_max_width, pad_large, pad_medium, pad_small


class DiscussionRenderer(BaseRenderer):
    """
    Renderer for discussion/spotlight-type tasks.

    Layout:
    - Discussion prompt centered prominently
    - Optional duration indicator
    - Green accent color for positive, collaborative feel
    - Green glow effect behind content
    """

    def get_glow_config(self, task: DiscussionTask) -> dict:
        """
        Configure green glow for discussion tasks.

        Args:
            task: DiscussionTask object

        Returns:
            Glow configuration dictionary
        """
        return {
            'color': settings.COLOR_ACCENT_DISCUSSION,
            'cache_key': 'discussion'
        }

    def render_content(self, task: DiscussionTask) -> None:
        """
        Render discussion prompt and duration.

        Args:
            task: DiscussionTask object to render
        """
        # Type hint for better IDE support
        assert isinstance(task, DiscussionTask), "DiscussionRenderer requires DiscussionTask"

        # Calculate available width for text
        max_width = min(
            content_max_width(),
            self.screen_rect.width - (pad_large() * 2)
        )

        # Wrap prompt text
        prompt_lines = wrap_text(task.prompt, self.font_title, max_width)

        # Calculate vertical position
        # Center the entire content block (prompt + duration)
        title_h = self.font_title.get_linesize()
        subtitle_h = self.font_subtitle.get_linesize()
        small_h = self.font_small.get_linesize()

        total_height = len(prompt_lines) * title_h

        # Add space for duration if present
        if task.spotlight_duration:
            total_height += pad_large() + subtitle_h

        prompt_start_y = (
            (self.screen_rect.height - total_height) // 2 +
            content_center_y_offset()
        )

        # Render "Spotlight" label
        label_y = prompt_start_y - small_h - pad_medium()
        draw_text_centered(
            self.screen,
            "Spotlight Diskussion",
            self.font_small,
            settings.COLOR_ACCENT_DISCUSSION,
            label_y
        )

        # Render prompt lines
        current_y = prompt_start_y
        for line in prompt_lines:
            draw_text_centered(
                self.screen,
                line,
                self.font_title,
                settings.COLOR_TEXT_PRIMARY,
                current_y
            )
            current_y += title_h + pad_small()

        # Render duration if present
        if task.spotlight_duration:
            current_y += pad_medium()

            duration_text = f"{task.spotlight_duration}"
            draw_text_centered(
                self.screen,
                duration_text,
                self.font_subtitle,
                settings.DISCUSSION_TIMER_COLOR,
                current_y
            )