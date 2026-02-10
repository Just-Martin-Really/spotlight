"""
Code task renderer for TIA25 Spotlight.

Renders code snippets with questions like "Find the bug" or
"Which programming language is this?". Uses monospace font without
syntax highlighting for simplicity.

Design principle: Clean code display, easy JSON integration.
"""

import pygame
from config import settings
from src.models.task import CodeTask
from src.views.base_renderer import BaseRenderer
from src.services.renderer_utils import draw_text_centered


class CodeRenderer(BaseRenderer):
    """
    Renderer for code analysis tasks.

    Layout:
    - Question at top
    - Code in monospace font in bordered box
    - Optional note below code
    - Orange/yellow accent color for coding theme
    - Orange glow effect behind content
    """

    def get_glow_config(self, task: CodeTask) -> dict:
        """
        Configure orange glow for code tasks.

        Args:
            task: CodeTask object

        Returns:
            Glow configuration dictionary
        """
        # Using the same orange as the code box border
        CODE_ACCENT_COLOR = (251, 146, 60)  # Orange-400

        return {
            'color': CODE_ACCENT_COLOR,
            'x': self.screen_rect.width // 2,
            'y': self.screen_rect.height // 2,
            'cache_key': 'code'
        }

    def render_content(self, task: CodeTask) -> None:
        """
        Render code snippet with question.

        Args:
            task: CodeTask object to render
        """
        # Type hint for better IDE support
        assert isinstance(task, CodeTask), "CodeRenderer requires CodeTask"

        # Initialize monospace font if not already done
        if not hasattr(self, 'font_mono'):
            self._init_mono_font()

        # Calculate vertical spacing
        # Start position for question
        start_y = settings.PADDING_LARGE + 50

        # Render question
        draw_text_centered(
            self.screen,
            task.question,
            self.font_subtitle,
            settings.COLOR_TEXT_PRIMARY,
            start_y
        )

        # Code section starts below question
        code_start_y = start_y + settings.FONT_SIZE_SUBTITLE + settings.PADDING_LARGE

        # Render code in bordered box
        self._render_code_box(task.code, code_start_y)

        # Render note if present
        if task.note:
            # Position note below code box
            note_y = self.screen_rect.height - settings.PADDING_LARGE - 150

            draw_text_centered(
                self.screen,
                f"💡 {task.note}",
                self.font_body,
                settings.COLOR_TEXT_MUTED,
                note_y
            )

    def _init_mono_font(self) -> None:
        """Initialize monospace font for code display."""
        try:
            self.font_mono = pygame.font.SysFont(
                settings.FONT_FAMILY_MONO,
                settings.FONT_SIZE_BODY,
                bold=False
            )
        except Exception:
            # Fallback to default monospace
            self.font_mono = pygame.font.Font(None, settings.FONT_SIZE_BODY)

    def _render_code_box(self, code: str, start_y: int) -> None:
        """
        Render code in a bordered box with monospace font.

        Args:
            code: Code string (may contain \n for line breaks)
            start_y: Top Y position for code box
        """
        # Split code into lines
        code_lines = code.split('\n')

        # Calculate box dimensions
        line_height = self.font_mono.get_linesize()
        box_padding = settings.PADDING_MEDIUM

        # Render each line to calculate max width
        rendered_lines = []
        max_line_width = 0

        for line in code_lines:
            # Replace empty lines with single space to maintain structure
            display_line = line if line.strip() else " "
            surface = self.font_mono.render(
                display_line,
                True,
                settings.COLOR_TEXT_PRIMARY
            )
            rendered_lines.append(surface)
            max_line_width = max(max_line_width, surface.get_width())

        # Calculate box dimensions
        box_width = min(
            max_line_width + (box_padding * 2),
            self.screen_rect.width - (settings.PADDING_LARGE * 2)
        )
        box_height = (len(code_lines) * line_height) + (box_padding * 2)

        # Create box rectangle (centered horizontally)
        box_x = (self.screen_rect.width - box_width) // 2
        box_rect = pygame.Rect(box_x, start_y, box_width, box_height)

        # Draw box background and border
        # Using orange/amber accent for code
        CODE_ACCENT_COLOR = (251, 146, 60)  # Orange-400

        pygame.draw.rect(self.screen, settings.COLOR_SURFACE, box_rect)
        pygame.draw.rect(
            self.screen,
            CODE_ACCENT_COLOR,
            box_rect,
            settings.BORDER_WIDTH
        )

        # Render code lines inside box
        current_y = start_y + box_padding

        for line_surface in rendered_lines:
            # Left-align code within box (more readable for code)
            line_x = box_x + box_padding
            self.screen.blit(line_surface, (line_x, current_y))
            current_y += line_height