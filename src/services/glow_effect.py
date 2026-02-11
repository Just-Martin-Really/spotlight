"""
Glow effect service for Spotlight.

Provides subtle background glow effect behind content.
Creates a large, soft gradient overlay across the screen.

Design principle: Ambient background lighting, not spotlights.
"""

import pygame
from typing import Tuple, Optional
from config import settings


class GlowEffect:
    """
    Service for rendering ambient background glow effects.

    Creates large, soft gradient overlays that fill the screen
    with subtle colored light behind content.
    """

    def __init__(self):
        """Initialize glow effect cache."""
        self._glow_cache = {}

    def render_background_glow(
        self,
        surface: pygame.Surface,
        color: Tuple[int, int, int],
        cache_key: str = None
    ) -> None:
        """
        Render a large background glow effect across entire screen.

        Args:
            surface: Surface to draw on
            color: RGB color for glow (task accent color)
            cache_key: Optional cache key (e.g., task type)
        """
        if not settings.GLOW_ENABLED:
            return

        # Check cache if key provided
        if cache_key and cache_key in self._glow_cache:
            glow_surface = self._glow_cache[cache_key]
        else:
            # Create new glow surface
            glow_surface = self._create_background_glow(surface.get_size(), color)

            # Cache if key provided
            if cache_key:
                self._glow_cache[cache_key] = glow_surface

        # Blit at origin - glow surface is full screen size
        surface.blit(glow_surface, (0, 0))

    def _create_background_glow(
        self,
        screen_size: Tuple[int, int],
        color: Tuple[int, int, int]
    ) -> pygame.Surface:
        """
        Create a large background glow surface.

        Strategy:
        1. Create full-screen surface
        2. Draw large radial gradient from center
        3. Make it subtle with low alpha

        Args:
            screen_size: Screen dimensions (width, height)
            color: RGB color for glow

        Returns:
            Transparent surface with background glow
        """
        width, height = screen_size

        # Create full-screen surface with alpha
        glow_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        glow_surface.fill((0, 0, 0, 0))

        # Center point
        center_x = width // 2
        center_y = height // 2

        # Calculate maximum radius to cover screen
        max_radius = int(((width ** 2 + height ** 2) ** 0.5) / 2)

        # Draw radial gradient with many layers
        # More layers = smoother gradient
        num_layers = 50

        for i in range(num_layers, 0, -1):
            # Progress from outer (0.0) to inner (1.0)
            progress = i / num_layers

            # Radius decreases from max to a small core
            radius = int(max_radius * progress)

            # Alpha increases towards center but stays subtle
            # Use quadratic falloff for more natural glow
            alpha = int(settings.GLOW_INTENSITY * (1 - progress) ** 2)

            # Don't draw if alpha would be 0
            if alpha < 1:
                continue

            # Create color with calculated alpha
            glow_color = (*color, alpha)

            # Draw filled circle for this layer
            pygame.draw.circle(
                glow_surface,
                glow_color,
                (center_x, center_y),
                radius
            )

        return glow_surface

    def clear_cache(self) -> None:
        """Clear the glow cache (useful when changing settings)."""
        self._glow_cache.clear()


# Global glow effect instance (singleton pattern)
_glow_effect = GlowEffect()


def render_glow(
    surface: pygame.Surface,
    color: Tuple[int, int, int],
    cache_key: str = None
) -> None:
    """
    Convenience function to render background glow effect.

    Args:
        surface: Surface to draw on
        color: RGB color for glow
        cache_key: Optional cache key for performance
    """
    _glow_effect.render_background_glow(surface, color, cache_key)


def clear_glow_cache() -> None:
    """Clear the glow effect cache."""
    _glow_effect.clear_cache()