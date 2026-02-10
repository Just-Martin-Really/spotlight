"""
Keyboard input configuration for Spotlight.

Centralizes all key bindings in one place for easy remapping.
Decouples pygame key constants from application logic.
"""

import pygame

# =============================================================================
# NAVIGATION KEYS
# =============================================================================

KEY_NEXT = pygame.K_RIGHT  # Navigate to next task
KEY_PREV = pygame.K_LEFT  # Navigate to previous task

# =============================================================================
# APPLICATION CONTROL
# =============================================================================

KEY_QUIT = pygame.K_ESCAPE  # Exit application

# =============================================================================
# FUTURE EXTENSIONS (commented out for now)
# =============================================================================

# KEY_FULLSCREEN_TOGGLE = pygame.K_F11  # Toggle fullscreen mode
# KEY_HELP = pygame.K_h  # Show help overlay
# KEY_JUMP_TO_START = pygame.K_HOME  # Jump to first task
# KEY_JUMP_TO_END = pygame.K_END  # Jump to last task
# KEY_RANDOM = pygame.K_r  # Shuffle to random task
