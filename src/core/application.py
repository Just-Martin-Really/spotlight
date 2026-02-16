"""
Main application class for Spotlight.

Orchestrates all components: loading, rendering, input, game loop.
Implements Facade pattern - single entry point for the entire application.

Design principle: High-level coordination, delegates to specialized components.
"""

import sys
import pygame

from config import settings
from src.models.session import Session
from src.services.task_loader import TaskLoader, TaskLoadError
from src.controllers.input_controller import InputController
from src.views.quiz_renderer import QuizRenderer
from src.views.tabu_renderer import TabuRenderer
from src.views.discussion_renderer import DiscussionRenderer
from src.views.code_renderer import CodeRenderer
from src.views.explain_to_renderer import ExplainToRenderer
from src.services.transitions import crossfade


class Application:
    """Main application class - coordinates all subsystems."""

    def __init__(self, task_file: str = "data/tasks.json"):
        self.task_file = task_file
        self.screen = None
        self.clock = None
        self.session = None
        self.input_controller = None
        self.renderers = {}

        # Transition state
        self._frame_surface = None
        self._transition_prev = None
        self._transition_next = None
        self._transition_start_ms = None
        self._last_task_index = 0

    def run(self) -> None:
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
        pygame.init()

        if settings.FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                pygame.FULLSCREEN,
            )
        else:
            self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

        pygame.display.set_caption("Spotlight")
        self.clock = pygame.time.Clock()

        tasks = TaskLoader.load_tasks(self.task_file)
        print(f"Loaded {len(tasks)} tasks")

        self.session = Session(tasks)
        self.input_controller = InputController(self.session)

        # Offscreen surface for rendering frames (for transitions)
        self._frame_surface = pygame.Surface(self.screen.get_size()).convert_alpha()

        self._init_renderers()

        # Render initial frame into the buffer
        self._last_task_index = self.session.current_index
        self._transition_next = self._render_to_surface()
        self.screen.blit(self._transition_next, (0, 0))
        pygame.display.flip()

    def _init_renderers(self) -> None:
        self.renderers = {
            "quiz": QuizRenderer(self._frame_surface),
            "tabu": TabuRenderer(self._frame_surface),
            "discussion": DiscussionRenderer(self._frame_surface),
            "code": CodeRenderer(self._frame_surface),
            "explain_to": ExplainToRenderer(self._frame_surface),
        }

    def _game_loop(self) -> None:
        running = True

        while running:
            running = self.input_controller.handle_events()

            self._render_frame()
            pygame.display.flip()

            self.clock.tick(settings.FPS)

    def _render_to_surface(self) -> pygame.Surface:
        """Render current task to an offscreen surface and return a copy."""
        current_task = self.session.current_task()
        renderer = self.renderers.get(current_task.type)

        self._frame_surface.fill(settings.COLOR_BACKGROUND)

        if renderer is None:
            self._render_error(f"Unknown task type: {current_task.type}")
        else:
            position_info = self.session.get_position_info()
            renderer.render(current_task, position_info)

        return self._frame_surface.copy()

    def _render_frame(self) -> None:
        # Detect task change and start a transition
        if self.session.current_index != self._last_task_index:
            self._transition_prev = self._transition_next or self._render_to_surface()
            self._transition_next = self._render_to_surface()
            self._transition_start_ms = pygame.time.get_ticks()
            self._last_task_index = self.session.current_index

        # If a transition is active, blend frames
        if self._transition_start_ms is not None and self._transition_prev is not None and self._transition_next is not None:
            elapsed = pygame.time.get_ticks() - self._transition_start_ms
            duration = max(1, int(settings.FADE_DURATION))
            progress = min(1.0, max(0.0, elapsed / duration))

            blended = crossfade(self._transition_prev, self._transition_next, progress)
            self.screen.blit(blended, (0, 0))

            if progress >= 1.0:
                self._transition_start_ms = None
                self._transition_prev = None
        else:
            # Normal render (no active transition)
            frame = self._transition_next or self._render_to_surface()
            self.screen.blit(frame, (0, 0))

    def _render_error(self, message: str) -> None:
        self._frame_surface.fill(settings.COLOR_BACKGROUND)
        font = pygame.font.Font(None, 48)
        text_surface = font.render(message, True, settings.COLOR_ACCENT_TABU)
        text_rect = text_surface.get_rect(center=self._frame_surface.get_rect().center)
        self._frame_surface.blit(text_surface, text_rect)

    def _cleanup(self) -> None:
        pygame.quit()
        print("Application closed")


def main():
    """Entry point for console script."""
    app = Application()
    app.run()


if __name__ == "__main__":
    main()

