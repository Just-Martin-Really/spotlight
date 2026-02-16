"""Persistence helpers for GameState.

Contract
- save_state(path, game_state) writes JSON.
- load_state(path) reads JSON and returns GameState.

Side effects:
- file I/O
"""

from __future__ import annotations

import json
from pathlib import Path

from src.models.game_state import GameState


class GameStateStoreError(Exception):
    pass


def save_state(filepath: str, state: GameState) -> None:
    path = Path(filepath)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        raise GameStateStoreError(f"Failed to save game state: {e}") from e


def load_state(filepath: str) -> GameState:
    path = Path(filepath)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return GameState.from_dict(data)
    except Exception as e:
        raise GameStateStoreError(f"Failed to load game state: {e}") from e

