"""Game-show orchestration helpers.

This module bridges the task roster (Session) and the game state (GameState)
with a few small, deterministic rules:
- awarding the current task's difficulty as points
- choosing the target team (buzz-locked team or a manually selected team)

Contract
- award_points_for_current_task(session, game_state, selected_team_index, now_ms)
  returns the team index that was awarded, or None if no award happened.

Side effects: modifies the provided GameState.
"""

from __future__ import annotations

from typing import Optional

from src.models.game_state import GameState
from src.models.session import Session


def award_points_for_current_task(
    session: Session,
    game_state: GameState,
    selected_team_index: Optional[int],
    now_ms: int,
) -> Optional[int]:
    """Award points for the current task.

    Rules:
    - points = current_task.difficulty (guaranteed to be present by loader)
    - target team:
      - if buzz is locked: that team wins
      - else if a team is selected: use it
      - else: do nothing

    Returns:
        Awarded team index, or None.
    """

    task = session.current_task()
    assert task.difficulty is not None, "Task difficulty must be present (validated at load time)"
    points = int(task.difficulty)

    team_index = game_state.buzz_locked_team
    if team_index is None:
        team_index = selected_team_index

    if team_index is None:
        game_state.set_status("No team selected", now_ms)
        return None

    game_state.add_points(team_index, points, now_ms=now_ms)
    return team_index
