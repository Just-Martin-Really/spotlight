"""Pure, testable logic for the board reload prompt.

The UI prompt is intentionally handled in pygame, but the decision/state machine
(what keys do what) can be tested without pygame.

Contract
- Inputs: current choice (bool) and a key identifier string
- Output: (new_choice, result)
  - new_choice: possibly toggled choice
  - result: None (continue) | bool (confirm choice) | "abort"
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptUpdate:
    choice: bool
    result: bool | None | str


TOGGLE_KEYS = {"UP", "DOWN", "TAB"}
CONFIRM_KEYS = {"ENTER"}
ABORT_KEYS = {"ESC"}


def update_reload_prompt(choice: bool, key: str) -> PromptUpdate:
    key_u = key.upper()
    if key_u in TOGGLE_KEYS:
        return PromptUpdate(choice=not choice, result=None)
    if key_u in CONFIRM_KEYS:
        return PromptUpdate(choice=choice, result=choice)
    if key_u in ABORT_KEYS:
        return PromptUpdate(choice=choice, result="abort")
    return PromptUpdate(choice=choice, result=None)

