"""Presentation mode configuration.

This module defines a tiny, explicit contract for whether Spotlight should run
as a full game-show with teams/buzzer/scoring, or as a simple presenter.

Contract
- PresentationConfig.enable_game_show:
  - True: teams + buzzer + scoring enabled
  - False: no teams/buzzer/scoring; timer + navigation + reveal still work

Side effects: none
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PresentationConfig:
    enable_game_show: bool = True

