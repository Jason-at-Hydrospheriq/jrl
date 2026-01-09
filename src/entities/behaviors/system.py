#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING, cast
import tcod

from entities.behaviors.base import BaseGameEvent, BaseGameAction
from time import sleep
from game_types import StateActionObject, StateHandler

if TYPE_CHECKING:
    from store import GameStore


class SystemEvent(BaseGameEvent):
    def __init__(self, store: GameStore | None = None, handler: StateHandler | None = None, input_event: tcod.event.Event | None = None) -> None:
        super().__init__(store, handler)

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class NonEvent(BaseGameEvent):
    pass


class NoAction(BaseGameAction):

    def perform(self) -> None:
        pass


class WaitEvent(SystemEvent):
    wait_time: int

    def __init__(self, store: GameStore | None = None, handler: StateHandler | None = None, wait_time: int = 0) -> None:
        super().__init__(store, handler)
        self.wait_time = wait_time

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))


class WaitAction(BaseGameAction):
    wait_time: int = 0  # Time to wait in milliseconds

    def __init__(self, wait_time: int = 0) -> None:
        super().__init__()
        self.wait_time = wait_time

    def perform(self) -> None:
        sleep(self.wait_time / 1000.0) # Convert milliseconds to seconds
        self.handler.handle(None) # type: ignore
        
