"""Game-show state for Spotlight WOW mode.

This module is intentionally UI-agnostic and deterministic.
It contains the rules/state machine for:
- teams + scoring
- buzz-in locking
- timer (stopwatch/countdown)
- persistence to/from JSON-serializable dict

Contract
Inputs:
- Commands (e.g., add/subtract points, open/reset buzz, start/pause/reset timer)
- A time source (`now_ms`) injected by caller for deterministic behavior.

Outputs:
- Current team scores and names
- Buzz state (CLOSED/OPEN/LOCKED + locked team)
- Timer state

Error modes:
- Invalid team index: ignored (no exception)
- Invalid configuration (e.g., countdown target < 0): ValueError

Side effects:
- None in this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class BuzzState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    LOCKED = "locked"


class TimerMode(str, Enum):
    STOPWATCH = "stopwatch"
    COUNTDOWN = "countdown"


@dataclass
class Team:
    name: str
    score: int = 0


@dataclass
class Timer:
    mode: TimerMode = TimerMode.STOPWATCH
    running: bool = False

    # For stopwatch: elapsed_ms counts up.
    # For countdown: remaining_ms counts down from target_ms.
    elapsed_ms: int = 0
    target_ms: Optional[int] = None

    _last_start_ms: Optional[int] = None

    def start(self, now_ms: int) -> None:
        if self.running:
            return
        self.running = True
        self._last_start_ms = now_ms

    def pause(self, now_ms: int) -> None:
        if not self.running:
            return
        self._accumulate(now_ms)
        self.running = False
        self._last_start_ms = None

    def reset(self) -> None:
        self.running = False
        self.elapsed_ms = 0
        self._last_start_ms = None

    def set_countdown(self, target_ms: int) -> None:
        if target_ms < 0:
            raise ValueError("target_ms must be >= 0")
        self.mode = TimerMode.COUNTDOWN
        self.target_ms = target_ms
        self.reset()

    def set_stopwatch(self) -> None:
        self.mode = TimerMode.STOPWATCH
        self.target_ms = None
        self.reset()

    def tick(self, now_ms: int) -> None:
        if not self.running:
            return
        self._accumulate(now_ms)
        self._last_start_ms = now_ms

    def remaining_ms(self) -> Optional[int]:
        if self.mode != TimerMode.COUNTDOWN:
            return None
        if self.target_ms is None:
            return None
        return max(0, self.target_ms - self.elapsed_ms)

    def is_finished(self) -> bool:
        rem = self.remaining_ms()
        return rem is not None and rem == 0

    def _accumulate(self, now_ms: int) -> None:
        if self._last_start_ms is None:
            self._last_start_ms = now_ms
            return
        delta = max(0, now_ms - self._last_start_ms)
        self.elapsed_ms += delta


@dataclass
class GameState:
    teams: List[Team]
    buzz_state: BuzzState = BuzzState.CLOSED
    buzz_locked_team: Optional[int] = None
    timer: Timer = field(default_factory=Timer)

    # Teams blocked from buzzing for the current task (by team index)
    buzz_blocked_teams: set[int] = field(default_factory=set)

    # Transient UI hints (e.g., “Saved”, “Loaded”, “Buzz OPEN”)
    status_message: Optional[str] = None
    status_until_ms: Optional[int] = None

    @classmethod
    def with_teams(cls, team_names: List[str]) -> "GameState":
        clean = [name.strip() for name in team_names if name and name.strip()]
        if not clean:
            raise ValueError("At least one team name required")
        return cls(teams=[Team(name=n) for n in clean])

    def set_status(self, message: str, now_ms: int, duration_ms: int = 2000) -> None:
        self.status_message = message
        self.status_until_ms = now_ms + max(0, duration_ms)

    def clear_expired_status(self, now_ms: int) -> None:
        if self.status_until_ms is not None and now_ms >= self.status_until_ms:
            self.status_until_ms = None
            self.status_message = None

    # --- scoring ---
    def add_points(self, team_index: int, points: int, now_ms: Optional[int] = None) -> None:
        if not (0 <= team_index < len(self.teams)):
            return

        # If a team is blocked for the current task, they can't receive points.
        if team_index in self.buzz_blocked_teams:
            if now_ms is not None:
                self.set_status(f"BLOCKED: {self.teams[team_index].name}", now_ms)
            return

        self.teams[team_index].score += points
        if now_ms is not None:
            sign = "+" if points >= 0 else ""
            self.set_status(f"{self.teams[team_index].name} {sign}{points}", now_ms)

    def reset_scores(self, now_ms: Optional[int] = None) -> None:
        for t in self.teams:
            t.score = 0
        self.buzz_state = BuzzState.CLOSED
        self.buzz_locked_team = None
        self.buzz_blocked_teams.clear()
        self.timer.reset()
        if now_ms is not None:
            self.set_status("Scores reset", now_ms)

    # --- buzzer ---
    def open_buzz(self, now_ms: Optional[int] = None) -> None:
        self.buzz_state = BuzzState.OPEN
        self.buzz_locked_team = None
        if now_ms is not None:
            self.set_status("BUZZ OPEN", now_ms)

    def reset_buzz(self, now_ms: Optional[int] = None) -> None:
        self.buzz_state = BuzzState.CLOSED
        self.buzz_locked_team = None
        self.buzz_blocked_teams.clear()
        if now_ms is not None:
            self.set_status("BUZZ RESET", now_ms)

    def fail_locked_team_and_reopen(self, now_ms: Optional[int] = None) -> None:
        """Mark the currently locked team as failed and reopen buzz.

        The failed team is blocked from buzzing again until caller clears
        buzz_blocked_teams (typically on task change).
        """
        if self.buzz_locked_team is not None:
            self.buzz_blocked_teams.add(self.buzz_locked_team)
        self.buzz_state = BuzzState.OPEN
        self.buzz_locked_team = None
        if now_ms is not None:
            self.set_status("BUZZ REOPEN", now_ms)

    def clear_buzz_blocks(self) -> None:
        self.buzz_blocked_teams.clear()

    def buzz(self, team_index: int, now_ms: Optional[int] = None) -> bool:
        if self.buzz_state != BuzzState.OPEN:
            return False
        if not (0 <= team_index < len(self.teams)):
            return False
        if team_index in self.buzz_blocked_teams:
            if now_ms is not None:
                self.set_status(f"BLOCKED: {self.teams[team_index].name}", now_ms)
            return False
        self.buzz_state = BuzzState.LOCKED
        self.buzz_locked_team = team_index
        if now_ms is not None:
            self.set_status(f"BUZZ: {self.teams[team_index].name}", now_ms)
        return True

    # --- timer ---
    def timer_start_pause_toggle(self, now_ms: int) -> None:
        if self.timer.running:
            self.timer.pause(now_ms)
            self.set_status("Timer paused", now_ms)
        else:
            self.timer.start(now_ms)
            self.set_status("Timer started", now_ms)

    def timer_reset(self, now_ms: int) -> None:
        self.timer.reset()
        self.set_status("Timer reset", now_ms)

    def tick(self, now_ms: int) -> None:
        self.timer.tick(now_ms)
        self.clear_expired_status(now_ms)

    # --- persistence ---
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "teams": [{"name": t.name, "score": t.score} for t in self.teams],
            "buzz": {
                "state": self.buzz_state.value,
                "locked_team": self.buzz_locked_team,
            },
            "timer": {
                "mode": self.timer.mode.value,
                "running": self.timer.running,
                "elapsed_ms": self.timer.elapsed_ms,
                "target_ms": self.timer.target_ms,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GameState":
        if not isinstance(data, dict):
            raise ValueError("GameState data must be an object")

        teams_raw = data.get("teams")
        if not isinstance(teams_raw, list) or not teams_raw:
            raise ValueError("GameState.teams must be a non-empty array")

        teams: List[Team] = []
        for item in teams_raw:
            if not isinstance(item, dict):
                raise ValueError("Team must be an object")
            name = item.get("name")
            score = item.get("score", 0)
            if not isinstance(name, str) or not name.strip():
                raise ValueError("Team.name must be a non-empty string")
            if not isinstance(score, int):
                raise ValueError("Team.score must be an int")
            teams.append(Team(name=name.strip(), score=score))

        gs = cls(teams=teams)

        buzz = data.get("buzz", {})
        if isinstance(buzz, dict):
            state = buzz.get("state", BuzzState.CLOSED.value)
            locked_team = buzz.get("locked_team")
            if state in (BuzzState.CLOSED.value, BuzzState.OPEN.value, BuzzState.LOCKED.value):
                gs.buzz_state = BuzzState(state)
            if locked_team is None or isinstance(locked_team, int):
                gs.buzz_locked_team = locked_team

        timer = data.get("timer", {})
        if isinstance(timer, dict):
            mode = timer.get("mode", TimerMode.STOPWATCH.value)
            running = timer.get("running", False)
            elapsed_ms = timer.get("elapsed_ms", 0)
            target_ms = timer.get("target_ms")

            if mode in (TimerMode.STOPWATCH.value, TimerMode.COUNTDOWN.value):
                gs.timer.mode = TimerMode(mode)
            if isinstance(running, bool):
                gs.timer.running = False  # restored as paused; caller can start
            if isinstance(elapsed_ms, int) and elapsed_ms >= 0:
                gs.timer.elapsed_ms = elapsed_ms
            if target_ms is None or (isinstance(target_ms, int) and target_ms >= 0):
                gs.timer.target_ms = target_ms

        # Sanitize locked team index
        if gs.buzz_locked_team is not None and not (0 <= gs.buzz_locked_team < len(gs.teams)):
            gs.buzz_locked_team = None
            if gs.buzz_state == BuzzState.LOCKED:
                gs.buzz_state = BuzzState.CLOSED

        return gs

