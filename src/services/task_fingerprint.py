"""Task file fingerprinting.

Used to decide whether a saved board state matches the current tasks file.

Contract
- sha256_of_file(path) -> hex digest

Side effects: reads file from disk
"""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_of_file(path: str) -> str:
    p = Path(path)
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

