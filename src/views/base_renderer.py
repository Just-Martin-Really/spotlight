"""
Base renderer for Spotlight.

Provides common rendering infrastructure for all task types.
Implements Template Method pattern - subclasses override render_content().

Design principle: Abstract base class with shared setup logic.
"""

from abc import ABC, abstractmethod
import pygame
from config import settings
from src.models.task import BaseTask
from src.services.renderer_utils import draw_text_centered


class BaseRenderer(ABC):
    """
    Abstract base class for all task renderers.
    
    Handles screen setup, background, header/footer, and provides
    template method for content rendering.
    
    Subclasses must implement render_content() for task-specific layout.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Initialize the renderer.
        
        Args:
            screen: Pygame display surface to render on
        """
        self.screen = screen
        self.screen_rect = screen.get_rect()
        
        # Initialize fonts (cached for performance)
        self._init_fonts()
    
    def _init_fonts(self) -> None:
        """Initialize all fonts used by renderers."""
        try:
            self.font_title = pygame.font.SysFont(
                settings.FONT_FAMILY_PRIMARY,
                settings.FONT_SIZE_TITLE,
                bold=True
            )
            self.font_subtitle = pygame.font.SysFont(
                settings.FONT_FAMILY_PRIMARY,
                settings.FONT_SIZE_SUBTITLE
            )
            self.font_body = pygame.font.SysFont(
                settings.FONT_FAMILY_PRIMARY,
                settings.FONT_SIZE_BODY
            )
            self.font_small = pygame.font.SysFont(
                settings.FONT_FAMILY_PRIMARY,
                settings.FONT_SIZE_SMALL
            )
            self.font_tiny = pygame.font.SysFont(
                settings.FONT_FAMILY_PRIMARY,
                settings.FONT_SIZE_TINY
            )
        except Exception as e:
            # Fallback to pygame default font if system fonts fail
            print(f"Warning: Could not load system fonts, using defaults: {e}")
            self.font_title = pygame.font.Font(None, settings.FONT_SIZE_TITLE)
            self.font_subtitle = pygame.font.Font(None, settings.FONT_SIZE_SUBTITLE)
            self.font_body = pygame.font.Font(None, settings.FONT_SIZE_BODY)
            self.font_small = pygame.font.Font(None, settings.FONT_SIZE_SMALL)
            self.font_tiny = pygame.font.Font(None, settings.FONT_SIZE_TINY)
    
    def render(self, task: BaseTask, position_info: str) -> None:
        """
        Render a complete frame with task content.
        
        Template method - defines the overall rendering sequence:
        1. Clear screen with background
        2. Render header
        3. Render task-specific content (delegated to subclass)
        4. Render footer with navigation
        
        Args:
            task: Task object to render
            position_info: Current position string (e.g., "3 / 12")
        """
        # Clear screen
        self.screen.fill(settings.COLOR_BACKGROUND)
        
        # Render task-specific content (implemented by subclass)
        self.render_content(task)
        
        # Render footer with navigation info
        self._render_footer(position_info)
    
    @abstractmethod
    def render_content(self, task: BaseTask) -> None:
        """
        Render task-specific content.
        
        This method must be implemented by subclasses to provide
        custom layout for different task types.
        
        Args:
            task: Task object to render
        """
        pass
    
    def _render_footer(self, position_info: str) -> None:
        """
        Render footer with navigation hints and position.
        
        Args:
            position_info: Position string like "3 / 12"
        """
        footer_y = self.screen_rect.height - settings.PADDING_LARGE
        
        # Navigation hints
        nav_text = "◄ Zurück  |  Weiter ►  |  ESC = Beenden"
        draw_text_centered(
            self.screen,
            nav_text,
            self.font_tiny,
            settings.COLOR_TEXT_MUTED,
            footer_y - 40
        )
        
        # Position indicator
        draw_text_centered(
            self.screen,
            position_info,
            self.font_small,
            settings.COLOR_TEXT_SECONDARY,
            footer_y
        )
