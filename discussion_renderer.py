"""
Discussion task renderer for TIA25 Spotlight.

Renders open discussion prompts with optional time allocation.
Uses green accent color to indicate collaborative format.

Design principle: Inviting, open layout for audience participation.
"""

import pygame
from config import settings
from src.models.task import DiscussionTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import wrap_text, draw_text_centered


class DiscussionRenderer(BaseRenderer):
    """
    Renderer for discussion/spotlight-type tasks.
    
    Layout:
    - Discussion prompt centered prominently
    - Optional duration indicator
    - Green accent color for positive, collaborative feel
    """
    
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
            settings.CONTENT_MAX_WIDTH,
            self.screen_rect.width - (settings.PADDING_LARGE * 2)
        )
        
        # Wrap prompt text
        prompt_lines = wrap_text(task.prompt, self.font_title, max_width)
        
        # Calculate vertical position
        # Center the entire content block (prompt + duration)
        total_height = len(prompt_lines) * settings.FONT_SIZE_TITLE
        
        # Add space for duration if present
        if task.spotlight_duration:
            total_height += settings.PADDING_LARGE + settings.FONT_SIZE_SUBTITLE
        
        prompt_start_y = (
            (self.screen_rect.height - total_height) // 2 +
            settings.CONTENT_CENTER_Y_OFFSET
        )
        
        # Render "Spotlight" label
        label_y = prompt_start_y - settings.FONT_SIZE_SMALL - settings.PADDING_MEDIUM
        draw_text_centered(
            self.screen,
            "💡 Spotlight Diskussion",
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
            current_y += settings.FONT_SIZE_TITLE + settings.PADDING_SMALL
        
        # Render duration if present
        if task.spotlight_duration:
            current_y += settings.PADDING_MEDIUM
            
            duration_text = f"⏱️  {task.spotlight_duration}"
            draw_text_centered(
                self.screen,
                duration_text,
                self.font_subtitle,
                settings.DISCUSSION_TIMER_COLOR,
                current_y
            )
