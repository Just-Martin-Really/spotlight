"""
Main application class for Spotlight.

Orchestrates all components: loading, rendering, input, game loop.
Implements Facade pattern - single entry point for the entire application.

Design principle: High-level coordination, delegates to specialized components.
"""

import sys
import pygame

from config import settings
from src.controllers.commands import CommandType
from src.models.game_show import award_points_for_current_task
from src.models.game_state import GameState
from src.models.session import Session
from src.models.reveal_state import RevealState
from src.models.scoring_state import ScoringState
from src.services.game_state_store import GameStateStoreError, load_state, save_state
from src.services.task_loader import TaskLoader, TaskLoadError
from src.controllers.input_controller import InputController
from src.views.quiz_renderer import QuizRenderer
from src.views.tabu_renderer import TabuRenderer
from src.views.discussion_renderer import DiscussionRenderer
from src.views.code_renderer import CodeRenderer
from src.views.explain_to_renderer import ExplainToRenderer
from src.services.transitions import crossfade
from src.views.game_overlays import (
    draw_buzz_status,
    draw_help_hint,
    draw_help_overlay,
    draw_roster_overlay,
    draw_scoreboard,
    draw_status_message,
    draw_timer,
)
from src.views.team_setup import run_team_setup


class Application:
    """Main application class - coordinates all subsystems."""

    def __init__(self, task_file: str = "data/tasks.json"):
        self.task_file = task_file
        self.screen = None
        self.clock = None
        self.session = None
        self.input_controller = None
        self.renderers = {}

        # WOW state
        self.game_state: GameState | None = None
        self.selected_team: int | None = None
        self.show_roster = False
        self.show_help = False
        self._game_state_path = "data/game_state.json"

        # Transition state
        self._frame_surface = None
        self._transition_prev = None
        self._transition_next = None
        self._transition_start_ms = None
        self._last_task_index = 0

        # Base slide cache (task content only, no dynamic overlays)
        self._base_frame = None

        # Per-task reveal state
        self.reveal_state = RevealState()

        # Scoring state
        self.scoring_state = ScoringState()

        # Internal rendering (supersampling)
        self._render_canvas = None
        self._render_scale = 1.0
        self._display_size = None

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

        # Decide internal render scale
        self._render_scale = float(getattr(settings, "UI_RENDER_SCALE", 1.0) or 1.0)
        self._render_scale = max(1.0, min(2.0, self._render_scale))
        self._display_size = self.screen.get_size()

        # Create internal render canvas (supersampled)
        if self._render_scale > 1.0:
            w, h = self._display_size
            rw, rh = int(w * self._render_scale), int(h * self._render_scale)
            self._render_canvas = pygame.Surface((rw, rh)).convert_alpha()
        else:
            self._render_canvas = self.screen

        # Startup setup: choose teams/names
        team_names = run_team_setup(self.screen, self.clock)
        if team_names is None:
            raise SystemExit(0)

        self.game_state = GameState.with_teams(team_names)
        self.selected_team = 0

        tasks = TaskLoader.load_tasks(self.task_file)
        print(f"Loaded {len(tasks)} tasks")

        self.session = Session(tasks)
        self.input_controller = InputController(self.session)

        # Offscreen surface for rendering frames (for transitions)
        # NOTE: transitions and renderers target the internal canvas size.
        self._frame_surface = pygame.Surface(self._render_canvas.get_size()).convert_alpha()

        self._init_renderers()

        # Render initial frame into the buffer
        self._last_task_index = self.session.current_index
        self._transition_next = self._render_to_surface()
        self._blit_to_screen(self._transition_next)
        pygame.display.flip()

    def _blit_to_screen(self, rendered: pygame.Surface) -> None:
        """Blit rendered surface to the actual display, scaling if needed."""
        if self._render_scale <= 1.0:
            self.screen.blit(rendered, (0, 0))
            return

        assert self._display_size is not None
        scaled = pygame.transform.smoothscale(rendered, self._display_size)
        self.screen.blit(scaled, (0, 0))

    def _init_renderers(self) -> None:
        self.renderers = {
            "quiz": QuizRenderer(self._frame_surface),
            "tabu": TabuRenderer(self._frame_surface),
            "discussion": DiscussionRenderer(self._frame_surface),
            "code": CodeRenderer(self._frame_surface),
            "explain_to": ExplainToRenderer(self._frame_surface),
        }

    def _apply_command(self, cmd, now_ms: int) -> None:
        assert self.game_state is not None

        # If an overlay is open, prioritize closing it.
        if cmd.type == CommandType.TOGGLE_ROSTER:
            self.show_roster = not self.show_roster
            if self.show_roster:
                self.show_help = False
            return

        if cmd.type == CommandType.TOGGLE_HELP:
            self.show_help = not self.show_help
            if self.show_help:
                self.show_roster = False
            return

        if cmd.type == CommandType.SELECT_TEAM:
            # Once a team buzzed and is locked-in, don't allow manual switching.
            if self.game_state.buzz_state == self.game_state.buzz_state.LOCKED:
                return
            if cmd.team_index is not None and 0 <= cmd.team_index < len(self.game_state.teams):
                self.selected_team = cmd.team_index
                self.game_state.set_status(f"Selected: {self.game_state.teams[cmd.team_index].name}", now_ms)

        elif cmd.type == CommandType.BUZZ:
            if cmd.team_index is not None:
                if self.game_state.buzz(cmd.team_index, now_ms=now_ms):
                    # Auto-focus the buzzed team.
                    self.selected_team = cmd.team_index
                    self._base_frame = None

        elif cmd.type == CommandType.BUZZ_FAIL:
            # Reopen buzz and block the failing team for this task.
            self.game_state.fail_locked_team_and_reopen(now_ms=now_ms)
            self._base_frame = None

        elif cmd.type == CommandType.AWARD:
            task = self.session.current_task()
            task_id = int(task.id) if task.id is not None else None

            if task_id is not None and self.scoring_state.is_awarded(task_id):
                self.game_state.set_status("Already awarded", now_ms)
                return

            # Determine who would receive points before trying.
            target_team = self.game_state.buzz_locked_team
            if target_team is None:
                target_team = self.selected_team

            if target_team is None:
                self.game_state.set_status("No team selected", now_ms)
                return

            if target_team in self.game_state.buzz_blocked_teams:
                self.game_state.set_status(f"BLOCKED: {self.game_state.teams[target_team].name}", now_ms)
                return

            awarded_team = award_points_for_current_task(self.session, self.game_state, self.selected_team, now_ms)
            if awarded_team is None:
                return

            # Only now we lock the task as awarded.
            if task_id is not None:
                self.scoring_state.mark_awarded(task_id)

            # After a successful award, close the buzzer lock.
            self.game_state.reset_buzz(now_ms)

        elif cmd.type == CommandType.PENALTY:
            task = self.session.current_task()
            assert task.difficulty is not None
            points = int(task.difficulty)

            team_index = self.game_state.buzz_locked_team
            if team_index is None:
                team_index = self.selected_team
            if team_index is None:
                self.game_state.set_status("No team selected", now_ms)
            else:
                # Penalties also don't apply to blocked teams (handled by GameState.add_points)
                self.game_state.add_points(team_index, -points, now_ms=now_ms)

        elif cmd.type == CommandType.BUZZ_OPEN:
            self.game_state.open_buzz(now_ms)

        elif cmd.type == CommandType.BUZZ_RESET:
            self.game_state.reset_buzz(now_ms)

        elif cmd.type == CommandType.TIMER_TOGGLE:
            self.game_state.timer_start_pause_toggle(now_ms)

        elif cmd.type == CommandType.TIMER_RESET:
            self.game_state.timer_reset(now_ms)

        elif cmd.type == CommandType.SAVE:
            try:
                save_state(self._game_state_path, self.game_state)
                self.game_state.set_status("Saved", now_ms)
            except GameStateStoreError as e:
                self.game_state.set_status(str(e), now_ms)

        elif cmd.type == CommandType.LOAD:
            try:
                self.game_state = load_state(self._game_state_path)
                # Clamp selection
                self.selected_team = min(self.selected_team or 0, len(self.game_state.teams) - 1)
                self.game_state.set_status("Loaded", now_ms)
            except GameStateStoreError as e:
                self.game_state.set_status(str(e), now_ms)

        elif cmd.type == CommandType.TOGGLE_REVEAL:
            task = self.session.current_task()
            if task.id is not None:
                revealed = self.reveal_state.toggle(int(task.id))
                self.game_state.set_status("Revealed" if revealed else "Hidden", now_ms)
                # Base slide content changed (Tabu placeholder vs real content).
                self._base_frame = None
            return

    def _game_loop(self) -> None:
        running = True

        while running:
            now_ms = pygame.time.get_ticks()

            running, commands = self.input_controller.poll_commands()
            if not running:
                break

            if self.game_state is not None:
                self.game_state.tick(now_ms)

            for cmd in commands:
                if self.game_state is not None:
                    self._apply_command(cmd, now_ms)

            self._render_frame()
            pygame.display.flip()

            self.clock.tick(settings.FPS)

    def _render_base_slide(self) -> pygame.Surface:
        """Render current task (static content) to an offscreen surface and return a copy.

        This excludes dynamic overlays (timer/buzz/status/roster/help) so we can
        redraw overlays every frame without re-rendering the whole slide.
        """
        current_task = self.session.current_task()
        renderer = self.renderers.get(current_task.type)

        self._frame_surface.fill(settings.COLOR_BACKGROUND)

        if renderer is None:
            self._render_error(f"Unknown task type: {current_task.type}")
        else:
            position_info = self.session.get_position_info()

            if current_task.type == "tabu" and current_task.id is not None:
                hidden = not self.reveal_state.is_revealed(int(current_task.id))
                # Render via TabuRenderer with explicit hidden flag.
                if isinstance(renderer, TabuRenderer):
                    renderer.render(current_task, position_info)  # clears + glow + footer
                    # Re-render content area with placeholder if hidden.
                    # Minimal change: call render_content directly to override content.
                    if hidden:
                        self._frame_surface.fill(settings.COLOR_BACKGROUND)
                        glow_config = renderer.get_glow_config(current_task)
                        if glow_config:
                            from src.services.glow_effect import render_glow
                            render_glow(self._frame_surface, glow_config['color'], glow_config.get('cache_key'))
                        renderer.render_content(current_task, hidden=True)
                        renderer._render_footer(position_info)
                else:
                    renderer.render(current_task, position_info)
            else:
                renderer.render(current_task, position_info)

        return self._frame_surface.copy()

    def _render_overlay(self, target_surface: pygame.Surface) -> None:
        """Draw dynamic game overlays onto the given surface."""
        if self.game_state is None:
            return

        current_task = self.session.current_task()
        renderer = self.renderers.get(current_task.type)
        if renderer is None:
            return

        draw_scoreboard(target_surface, renderer.font_small, self.game_state, self.selected_team)
        draw_timer(target_surface, renderer.font_small, self.game_state)
        draw_buzz_status(target_surface, renderer.font_tiny, self.game_state)
        draw_status_message(target_surface, renderer.font_small, self.game_state)
        draw_help_hint(target_surface, renderer.font_tiny)

        if self.show_roster:
            draw_roster_overlay(target_surface, renderer.font_small, self.session)
        if self.show_help:
            draw_help_overlay(target_surface, renderer.font_small)

    def _render_to_surface(self) -> pygame.Surface:
        """Legacy wrapper: render base slide plus overlays."""
        base = self._render_base_slide()
        self._render_overlay(base)
        return base

    def _render_frame(self) -> None:
        # Detect task change and start a transition.
        if self.session.current_index != self._last_task_index:
            # Reset reveal state for new task (safe default)
            prev_task = self.session.tasks[self._last_task_index]
            if prev_task.id is not None:
                self.reveal_state.reset(int(prev_task.id))

            new_task = self.session.current_task()
            if new_task.id is not None:
                self.reveal_state.reset(int(new_task.id))
                # NOTE: scoring_state is intentionally NOT reset here.
                # Awarding is per-task and must remain locked even if the user
                # loops back to the same task via circular navigation.

            # New task => clear buzz blocks (blocked teams are per-task)
            if self.game_state is not None:
                self.game_state.clear_buzz_blocks()

            # Cache previous base frame and render the next base frame
            prev = self._base_frame or self._render_base_slide()
            self._base_frame = self._render_base_slide()

            self._transition_prev = prev
            self._transition_next = self._base_frame
            self._transition_start_ms = pygame.time.get_ticks()
            self._last_task_index = self.session.current_index

        # If a transition is active, blend base slides
        if (
            self._transition_start_ms is not None
            and self._transition_prev is not None
            and self._transition_next is not None
        ):
            elapsed = pygame.time.get_ticks() - self._transition_start_ms
            duration = max(1, int(settings.FADE_DURATION))
            progress = min(1.0, max(0.0, elapsed / duration))

            blended = crossfade(self._transition_prev, self._transition_next, progress)
            self._render_overlay(blended)
            self._blit_to_screen(blended)

            if progress >= 1.0:
                self._transition_start_ms = None
                self._transition_prev = None
        else:
            # No active transition: reuse cached base frame and redraw overlays every frame.
            if self._base_frame is None:
                self._base_frame = self._render_base_slide()
            frame = self._base_frame.copy()
            self._render_overlay(frame)
            self._blit_to_screen(frame)

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

