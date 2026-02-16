"""Per-task scoring state.

Prevents awarding points for the same task multiple times.

Contract:
- mark_awarded(task_id): returns True if this is the first award, False otherwise.
- is_awarded(task_id): query.
- reset(task_id): clear for a task.

Side effects: in-memory only.
"""

from __future__ import annotations


class ScoringState:
    def __init__(self) -> None:
        self._awarded: set[int] = set()

    def is_awarded(self, task_id: int) -> bool:
        return task_id in self._awarded

    def mark_awarded(self, task_id: int) -> bool:
        if task_id in self._awarded:
            return False
        self._awarded.add(task_id)
        return True

    def reset(self, task_id: int) -> None:
        self._awarded.discard(task_id)

    def clear_all(self) -> None:
        self._awarded.clear()

