"""
Input controller for TIA25 Spotlight.

Translates pygame keyboard events into application actions.
Decouples pygame event handling from business logic.

Design principle: Controller pattern - mediates between UI and model.
"""

import pygame
from src.models.session import Session
from config import keybindings


class InputController:
    """
    Handles keyboard input and translates it to session actions.
    
    Implements Command pattern - each key press triggers a specific
    action on the session object.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the input controller.
        
        Args:
            session: Session object to control
        """
        self.session = session
    
    def handle_events(self) -> bool:
        """
        Process all pending pygame events.
        
        Polls the event queue and translates relevant events
        (keyboard input) into session state changes.
        
        Returns:
            True if application should continue running,
            False if quit was requested
        """
        for event in pygame.event.get():
            # Handle window close button
            if event.type == pygame.QUIT:
                return False
            
            # Handle keyboard input
            if event.type == pygame.KEYDOWN:
                if not self._handle_keydown(event.key):
                    return False
        
        return True
    
    def _handle_keydown(self, key: int) -> bool:
        """
        Handle a key press event.
        
        Args:
            key: Pygame key constant
            
        Returns:
            True to continue running, False to quit
        """
        # Quit application
        if key == keybindings.KEY_QUIT:
            return False
        
        # Navigate to next task
        elif key == keybindings.KEY_NEXT:
            self.session.next_task()
        
        # Navigate to previous task
        elif key == keybindings.KEY_PREV:
            self.session.prev_task()
        
        # Unknown key - ignore
        # (We don't handle every possible key, only mapped ones)
        
        return True
