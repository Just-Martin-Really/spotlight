"""
Main application class for TIA25 Spotlight.

Orchestrates all components: loading, rendering, input, game loop.
Implements Facade pattern - single entry point for the entire application.

Design principle: High-level coordination, delegates to specialized components.
"""

import sys
import pygame
from pathlib import Path

from config import settings
from src.models.session import Session
from src.models.task import QuizTask, TabuTask, DiscussionTask
from src.services.task_loader import TaskLoader, TaskLoadError
from src.controllers.input_controller import InputController
from src.views.quiz_renderer import QuizRenderer
from src.views.tabu_renderer import TabuRenderer
from src.views.discussion_renderer import DiscussionRenderer


class Application:
    """
    Main application class - coordinates all subsystems.
    
    Responsibilities:
    - Initialize pygame
    - Load tasks from JSON
    - Create session
    - Manage renderer factory
    - Run main game loop
    - Handle cleanup
    """
    
    def __init__(self, task_file: str = "data/tasks.json"):
        """
        Initialize the application.
        
        Args:
            task_file: Path to JSON file containing tasks
        """
        self.task_file = task_file
        self.screen = None
        self.clock = None
        self.session = None
        self.input_controller = None
        self.renderers = {}
        
    def run(self) -> None:
        """
        Main entry point - initialize and start the game loop.
        
        This is the only public method needed to run the entire application.
        """
        try:
            self._initialize()
            self._game_loop()
        except TaskLoadError as e:
            print(f"Error loading tasks: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            self._cleanup()
    
    def _initialize(self) -> None:
        """Initialize all subsystems."""
        # Initialize pygame
        pygame.init()
        
        # Create display
        if settings.FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
            )
        
        pygame.display.set_caption("TIA25 Spotlight")
        
        # Create clock for FPS control
        self.clock = pygame.time.Clock()
        
        # Load tasks
        tasks = TaskLoader.load_tasks(self.task_file)
        print(f"Loaded {len(tasks)} tasks")
        
        # Create session
        self.session = Session(tasks)
        
        # Create input controller
        self.input_controller = InputController(self.session)
        
        # Initialize renderers (factory pattern)
        self._init_renderers()
    
    def _init_renderers(self) -> None:
        """
        Initialize renderer instances for all task types.
        
        Creates a mapping from task types to their respective renderers.
        This implements a simple factory pattern.
        """
        self.renderers = {
            "quiz": QuizRenderer(self.screen),
            "tabu": TabuRenderer(self.screen),
            "discussion": DiscussionRenderer(self.screen),
        }
    
    def _game_loop(self) -> None:
        """
        Main game loop.
        
        Runs until user quits:
        1. Handle input
        2. Render current task
        3. Update display
        4. Control frame rate
        """
        running = True
        
        while running:
            # Handle input events
            running = self.input_controller.handle_events()
            
            # Render current task
            self._render_frame()
            
            # Update display
            pygame.display.flip()
            
            # Maintain frame rate
            self.clock.tick(settings.FPS)
    
    def _render_frame(self) -> None:
        """
        Render a complete frame with the current task.
        
        Selects appropriate renderer based on task type and
        delegates rendering to it.
        """
        # Get current task
        current_task = self.session.current_task()
        
        # Get appropriate renderer for this task type
        renderer = self.renderers.get(current_task.type)
        
        if renderer is None:
            # Fallback for unknown task types
            print(f"Warning: No renderer for task type '{current_task.type}'")
            self._render_error(f"Unknown task type: {current_task.type}")
            return
        
        # Render the task
        position_info = self.session.get_position_info()
        renderer.render(current_task, position_info)
    
    def _render_error(self, message: str) -> None:
        """
        Render an error message on screen.
        
        Args:
            message: Error message to display
        """
        self.screen.fill(settings.COLOR_BACKGROUND)
        
        font = pygame.font.Font(None, 48)
        text_surface = font.render(message, True, settings.COLOR_ACCENT_TABU)
        text_rect = text_surface.get_rect(center=self.screen.get_rect().center)
        
        self.screen.blit(text_surface, text_rect)
    
    def _cleanup(self) -> None:
        """Clean up resources and quit pygame."""
        pygame.quit()
        print("Application closed")


def main():
    """Entry point for console script."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
