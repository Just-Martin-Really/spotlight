"""Per-task reveal state.

Used for content that should be hidden on the beamer until explicitly revealed
(e.g., Tabu topic/forbidden words).

Contract
- toggle(task_id): flips reveal state for that task id.
- is_revealed(task_id): returns current state.
- reset(task_id): sets to hidden.

Side effects: stores state in-memory only.
"""

from __future__ import annotations


class RevealState:
    def __init__(self) -> None:
        self._revealed: set[int] = set()

    def is_revealed(self, task_id: int) -> bool:
        return task_id in self._revealed

    def toggle(self, task_id: int) -> bool:
        if task_id in self._revealed:
            self._revealed.remove(task_id)
            return False
        self._revealed.add(task_id)
        return True

    def reset(self, task_id: int) -> None:
        self._revealed.discard(task_id)

    def clear_all(self) -> None:
        self._revealed.clear()

