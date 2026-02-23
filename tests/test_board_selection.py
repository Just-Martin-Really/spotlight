import random
import pytest

from src.models.board_selection import POINT_ROWS, BoardSelectionError, build_board_selection
from src.models.task import QuizTask


def _task(i: int, category: str, points: int) -> QuizTask:
    return QuizTask(type="quiz", id=i, category=category, points=points, question=f"Q{i}")


def test_board_selection_requires_full_grid() -> None:
    # Missing many slots -> should error.
    tasks = [_task(0, "Mathe", 100)]
    with pytest.raises(BoardSelectionError):
        build_board_selection(tasks, random.Random(0))


def test_board_selection_picks_stably_with_seed() -> None:
    # Provide full grid with duplicates for one slot.
    tasks = []
    tid = 0
    for cat in ["Mathe", "Theo Inf"]:
        for pts in POINT_ROWS:
            tasks.append(_task(tid, cat, pts))
            tid += 1

    # Duplicate one slot
    tasks.append(_task(tid, "Mathe", 200))

    sel1 = build_board_selection(tasks, random.Random(123))
    sel2 = build_board_selection(tasks, random.Random(123))
    assert sel1.slot_to_task_id == sel2.slot_to_task_id

