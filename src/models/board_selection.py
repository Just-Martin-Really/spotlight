"""Board selection (Jeopardy-style) helpers.

Builds a stable mapping of (category, points) -> task_id for board mode.

Rules
- Points rows are always [100, 200, 300, 400, 500] (ascending).
- For each (category, points) slot, there must be >= 1 task candidate.
- If multiple tasks exist for the same slot, one is chosen randomly at startup
  and stays stable for the session.

Contract
- build_board_selection(tasks, rng) -> BoardSelection

Side effects: none
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, Iterable, List, Tuple

from src.models.task import BaseTask


POINT_ROWS: List[int] = [100, 200, 300, 400, 500]


class BoardSelectionError(ValueError):
    pass


Slot = Tuple[str, int]  # (category, points)


@dataclass(frozen=True)
class BoardSelection:
    categories: List[str]
    slot_to_task_id: Dict[Slot, int]

    def task_id_for(self, category: str, points: int) -> int:
        return self.slot_to_task_id[(category, points)]


def build_board_selection(tasks: Iterable[BaseTask], rng: random.Random) -> BoardSelection:
    tasks = list(tasks)

    categories = sorted({(t.category or "").strip() for t in tasks if (t.category or "").strip()})
    if not categories:
        raise BoardSelectionError("No categories found. Every task must define 'category'.")

    # Collect candidates by slot
    candidates: Dict[Slot, List[int]] = {}
    for t in tasks:
        if t.id is None:
            continue
        if not t.category or not t.category.strip():
            continue
        if t.points is None:
            continue
        slot = (t.category.strip(), int(t.points))
        candidates.setdefault(slot, []).append(int(t.id))

    slot_to_task_id: Dict[Slot, int] = {}

    # Enforce full board: every category must have every points row.
    missing: List[Slot] = []
    for cat in categories:
        for pts in POINT_ROWS:
            slot = (cat, pts)
            ids = candidates.get(slot, [])
            if not ids:
                missing.append(slot)
                continue
            slot_to_task_id[slot] = rng.choice(ids)

    if missing:
        missing_str = ", ".join([f"({c}, {p})" for c, p in missing])
        raise BoardSelectionError(f"Board has empty slots (category, points) with no tasks: {missing_str}")

    return BoardSelection(categories=categories, slot_to_task_id=slot_to_task_id)

