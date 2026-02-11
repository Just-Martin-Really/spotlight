"""
Configuration settings for Spotlight application.

This module contains all visual, layout, and performance settings.
Acts as Single Source of Truth for the entire application's appearance.
"""

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

SCREEN_WIDTH = 1920  # Full HD width
SCREEN_HEIGHT = 1080  # Full HD height
FPS = 60  # Frames per second - smooth animations
FULLSCREEN = True  # Set to False for windowed mode during development

# =============================================================================
# COLOR PALETTE
# =============================================================================

# Background colors
COLOR_BACKGROUND = (15, 23, 42)  # Dark blue-gray (slate-900)
COLOR_SURFACE = (30, 41, 59)  # Lighter surface color (slate-800)

# Text colors
COLOR_TEXT_PRIMARY = (248, 250, 252)  # Off-white (slate-50)
COLOR_TEXT_SECONDARY = (203, 213, 225)  # Gray-white (slate-300)
COLOR_TEXT_MUTED = (148, 163, 184)  # Muted gray (slate-400)

# Accent colors per task type
COLOR_ACCENT_QUIZ = (59, 130, 246)  # Blue-500 - Quiz questions
COLOR_ACCENT_TABU = (239, 68, 68)  # Red-500 - Forbidden words
COLOR_ACCENT_DISCUSSION = (34, 197, 94)  # Green-500 - Open discussion

# UI elements
COLOR_BORDER = (71, 85, 105)  # Slate-600
COLOR_HIGHLIGHT = (100, 116, 139)  # Slate-500

# =============================================================================
# TYPOGRAPHY
# =============================================================================

# Font families (fallback to pygame defaults if not available)
FONT_FAMILY_PRIMARY = "Arial"  # Clean, readable sans-serif
FONT_FAMILY_MONO = "Courier New"  # For code snippets if needed

# Font sizes
FONT_SIZE_TITLE = 72  # Main task title/question
FONT_SIZE_SUBTITLE = 48  # Secondary information
FONT_SIZE_BODY = 36  # Body text, notes
FONT_SIZE_SMALL = 28  # Footer, metadata
FONT_SIZE_TINY = 20  # Navigation hints

# =============================================================================
# LAYOUT & SPACING
# =============================================================================

# Padding and margins
PADDING_LARGE = 80  # Screen edges
PADDING_MEDIUM = 40  # Between sections
PADDING_SMALL = 20  # Between lines

# Content area
CONTENT_MAX_WIDTH = 1600  # Maximum width for text blocks
CONTENT_CENTER_Y_OFFSET = -50  # Shift content slightly up for better visual balance

# Border and box styling
BORDER_WIDTH = 4
BORDER_RADIUS = 12  # Rounded corners (if implemented)

# =============================================================================
# ANIMATION & TIMING
# =============================================================================

FADE_DURATION = 300  # Milliseconds for fade transitions (future feature)
TRANSITION_SPEED = 0.15  # Smooth transition coefficient

# =============================================================================
# TASK-SPECIFIC SETTINGS
# =============================================================================

# Tabu task settings
TABU_FORBIDDEN_BOX_COLOR = COLOR_ACCENT_TABU
TABU_FORBIDDEN_BOX_ALPHA = 30  # Transparency (0-255)

# Quiz task settings
QUIZ_NOTE_COLOR = COLOR_TEXT_MUTED

# Discussion task settings
DISCUSSION_TIMER_COLOR = COLOR_ACCENT_DISCUSSION

# =============================================================================
# VISUAL EFFECTS
# =============================================================================

# Glow effect settings
GLOW_ENABLED = True  # Set to False to disable glow for performance
GLOW_INTENSITY = 100  # Alpha value (5-30 recommended for subtle background glow)

# Note: GLOW_RADIUS and GLOW_LAYERS are not used in background glow mode
# The glow automatically covers the entire screen with a radial gradient