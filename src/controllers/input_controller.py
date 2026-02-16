"""
Input controller for Spotlight.

Translates pygame keyboard events into application actions.
Decouples pygame event handling from business logic.

Design principle: Controller pattern - mediates between UI and model.
"""

from __future__ import annotations

import pygame

from config import keybindings
from src.controllers.commands import Command, CommandType
from src.models.session import Session


class InputController:
    """Handles keyboard input and translates it into session/app commands."""

    def __init__(self, session: Session):
        self.session = session
        self._buzz_open_mode = False

    def poll_commands(self) -> tuple[bool, list[Command]]:
        """Process pending pygame events.

        Returns:
            (running, commands)
        """
        commands: list[Command] = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, [Command(CommandType.QUIT)]

            if event.type == pygame.KEYDOWN:
                cmd = self._map_keydown(event)
                if cmd is not None:
                    if cmd.type == CommandType.QUIT:
                        return False, [cmd]
                    commands.append(cmd)

        return True, commands

    def _map_keydown(self, event: pygame.event.Event) -> Command | None:
        key = event.key

        if key == keybindings.KEY_QUIT:
            return Command(CommandType.QUIT)

        if key == keybindings.KEY_NEXT:
            self.session.next_task()
            return Command(CommandType.NEXT)

        if key == keybindings.KEY_PREV:
            self.session.prev_task()
            return Command(CommandType.PREV)

        # Buzz-in open / reset
        if key == keybindings.KEY_BUZZ_OPEN:
            self._buzz_open_mode = True
            return Command(CommandType.BUZZ_OPEN)

        if key == keybindings.KEY_BUZZ_RESET:
            self._buzz_open_mode = False
            return Command(CommandType.BUZZ_RESET)

        if key == keybindings.KEY_BUZZ_FAIL:
            self._buzz_open_mode = False
            return Command(CommandType.BUZZ_FAIL)

        # Team selection / buzz: 1..9
        team_keys = {
            keybindings.KEY_TEAM_1: 0,
            keybindings.KEY_TEAM_2: 1,
            keybindings.KEY_TEAM_3: 2,
            keybindings.KEY_TEAM_4: 3,
            keybindings.KEY_TEAM_5: 4,
            keybindings.KEY_TEAM_6: 5,
            keybindings.KEY_TEAM_7: 6,
            keybindings.KEY_TEAM_8: 7,
            keybindings.KEY_TEAM_9: 8,
        }
        if key in team_keys:
            team_index = team_keys[key]
            if self._buzz_open_mode:
                # First team number after opening buzz counts as "buzz".
                # Application will decide whether it locks based on GameState.
                self._buzz_open_mode = False
                return Command(CommandType.BUZZ, team_index=team_index)
            return Command(CommandType.SELECT_TEAM, team_index=team_index)

        if key == keybindings.KEY_AWARD:
            return Command(CommandType.AWARD)

        if key == keybindings.KEY_PENALTY:
            return Command(CommandType.PENALTY)

        if key == keybindings.KEY_TIMER_TOGGLE:
            return Command(CommandType.TIMER_TOGGLE)

        if key == keybindings.KEY_TIMER_RESET:
            return Command(CommandType.TIMER_RESET)

        if key == keybindings.KEY_TOGGLE_ROSTER:
            return Command(CommandType.TOGGLE_ROSTER)

        if key == keybindings.KEY_TOGGLE_HELP:
            return Command(CommandType.TOGGLE_HELP)

        if key == keybindings.KEY_SAVE:
            return Command(CommandType.SAVE)

        if key == keybindings.KEY_LOAD:
            return Command(CommandType.LOAD)

        if key == keybindings.KEY_TOGGLE_REVEAL:
            return Command(CommandType.TOGGLE_REVEAL)

        return None

    # Backward-compatible API
    def handle_events(self) -> bool:
        running, _ = self.poll_commands()
        return running
