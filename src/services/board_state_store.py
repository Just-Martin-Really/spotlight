"""Board state persistence.

Uses a simple JSON file with atomic replace to avoid corruption.

Contract
- save_board_state(path, state)
- load_board_state(path) -> BoardState

Side effects
- reads/writes a JSON file on disk
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from src.models.board_state import BoardState


class BoardStateStoreError(Exception):
    pass


def load_board_state(path: str) -> BoardState:
    p = Path(path)
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        return BoardState.from_dict(raw)
    except FileNotFoundError as e:
        raise BoardStateStoreError(f"Board state not found: {path}") from e
    except Exception as e:
        raise BoardStateStoreError(f"Failed to load board state: {e}") from e


def save_board_state(path: str, state: BoardState) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    tmp = p.with_suffix(p.suffix + ".tmp")
    payload = json.dumps(state.to_dict(), ensure_ascii=False, indent=2)

    try:
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, p)
    except Exception as e:
        # Best-effort cleanup
        try:
            if tmp.exists():
                tmp.unlink()
        except Exception:
            pass
        raise BoardStateStoreError(f"Failed to save board state: {e}") from e

