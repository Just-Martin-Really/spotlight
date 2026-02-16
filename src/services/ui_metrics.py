"""Scaled UI metrics.

UI_SCALE can be pushed high (e.g., 2.5+) for high-res displays/projectors.
To keep layouts consistent, renderers should use these helpers instead of
raw settings constants for paddings/box sizes/borders.

This intentionally clamps extreme values to prevent negative/absurd layouts.
"""

from __future__ import annotations

from config import settings
from src.services.ui_scale import ui_scale


def pad_large() -> int:
    return ui_scale(settings.PADDING_LARGE)


def pad_medium() -> int:
    return ui_scale(settings.PADDING_MEDIUM)


def pad_small() -> int:
    return ui_scale(settings.PADDING_SMALL)


def border_width() -> int:
    return max(1, ui_scale(settings.BORDER_WIDTH))


def border_radius() -> int:
    return max(0, ui_scale(getattr(settings, "BORDER_RADIUS", 0)))


def content_max_width() -> int:
    # Don't exceed screen width; keep it within a sensible multiple.
    base = ui_scale(settings.CONTENT_MAX_WIDTH)
    return max(300, base)


def content_center_y_offset() -> int:
    # Allow negative offsets; scale magnitude.
    return int(round((getattr(settings, "CONTENT_CENTER_Y_OFFSET", 0)) * float(getattr(settings, "UI_SCALE", 1.0) or 1.0)))

