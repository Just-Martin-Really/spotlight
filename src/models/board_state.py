"""Board mode persistent state.

Stores:
- The frozen mapping of board slots -> task ids (so duplicates don't reshuffle)
- Which tasks are solved

Contract
- BoardState can be serialized to/from dict for JSON storage.

Side effects: none
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple, Any


Slot = Tuple[str, int]  # (category, points)


@dataclass
class BoardState:
    slot_to_task_id: Dict[Slot, int]
    solved_task_ids: Set[int]
    task_file_sha256: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_file_sha256": self.task_file_sha256,
            "solved_task_ids": sorted(self.solved_task_ids),
            "slot_to_task_id": [{"category": c, "points": p, "task_id": tid} for (c, p), tid in self.slot_to_task_id.items()],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BoardState":
        if not isinstance(data, dict):
            raise ValueError("BoardState must be an object")
        sha = data.get("task_file_sha256")
        if not isinstance(sha, str) or not sha:
            raise ValueError("BoardState.task_file_sha256 missing/invalid")

        solved_raw = data.get("solved_task_ids", [])
        if not isinstance(solved_raw, list) or not all(isinstance(x, int) for x in solved_raw):
            raise ValueError("BoardState.solved_task_ids must be a list of ints")

        slots_raw = data.get("slot_to_task_id", [])
        if not isinstance(slots_raw, list):
            raise ValueError("BoardState.slot_to_task_id must be a list")

        slot_to_task_id: Dict[Slot, int] = {}
        for item in slots_raw:
            if not isinstance(item, dict):
                raise ValueError("Invalid slot entry")
            cat = item.get("category")
            pts = item.get("points")
            tid = item.get("task_id")
            if not isinstance(cat, str) or not cat.strip():
                raise ValueError("Slot.category missing/invalid")
            if not isinstance(pts, int):
                raise ValueError("Slot.points missing/invalid")
            if not isinstance(tid, int):
                raise ValueError("Slot.task_id missing/invalid")
            slot_to_task_id[(cat.strip(), pts)] = tid

        return cls(slot_to_task_id=slot_to_task_id, solved_task_ids=set(solved_raw), task_file_sha256=sha)

