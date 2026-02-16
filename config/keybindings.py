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
# GAME SHOW (WOW MODE)
# =============================================================================

# Team selection (1..9 supported)
KEY_TEAM_1 = pygame.K_1
KEY_TEAM_2 = pygame.K_2
KEY_TEAM_3 = pygame.K_3
KEY_TEAM_4 = pygame.K_4
KEY_TEAM_5 = pygame.K_5
KEY_TEAM_6 = pygame.K_6
KEY_TEAM_7 = pygame.K_7
KEY_TEAM_8 = pygame.K_8
KEY_TEAM_9 = pygame.K_9

# Award / penalty
KEY_AWARD = pygame.K_RETURN  # award difficulty points to buzzed/selected team
KEY_PENALTY = pygame.K_BACKSLASH  # subtract difficulty points

# Buzz-in
KEY_BUZZ_OPEN = pygame.K_b
KEY_BUZZ_RESET = pygame.K_r
KEY_BUZZ_FAIL = pygame.K_f  # mark current buzz-locked team as failed; reopen buzz and block them

# Timer
KEY_TIMER_TOGGLE = pygame.K_SPACE
KEY_TIMER_RESET = pygame.K_BACKSPACE

# Overlays
KEY_TOGGLE_ROSTER = pygame.K_TAB
KEY_TOGGLE_HELP = pygame.K_h

# Tabu safety / reveals
KEY_TOGGLE_REVEAL = pygame.K_v  # toggle reveal (used e.g. for tabu placeholder)

# Persistence
KEY_SAVE = pygame.K_s
KEY_LOAD = pygame.K_l
