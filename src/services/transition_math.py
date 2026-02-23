"""Transition math helpers.

This module exists so we can unit-test transition timing without needing Pygame.

Contract
- Inputs:
  - elapsed_ms: int (>= 0)
  - duration_ms: int (> 0)
- Output:
  - progress: float in [0.0, 1.0]

Side effects: none
"""

from __future__ import annotations


def transition_progress(elapsed_ms: int, duration_ms: int) -> float:
    if duration_ms <= 0:
        raise ValueError("duration_ms must be > 0")
    if elapsed_ms <= 0:
        return 0.0
    if elapsed_ms >= duration_ms:
        return 1.0
    return elapsed_ms / duration_ms

