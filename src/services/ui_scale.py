"""UI scaling helpers.

Goal: separate crispness (UI_RENDER_SCALE) from perceived UI size (UI_SCALE).

- UI_RENDER_SCALE: internal supersampling factor (handled in Application).
- UI_SCALE: multiplies layout constants and font sizes.

This module provides a tiny helper to scale integer pixel values.
"""

from __future__ import annotations

from config import settings


def ui_scale(value: int) -> int:
    scale = float(getattr(settings, "UI_SCALE", 1.0) or 1.0)
    if scale <= 0:
        scale = 1.0
    return max(1, int(round(value * scale)))

