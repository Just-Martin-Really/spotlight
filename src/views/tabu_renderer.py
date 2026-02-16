"""
Tabu task renderer for Spotlight.

Renders explanation tasks with forbidden words prominently displayed.
Uses red accent color to emphasize restrictions.

Design principle: Visual clarity for game rules.
"""

import pygame
from config import settings
from src.models.task import TabuTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import draw_text_centered, draw_bordered_box
from src.services.ui_metrics import content_center_y_offset, content_max_width, pad_large, pad_medium, pad_small, border_width


class TabuRenderer(BaseRenderer):
    """
    Renderer for tabu/explain-type tasks.

    Layout:
    - Topic at top in large text
    - "Verbotene Wörter:" label
    - Forbidden words in a bordered box with red accent
    - Red glow effect behind content
    """

    def get_glow_config(self, task: TabuTask) -> dict:
        """
        Configure red glow for tabu tasks.

        Args:
            task: TabuTask object

        Returns:
            Glow configuration dictionary
        """
        return {
            'color': settings.COLOR_ACCENT_TABU,
            'cache_key': 'tabu'
        }

    def render_content(self, task: TabuTask, hidden: bool = False) -> None:
        """Render topic and forbidden words list, or a safe placeholder."""
        assert isinstance(task, TabuTask), "TabuRenderer requires TabuTask"

        if hidden:
            self._render_placeholder()
            return

        # Calculate vertical spacing
        start_y = (
            self.screen_rect.height // 2 +
            content_center_y_offset() - pad_large() * 2
        )

        # Render topic
        draw_text_centered(
            self.screen,
            f"Erkläre: {task.topic}",
            self.font_title,
            settings.COLOR_TEXT_PRIMARY,
            start_y
        )

        # Spacing before forbidden words section
        forbidden_y = start_y + self.font_title.get_linesize() + pad_large()

        # Render "Forbidden words" label
        draw_text_centered(
            self.screen,
            "Verbotene Wörter:",
            self.font_subtitle,
            settings.COLOR_ACCENT_TABU,  # Red accent
            forbidden_y
        )

        # Render forbidden words in a box
        self._render_forbidden_box(
            task.forbidden_words,
            forbidden_y + self.font_subtitle.get_linesize() + pad_medium()
        )

    def _render_placeholder(self) -> None:
        """Render a safe placeholder screen for hidden Tabu tasks."""
        start_y = (
            self.screen_rect.height // 2 +
            content_center_y_offset() - pad_large()
        )

        draw_text_centered(
            self.screen,
            "Tabu",
            self.font_title,
            settings.COLOR_TEXT_PRIMARY,
            start_y,
        )
        draw_text_centered(
            self.screen,
            "Press V to reveal",
            self.font_body,
            settings.COLOR_TEXT_MUTED,
            start_y + self.font_title.get_linesize() + pad_medium(),
        )

    def _render_forbidden_box(self, words: list, start_y: int) -> None:
        """
        Render forbidden words in a bordered box.

        Args:
            words: List of forbidden words
            start_y: Top Y position for the box
        """
        # Join words with bullets
        word_text = "  •  ".join(words)

        # Calculate box dimensions
        max_width = min(
            content_max_width(),
            self.screen_rect.width - (pad_large() * 2)
        )

        # Render word text
        word_surface = self.font_body.render(
            word_text,
            True,
            settings.COLOR_ACCENT_TABU
        )

        # Check if text fits on one line
        if word_surface.get_width() > max_width:
            # Split into multiple lines if too wide
            # Simple approach: split in half
            mid = len(words) // 2
            line1 = "  •  ".join(words[:mid])
            line2 = "  •  ".join(words[mid:])

            # Render both lines
            current_y = start_y + pad_medium()
            for line in [line1, line2]:
                draw_text_centered(
                    self.screen,
                    line,
                    self.font_body,
                    settings.COLOR_ACCENT_TABU,
                    current_y
                )
                current_y += self.font_body.get_linesize() + pad_small()

        else:
            box_padding = pad_medium()

            # Create box around text
            box_width = word_surface.get_width() + (box_padding * 2)
            box_height = word_surface.get_height() + (box_padding * 2)

            box_rect = pygame.Rect(
                (self.screen_rect.width - box_width) // 2,
                start_y,
                box_width,
                box_height
            )

            # Draw bordered box
            draw_bordered_box(
                self.screen,
                box_rect,
                settings.COLOR_SURFACE,
                settings.COLOR_ACCENT_TABU,
                border_width()
            )

            # Draw text inside box
            text_rect = word_surface.get_rect(center=box_rect.center)
            self.screen.blit(word_surface, text_rect)
