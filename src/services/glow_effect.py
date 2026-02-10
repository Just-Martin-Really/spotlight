"""
Glow effect service for TIA25 Spotlight.

Provides performant glow rendering behind content areas.
Uses layered circles for gaussian-like blur approximation.

Design principle: Performance-first, subtle visual enhancement.
"""

import pygame
from typing import Tuple
from config import settings


class GlowEffect:
    """
    Service for rendering glow effects behind content.

    Implements a multi-layer radial gradient to simulate glow.
    Effects are cached per task type for performance.
    """

    def __init__(self):
        """Initialize glow effect cache."""
        self._glow_cache = {}

    def render_centered_glow(
            self,
            surface: pygame.Surface,
            color: Tuple[int, int, int],
            center_x: int,
            center_y: int,
            cache_key: str = None
    ) -> None:
        """
        Render a glow effect centered at specified position.

        Args:
            surface: Surface to draw on
            color: RGB color for glow (task accent color)
            center_x: X coordinate of glow center
            center_y: Y coordinate of glow center
            cache_key: Optional cache key (e.g., task type)
        """
        if not settings.GLOW_ENABLED:
            return

        # Check cache if key provided
        if cache_key and cache_key in self._glow_cache:
            glow_surface = self._glow_cache[cache_key]
        else:
            # Create new glow surface
            glow_surface = self._create_glow_surface(color)

            # Cache if key provided
            if cache_key:
                self._glow_cache[cache_key] = glow_surface

        # Calculate position to center the glow
        glow_rect = glow_surface.get_rect(
            center=(center_x, center_y)
        )

        # Blit glow surface
        surface.blit(glow_surface, glow_rect, special_flags=pygame.BLEND_RGBA_ADD)

    def _create_glow_surface(
            self,
            color: Tuple[int, int, int]
    ) -> pygame.Surface:
        """
        Create a glow surface with layered circles.

        Args:
            color: RGB color for glow

        Returns:
            Transparent surface with glow effect
        """
        # Create surface with alpha channel
        size = settings.GLOW_RADIUS * 2
        glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Center point
        center = (settings.GLOW_RADIUS, settings.GLOW_RADIUS)

        # Draw layered circles from outer to inner
        # Each layer gets smaller radius and higher alpha
        for i in range(settings.GLOW_LAYERS):
            # Calculate this layer's properties
            layer_progress = (i + 1) / settings.GLOW_LAYERS

            # Radius decreases from GLOW_RADIUS to ~30% of it
            radius = int(settings.GLOW_RADIUS * (1 - layer_progress * 0.7))

            # Alpha increases from low to GLOW_INTENSITY
            alpha = int(settings.GLOW_INTENSITY * layer_progress)

            # Create color with alpha
            glow_color = (*color, alpha)

            # Draw circle
            pygame.draw.circle(
                glow_surface,
                glow_color,
                center,
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
        center_x: int,
        center_y: int,
        cache_key: str = None
) -> None:
    """
    Convenience function to render glow effect.

    Args:
        surface: Surface to draw on
        color: RGB color for glow
        center_x: X coordinate of glow center
        center_y: Y coordinate of glow center
        cache_key: Optional cache key for performance
    """
    _glow_effect.render_centered_glow(surface, color, center_x, center_y, cache_key)


def clear_glow_cache() -> None:
    """Clear the glow effect cache."""
    _glow_effect.clear_cache()