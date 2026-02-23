"""
Main application class for Spotlight.

Orchestrates all components: loading, rendering, input, game loop.
Implements Facade pattern - single entry point for the entire application.

Design principle: High-level coordination, delegates to specialized components.
"""

import sys
import pygame
import time

from config import settings
from src.controllers.commands import CommandType
from src.models.game_show import award_points_for_current_task
from src.models.game_state import GameState
from src.models.session import Session
from src.models.reveal_state import RevealState
from src.models.scoring_state import ScoringState
from src.models.presentation_mode import PresentationConfig
from src.models.board_selection import build_board_selection, BoardSelectionError
from src.models.board_selection import BoardSelection
from src.models.board_state import BoardState
from src.services.board_state_store import BoardStateStoreError, load_board_state, save_board_state
from src.services.task_fingerprint import sha256_of_file
from src.services.game_state_store import GameStateStoreError, load_state, save_state
from src.services.task_loader import TaskLoader, TaskLoadError
from src.controllers.input_controller import InputController
from src.views.quiz_renderer import QuizRenderer
from src.views.tabu_renderer import TabuRenderer
from src.views.discussion_renderer import DiscussionRenderer
from src.views.code_renderer import CodeRenderer
from src.views.explain_to_renderer import ExplainToRenderer
from src.services.transitions import crossfade
from src.services.transition_math import transition_progress
from src.views.board_renderer import render_board
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
from src.views.mode_select import run_mode_select
from src.views.app_mode_select import run_app_mode_select
from src.services.ui_scale import ui_scale


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

        # Presentation configuration
        self.presentation = PresentationConfig(enable_game_show=True)

        # Transition state
        self._frame_surface = None
        self._transition_prev = None
        self._transition_next = None
        self._transition_start_ms = None
        self._last_task_index = 0

        # One-shot slide-change flash cue
        self._slide_flash_start_ms: int | None = None
        self._slide_flash_color: tuple[int, int, int] | None = None

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

        # Board state
        self._board_state_path = "data/board_state.json"
        self._board_state: BoardState | None = None
        self._board_selection: BoardSelection | None = None
        self._board_hit_map = None
        self._board_hover_slot = None
        self._board_active_task_id: int | None = None
        self._board_screen: str = "board"  # "board" | "task" | "prompt"
        self._board_reload_choice: bool | None = None

        # App mode (board vs slideshow)
        self._app_mode: str = getattr(settings, "APP_MODE", "slideshow")

        # Debug instrumentation
        self._debug_enabled = bool(getattr(settings, "DEBUG", False))
        self._debug_last_tick_ms: int | None = None
        self._debug_board_frames: int = 0

    def _dbg(self, msg: str) -> None:
        if not self._debug_enabled:
            return
        ts = time.strftime("%H:%M:%S")
        print(f"[{ts}][DEBUG] {msg}", file=sys.stderr, flush=True)

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

        self._dbg("initialize: pygame.init done")

        # Disable key repeat globally. It can cause "stuck" behavior when holding
        # keys through startup prompts into the main loop (macOS in particular).
        pygame.key.set_repeat()

        if settings.FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
                pygame.FULLSCREEN,
            )
        else:
            self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))

        pygame.display.set_caption("Spotlight")
        self.clock = pygame.time.Clock()

        self._dbg(f"initialize: display_size={self.screen.get_size()} fullscreen={settings.FULLSCREEN}")

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

        self._dbg(f"initialize: render_scale={self._render_scale} render_canvas_size={self._render_canvas.get_size()}")

        # Choose app mode first (board vs slideshow)
        chosen_app_mode = run_app_mode_select(self.screen, self.clock)
        if chosen_app_mode is None:
            raise SystemExit(0)
        self._app_mode = chosen_app_mode
        self._dbg(f"initialize: app_mode={self._app_mode}")

        # Startup setup: pick mode, then optionally teams.
        enable_game_show = run_mode_select(self.screen, self.clock)
        if enable_game_show is None:
            raise SystemExit(0)
        self.presentation = PresentationConfig(enable_game_show=bool(enable_game_show))
        self._dbg(f"initialize: enable_game_show={self.presentation.enable_game_show}")

        if self.presentation.enable_game_show:
            team_names = run_team_setup(self.screen, self.clock)
            if team_names is None:
                raise SystemExit(0)
            self.game_state = GameState.with_teams(team_names)
            self.selected_team = 0
        else:
            # Minimal stub game state: used for timer/status only.
            self.game_state = GameState.with_teams(["Presenter"])
            self.selected_team = None

        tasks = TaskLoader.load_tasks(self.task_file)
        print(f"Loaded {len(tasks)} tasks")
        self._dbg(f"initialize: tasks_loaded={len(tasks)}")

        self.session = Session(tasks)

        if self._app_mode == "board":
            self._dbg("initialize: entering board mode init")
            self._init_board_mode(tasks)
            self._dbg("initialize: board mode init complete")
            self.input_controller = None
        else:
            self.input_controller = InputController(self.session)

        # Offscreen surface for rendering frames (for transitions)
        # NOTE: transitions and renderers target the internal canvas size.
        self._frame_surface = pygame.Surface(self._render_canvas.get_size()).convert_alpha()

        self._init_renderers()

        # Render initial frame into the buffer
        self._last_task_index = self.session.current_index
        if self._app_mode == "board":
            # Board mode draws directly.
            self._render_board_frame(initial=True)
            # Board mode renders to the internal canvas; ensure we blit/scale to the
            # actual display, same as slideshow mode.
            assert self._render_canvas is not None
            if self._render_canvas is not self.screen:
                self._blit_to_screen(self._render_canvas)
            pygame.display.flip()
        else:
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
            if not self.presentation.enable_game_show:
                return
            # Once a team buzzed and is locked-in, don't allow manual switching.
            if self.game_state.buzz_state == self.game_state.buzz_state.LOCKED:
                return
            if cmd.team_index is not None and 0 <= cmd.team_index < len(self.game_state.teams):
                self.selected_team = cmd.team_index
                self.game_state.set_status(f"Selected: {self.game_state.teams[cmd.team_index].name}", now_ms)

        elif cmd.type == CommandType.BUZZ:
            if not self.presentation.enable_game_show:
                return
            if cmd.team_index is not None:
                if self.game_state.buzz(cmd.team_index, now_ms=now_ms):
                    # Auto-focus the buzzed team.
                    self.selected_team = cmd.team_index
                    self._base_frame = None

        elif cmd.type == CommandType.BUZZ_FAIL:
            if not self.presentation.enable_game_show:
                return
            # Reopen buzz and block the failing team for this task.
            self.game_state.fail_locked_team_and_reopen(now_ms=now_ms)
            self._base_frame = None

        elif cmd.type == CommandType.AWARD:
            if not self.presentation.enable_game_show:
                return
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
            if not self.presentation.enable_game_show:
                return
            task = self.session.current_task()
            assert task.points is not None
            points = int(task.points)

            team_index = self.game_state.buzz_locked_team
            if team_index is None:
                team_index = self.selected_team
            if team_index is None:
                self.game_state.set_status("No team selected", now_ms)
            else:
                # Penalties also don't apply to blocked teams (handled by GameState.add_points)
                self.game_state.add_points(team_index, -points, now_ms=now_ms)

        elif cmd.type == CommandType.BUZZ_OPEN:
            if not self.presentation.enable_game_show:
                return
            self.game_state.open_buzz(now_ms)

        elif cmd.type == CommandType.BUZZ_RESET:
            if not self.presentation.enable_game_show:
                return
            self.game_state.reset_buzz(now_ms)

        elif cmd.type == CommandType.TIMER_TOGGLE:
            self.game_state.timer_start_pause_toggle(now_ms)

        elif cmd.type == CommandType.TIMER_RESET:
            self.game_state.timer_reset(now_ms)

        elif cmd.type == CommandType.SAVE:
            if not self.presentation.enable_game_show:
                self.game_state.set_status("Save disabled in presenter mode", now_ms)
                return
            try:
                save_state(self._game_state_path, self.game_state)
                self.game_state.set_status("Saved", now_ms)
            except GameStateStoreError as e:
                self.game_state.set_status(str(e), now_ms)

        elif cmd.type == CommandType.LOAD:
            if not self.presentation.enable_game_show:
                self.game_state.set_status("Load disabled in presenter mode", now_ms)
                return
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
                # Base slide content changed (notes and/or Tabu placeholder).
                self._base_frame = None
            return

    def _game_loop(self) -> None:
        running = True

        while running:
            now_ms = pygame.time.get_ticks()

            if self._debug_enabled:
                if self._debug_last_tick_ms is None:
                    self._debug_last_tick_ms = now_ms
                else:
                    dt = now_ms - self._debug_last_tick_ms
                    # Log only when we stall for noticeable time.
                    if dt > 250:
                        self._dbg(f"loop: stall dt_ms={dt} app_mode={self._app_mode} board_screen={self._board_screen}")
                    self._debug_last_tick_ms = now_ms

            commands = []

            if self._app_mode == "board":
                running = self._poll_board_events(now_ms)
                if not running:
                    break
            else:
                running, commands = self.input_controller.poll_commands()
                if not running:
                    break

            if self.game_state is not None:
                self.game_state.tick(now_ms)

            if self._app_mode == "board":
                self._debug_board_frames += 1
                if self._debug_enabled and self._debug_board_frames <= 5:
                    self._dbg(
                        "render: board frame "
                        f"n={self._debug_board_frames} board_screen={self._board_screen} "
                        f"selection={'set' if self._board_selection is not None else 'None'} "
                        f"state={'set' if self._board_state is not None else 'None'}"
                    )
                self._render_board_frame()
                # Board mode renders to the internal canvas; ensure we blit/scale to the
                # actual display, same as slideshow mode.
                assert self._render_canvas is not None
                if self._render_canvas is not self.screen:
                    self._blit_to_screen(self._render_canvas)
                pygame.display.flip()
            else:
                for cmd in commands:
                    if self.game_state is not None:
                        self._apply_command(cmd, now_ms)

                self._render_frame()
                pygame.display.flip()

            self.clock.tick(settings.FPS)

    def _render_to_surface(self) -> pygame.Surface:
        """Legacy wrapper: render base slide plus overlays."""
        base = self._render_base_slide()
        self._render_overlay(base)
        return base

    def _render_frame(self) -> None:
        """Render current frame for slideshow mode, including transitions."""
        # Detect task change and start a transition.
        if self.session.current_index != self._last_task_index:
            prev_task = self.session.tasks[self._last_task_index]
            if prev_task.id is not None:
                self.reveal_state.reset(int(prev_task.id))

            new_task = self.session.current_task()
            if new_task.id is not None:
                self.reveal_state.reset(int(new_task.id))

            if self.game_state is not None:
                self.game_state.clear_buzz_blocks()

            prev = self._base_frame or self._render_base_slide()
            self._base_frame = self._render_base_slide()

            self._transition_prev = prev
            self._transition_next = self._base_frame
            self._transition_start_ms = pygame.time.get_ticks()
            self._last_task_index = self.session.current_index

            # Start short flash cue (accent color of next task)
            now = self._transition_start_ms
            self._slide_flash_start_ms = now
            try:
                glow_cfg = self.renderers.get(self.session.current_task().type).get_glow_config(self.session.current_task())  # type: ignore[union-attr]
                if isinstance(glow_cfg, dict) and "color" in glow_cfg:
                    self._slide_flash_color = glow_cfg["color"]
                else:
                    self._slide_flash_color = settings.COLOR_BORDER
            except Exception:
                self._slide_flash_color = settings.COLOR_BORDER

        # If a transition is active, blend base slides
        if (
            self._transition_start_ms is not None
            and self._transition_prev is not None
            and self._transition_next is not None
        ):
            elapsed = pygame.time.get_ticks() - self._transition_start_ms
            duration = max(1, int(settings.FADE_DURATION))
            progress = transition_progress(elapsed, duration)

            blended = crossfade(self._transition_prev, self._transition_next, progress)
            self._render_overlay(blended)

            # Slide flash cue
            if self._slide_flash_start_ms is not None:
                flash_elapsed = pygame.time.get_ticks() - self._slide_flash_start_ms
                flash_duration = int(getattr(settings, "SLIDE_FLASH_DURATION", 0) or 0)
                if flash_duration > 0 and flash_elapsed < flash_duration:
                    alpha_max = int(getattr(settings, "SLIDE_FLASH_ALPHA", 0) or 0)
                    alpha_max = max(0, min(255, alpha_max))
                    flash_progress = transition_progress(flash_elapsed, flash_duration)
                    alpha = int(alpha_max * (1.0 - flash_progress))
                    if alpha > 0:
                        overlay = pygame.Surface(blended.get_size(), pygame.SRCALPHA)
                        color = self._slide_flash_color or settings.COLOR_BORDER
                        overlay.fill((color[0], color[1], color[2], alpha))
                        blended.blit(overlay, (0, 0))
                else:
                    self._slide_flash_start_ms = None

            self._blit_to_screen(blended)

            if progress >= 1.0:
                self._transition_start_ms = None
                self._transition_prev = None
        else:
            if self._base_frame is None:
                self._base_frame = self._render_base_slide()
            frame = self._base_frame.copy()
            self._render_overlay(frame)
            self._blit_to_screen(frame)

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

            # Notes are presenter-only: show when this task is revealed.
            show_note = False
            if current_task.id is not None:
                show_note = self.reveal_state.is_revealed(int(current_task.id))

            if current_task.type == "tabu" and current_task.id is not None:
                hidden = not self.reveal_state.is_revealed(int(current_task.id))
                # Render via TabuRenderer with explicit hidden flag.
                # Minimal change: call render_content directly to override content.
                if isinstance(renderer, TabuRenderer):
                    renderer.render(current_task, position_info)  # clears + glow + footer
                    # Re-render content area with placeholder if hidden.
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
                # Renderers with notes accept show_note kwarg.
                if current_task.type == "quiz" and isinstance(renderer, QuizRenderer):
                    renderer.screen.fill(settings.COLOR_BACKGROUND)
                    glow_cfg = renderer.get_glow_config(current_task)
                    if glow_cfg is not None:
                        from src.services.glow_effect import render_glow
                        render_glow(renderer.screen, glow_cfg["color"], glow_cfg.get("cache_key"))
                    renderer.render_content(current_task, show_note=show_note)
                    renderer._render_footer(position_info)
                elif current_task.type == "explain_to" and isinstance(renderer, ExplainToRenderer):
                    renderer.screen.fill(settings.COLOR_BACKGROUND)
                    glow_cfg = renderer.get_glow_config(current_task)
                    if glow_cfg is not None:
                        from src.services.glow_effect import render_glow
                        render_glow(renderer.screen, glow_cfg["color"], glow_cfg.get("cache_key"))
                    renderer.render_content(current_task, show_note=show_note)
                    renderer._render_footer(position_info)
                elif current_task.type == "code" and isinstance(renderer, CodeRenderer):
                    renderer.screen.fill(settings.COLOR_BACKGROUND)
                    glow_cfg = renderer.get_glow_config(current_task)
                    if glow_cfg is not None:
                        from src.services.glow_effect import render_glow
                        render_glow(renderer.screen, glow_cfg["color"], glow_cfg.get("cache_key"))
                    renderer.render_content(current_task, show_note=show_note)
                    renderer._render_footer(position_info)
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

        if self.presentation.enable_game_show:
            draw_scoreboard(target_surface, renderer.font_small, self.game_state, self.selected_team)
            draw_buzz_status(target_surface, renderer.font_tiny, self.game_state)

        draw_timer(target_surface, renderer.font_small, self.game_state)
        draw_status_message(target_surface, renderer.font_small, self.game_state)
        draw_help_hint(target_surface, renderer.font_tiny)

        if self.show_roster:
            draw_roster_overlay(target_surface, renderer.font_small, self.session)
        if self.show_help:
            draw_help_overlay(
                target_surface,
                renderer.font_small,
                enable_game_show=self.presentation.enable_game_show,
                enable_board=False,
            )

    def _poll_board_events(self, now_ms: int) -> bool:
        assert self.game_state is not None

        events = pygame.event.get()
        if self._debug_enabled and self._debug_board_frames < 3:
            self._dbg(f"events: count={len(events)}")

        for event in events:
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._board_screen != "board":
                    continue
                if self._board_hit_map is None:
                    continue
                pos = event.pos
                # Hit-test scaled coordinate if rendering is supersampled.
                if self._render_scale > 1.0:
                    sx, sy = self._render_canvas.get_size()
                    dx, dy = self.screen.get_size()
                    scale_x = sx / dx
                    scale_y = sy / dy
                    pos = (int(pos[0] * scale_x), int(pos[1] * scale_y))

                for rect, slot in self._board_hit_map.rect_slots:
                    if rect.collidepoint(pos):
                        assert self._board_state is not None
                        task_id = self._board_state.slot_to_task_id[slot]
                        if task_id in self._board_state.solved_task_ids:
                            self.game_state.set_status("Already solved", now_ms)
                            return True
                        self._board_active_task_id = int(task_id)
                        self._board_screen = "task"
                        # Reset reveal state for this task on open
                        self.reveal_state.reset(int(task_id))
                        self._base_frame = None
                        return True

            if event.type == pygame.MOUSEMOTION:
                if self._board_screen != "board" or self._board_hit_map is None:
                    self._board_hover_slot = None
                    continue

                pos = event.pos
                if self._render_scale > 1.0:
                    sx, sy = self._render_canvas.get_size()
                    dx, dy = self.screen.get_size()
                    scale_x = sx / dx
                    scale_y = sy / dy
                    pos = (int(pos[0] * scale_x), int(pos[1] * scale_y))

                hover = None
                for rect, slot in self._board_hit_map.rect_slots:
                    if rect.collidepoint(pos):
                        hover = slot
                        break
                self._board_hover_slot = hover

        return True

    def _init_board_mode(self, tasks) -> None:
        # Try to load previous board state. If present and matches tasks hash,
        # ask user whether to reload.
        task_sha = sha256_of_file(self.task_file)
        self._board_reload_choice = None
        self._board_screen = "board"

        loaded: BoardState | None = None
        try:
            loaded = load_board_state(self._board_state_path)
        except BoardStateStoreError:
            loaded = None

        if loaded is None or loaded.task_file_sha256 != task_sha:
            # No valid state to reload.
            self._dbg("board_init: no reloadable state; creating new")
            self._board_state = self._new_board_state(tasks, task_sha)
            self._board_screen = "board"
            return

        # Blocking prompt that renders onto the internal canvas for consistent resolution.
        assert self._render_canvas is not None
        assert self.screen is not None
        assert self.clock is not None

        # Flush any queued events from prior startup screens.
        pygame.event.clear()

        font_title = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(56), bold=True)
        font_body = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(32))
        reload_choice = True

        self._dbg("board_init: reloadable state found; entering prompt")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit(0)
                if event.type != pygame.KEYDOWN:
                    continue
                if event.key == pygame.K_ESCAPE:
                    raise SystemExit(0)
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_TAB):
                    reload_choice = not reload_choice
                if event.key == pygame.K_RETURN:
                    choice = reload_choice
                    self._dbg(f"board_init: prompt confirm choice={'reload' if choice else 'new'}")
                    # Clear the confirm key so it cannot leak into the board loop.
                    pygame.event.clear()
                    if choice:
                        self._board_state = loaded
                        self._ensure_board_selection_loaded(tasks)
                    else:
                        self._board_state = self._new_board_state(tasks, task_sha)
                    self._dbg(
                        "board_init: after choice "
                        f"state={'set' if self._board_state is not None else 'None'} "
                        f"selection={'set' if self._board_selection is not None else 'None'}"
                    )
                    self._board_hover_slot = None
                    self._board_screen = "board"
                    return

            # render prompt
            self._render_canvas.fill(settings.COLOR_BACKGROUND)
            from src.services.renderer_utils import draw_text_centered_shadow
            draw_text_centered_shadow(self._render_canvas, "Reload previous board?", font_title, settings.COLOR_TEXT_PRIMARY, ui_scale(80))
            draw_text_centered_shadow(
                self._render_canvas,
                "UP/DOWN toggle   ENTER confirm   ESC quit",
                font_body,
                settings.COLOR_TEXT_SECONDARY,
                ui_scale(150),
            )
            y = ui_scale(260)
            a_prefix = ">" if reload_choice else " "
            b_prefix = ">" if not reload_choice else " "
            draw_text_centered_shadow(
                self._render_canvas,
                f"{a_prefix} Reload last board (keeps random tasks)",
                font_body,
                settings.COLOR_TEXT_PRIMARY,
                y,
            )
            y += ui_scale(70)
            draw_text_centered_shadow(
                self._render_canvas,
                f"{b_prefix} Start new board (reshuffle once)",
                font_body,
                settings.COLOR_TEXT_PRIMARY,
                y,
            )

            self._blit_to_screen(self._render_canvas)
            pygame.display.flip()
            self.clock.tick(settings.FPS)

    def _new_board_state(self, tasks, task_sha: str) -> BoardState:
        import random
        try:
            selection = build_board_selection(tasks, random.Random())
        except BoardSelectionError as e:
            raise TaskLoadError(str(e))

        self._board_selection = selection
        st = BoardState(slot_to_task_id=selection.slot_to_task_id, solved_task_ids=set(), task_file_sha256=task_sha)
        # Persist immediately so crashes don't reshuffle.
        try:
            save_board_state(self._board_state_path, st)
        except BoardStateStoreError:
            pass
        return st

    def _ensure_board_selection_loaded(self, tasks) -> None:
        assert self._board_state is not None
        # Build selection view from saved mapping.
        from src.models.board_selection import BoardSelection
        cats = sorted({c for (c, _p) in self._board_state.slot_to_task_id.keys()})
        self._board_selection = BoardSelection(categories=cats, slot_to_task_id=self._board_state.slot_to_task_id)

    def _render_board_frame(self, initial: bool = False) -> None:
        assert self.screen is not None
        assert self.clock is not None
        assert self._render_canvas is not None
        assert self.game_state is not None

        # Ensure selection is ready
        if self._board_selection is None:
            # build from state
            self._ensure_board_selection_loaded(self.session.tasks)

        # Draw either board or task
        if self._board_screen == "board":
            font_header = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(40), bold=True)
            font_cell = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(56), bold=True)
            assert self._board_state is not None
            assert self._board_selection is not None
            self._board_hit_map = render_board(
                self._render_canvas,
                font_header,
                font_cell,
                self._board_selection,
                self._board_state.solved_task_ids,
                hover_slot=self._board_hover_slot,
            )
            # overlays (timer + help/status)
            self._render_board_overlays(self._render_canvas, on_board=True)
        else:
            # task
            assert self._board_active_task_id is not None
            self._render_canvas.fill(settings.COLOR_BACKGROUND)
            # render selected task base slide + overlays
            # Temporarily set session index to chosen task for reuse of renderers
            prev_idx = self.session.current_index
            try:
                self.session.current_index = self._board_active_task_id
                self._base_frame = None
                # In board mode's task view we don't want the slideshow position footer.
                # We'll temporarily override Session.get_position_info() by rendering with
                # an empty position string.
                base = self._render_base_slide_board_task()
                self._render_overlay(base)
                # Board-specific overlays
                self._render_board_overlays(base, on_board=False)
                self._render_canvas.blit(base, (0, 0))
            finally:
                self.session.current_index = prev_idx

    def _render_base_slide_board_task(self) -> pygame.Surface:
        """Render a task slide for board-mode task view.

        Same as _render_base_slide(), but without the slideshow footer position indicator.
        """
        current_task = self.session.current_task()
        renderer = self.renderers.get(current_task.type)

        self._frame_surface.fill(settings.COLOR_BACKGROUND)

        if renderer is None:
            self._render_error(f"Unknown task type: {current_task.type}")
            return self._frame_surface.copy()

        # Notes are presenter-only: show when this task is revealed.
        show_note = False
        if current_task.id is not None:
            show_note = self.reveal_state.is_revealed(int(current_task.id))

        # Render content; footer is suppressed by providing empty position info.
        position_info = ""

        if current_task.type == "tabu" and current_task.id is not None and isinstance(renderer, TabuRenderer):
            hidden = not self.reveal_state.is_revealed(int(current_task.id))
            renderer.render(current_task, position_info)
            if hidden:
                self._frame_surface.fill(settings.COLOR_BACKGROUND)
                glow_config = renderer.get_glow_config(current_task)
                if glow_config:
                    from src.services.glow_effect import render_glow
                    render_glow(self._frame_surface, glow_config['color'], glow_config.get('cache_key'))
                renderer.render_content(current_task, hidden=True)
                renderer._render_footer(position_info)
        elif current_task.type == "quiz" and isinstance(renderer, QuizRenderer):
            renderer.screen.fill(settings.COLOR_BACKGROUND)
            glow_cfg = renderer.get_glow_config(current_task)
            if glow_cfg is not None:
                from src.services.glow_effect import render_glow
                render_glow(renderer.screen, glow_cfg["color"], glow_cfg.get("cache_key"))
            renderer.render_content(current_task, show_note=show_note)
            renderer._render_footer(position_info)
        elif current_task.type == "explain_to" and isinstance(renderer, ExplainToRenderer):
            renderer.screen.fill(settings.COLOR_BACKGROUND)
            glow_cfg = renderer.get_glow_config(current_task)
            if glow_cfg is not None:
                from src.services.glow_effect import render_glow
                render_glow(renderer.screen, glow_cfg["color"], glow_cfg.get("cache_key"))
            renderer.render_content(current_task, show_note=show_note)
            renderer._render_footer(position_info)
        elif current_task.type == "code" and isinstance(renderer, CodeRenderer):
            renderer.screen.fill(settings.COLOR_BACKGROUND)
            glow_cfg = renderer.get_glow_config(current_task)
            if glow_cfg is not None:
                from src.services.glow_effect import render_glow
                render_glow(renderer.screen, glow_cfg["color"], glow_cfg.get("cache_key"))
            renderer.render_content(current_task, show_note=show_note)
            renderer._render_footer(position_info)
        else:
            renderer.render(current_task, position_info)

        return self._frame_surface.copy()

    def _render_board_overlays(self, surface: pygame.Surface, *, on_board: bool) -> None:
        # Keep timer + status + help hint; hide scoreboard/buzz in board mode.
        assert self.game_state is not None
        # Use any renderer font; fall back to pygame font.
        font_small = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(28))
        font_tiny = pygame.font.SysFont(settings.FONT_FAMILY_PRIMARY, ui_scale(20))
        draw_timer(surface, font_small, self.game_state)
        draw_status_message(surface, font_small, self.game_state)
        draw_help_hint(surface, font_tiny)

        if self.show_help:
            draw_help_overlay(surface, font_small, enable_game_show=False, enable_board=True)

        # Tiny bottom hint for board/task controls
        hint = "BACKSPACE=board  M=solved  V=reveal" if not on_board else "Click=open  H=help  ESC=quit"
        s = font_tiny.render(hint, True, settings.COLOR_TEXT_MUTED)
        # Keep fully on-screen (use font height rather than a hardcoded 30).
        y = surface.get_height() - s.get_height() - ui_scale(14)
        surface.blit(s, (ui_scale(18), y))

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

