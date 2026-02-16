"""Scene transition helpers.

Implements simple, deterministic transitions between frames.

Contract
- Inputs:
  - prev_surface: previous fully-rendered frame (same size as screen)
  - next_surface: next fully-rendered frame
  - progress: float in [0.0, 1.0]
- Output:
  - A new surface representing the blended frame

Side effects: none (pure function for testability)
"""

from __future__ import annotations

import pygame


def crossfade(prev_surface: pygame.Surface, next_surface: pygame.Surface, progress: float) -> pygame.Surface:
    """Crossfade two surfaces.

    Args:
        prev_surface: previous frame surface
        next_surface: next frame surface
        progress: 0.0 shows prev_surface, 1.0 shows next_surface

    Returns:
        New blended surface.

    Raises:
        ValueError: if surface sizes differ or progress is out of range
    """

    if prev_surface.get_size() != next_surface.get_size():
        raise ValueError("Surfaces must have the same size")
    if not (0.0 <= progress <= 1.0):
        raise ValueError("progress must be between 0.0 and 1.0")

    out = pygame.Surface(prev_surface.get_size()).convert_alpha()
    out.fill((0, 0, 0, 0))

    # Draw previous frame
    out.blit(prev_surface, (0, 0))

    # Draw next frame with alpha
    alpha = int(255 * progress)
    next_copy = next_surface.copy()
    next_copy.set_alpha(alpha)
    out.blit(next_copy, (0, 0))

    return out

