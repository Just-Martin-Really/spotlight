"""Input command types for Spotlight.

This keeps pygame event handling decoupled from application logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CommandType(str, Enum):
    NEXT = "next"
    PREV = "prev"
    QUIT = "quit"

    SELECT_TEAM = "select_team"
    AWARD = "award"
    PENALTY = "penalty"

    BUZZ_OPEN = "buzz_open"
    BUZZ_RESET = "buzz_reset"
    BUZZ = "buzz"
    BUZZ_FAIL = "buzz_fail"

    TIMER_TOGGLE = "timer_toggle"
    TIMER_RESET = "timer_reset"

    TOGGLE_ROSTER = "toggle_roster"
    TOGGLE_HELP = "toggle_help"

    TOGGLE_REVEAL = "toggle_reveal"

    SAVE = "save"
    LOAD = "load"


@dataclass(frozen=True)
class Command:
    type: CommandType
    team_index: Optional[int] = None
