import json
from pathlib import Path

import pytest

from src.models.board_state import BoardState
from src.services.board_state_store import load_board_state, save_board_state


def test_board_state_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "board_state.json"
    state = BoardState(
        task_file_sha256="abc",
        solved_task_ids={1, 2},
        slot_to_task_id={("Mathe", 100): 1, ("Theo Inf", 200): 2},
    )

    save_board_state(str(path), state)
    loaded = load_board_state(str(path))

    assert loaded.task_file_sha256 == "abc"
    assert loaded.solved_task_ids == {1, 2}
    assert loaded.slot_to_task_id == {("Mathe", 100): 1, ("Theo Inf", 200): 2}


def test_board_state_invalid(tmp_path: Path) -> None:
    path = tmp_path / "board_state.json"
    path.write_text(json.dumps({"nope": True}), encoding="utf-8")

    with pytest.raises(Exception):
        load_board_state(str(path))

