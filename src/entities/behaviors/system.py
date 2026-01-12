#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING, cast
import tcod

from baseclasses import BaseGameAction
from time import sleep
from baseclasses import BaseGameEvent
from game_types import StateActionObject, StateHandler

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler


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


class InputEvent(BaseGameEvent):
    _input_event: tcod.event.Event | None

    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, input_event: tcod.event.Event | None = None) -> None:
        super().__init__(store, handler)
        self._input_event = input_event

    @property
    def input_event(self) -> tcod.event.Event | None:
        return self._input_event

    @input_event.setter
    def input_event(self, value: tcod.event.Event | None) -> None:
        if value is not None and not isinstance(value, tcod.event.Event):
            raise TypeError("input_event must be an instance of tcod.event.Event or None")
        self._input_event = value

    def trigger(self) -> None:
        if self.handler:
            self.handler.handle(cast(StateActionObject, self))
        
