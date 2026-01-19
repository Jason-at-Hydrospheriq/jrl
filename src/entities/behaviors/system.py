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
        

class SystemKeyDownAction(BaseGameAction):
    input_event: tcod.event.Event | None
    
    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, input_event: tcod.event.KeyboardEvent | None = None) -> None:
        super().__init__(store, handler)
        self.input_event = input_event

    def perform(self) -> None:
        try:
            if isinstance(self.input_event, tcod.event.KeyboardEvent) and self.store and self.display and self.loop:
                key_sim = self.input_event.sym
                match key_sim:

                    case tcod.event.KeySym.V:
                        if self.display and self.loop.display_loop_handler:
                            main_console = self.display.get_window_by_name('main_window')                                        
                            history_console = self.display.get_window_by_name('history_window')
                                                                            
                            if main_console and history_console and not history_console.is_rendered:
                                self.loop.sequenced_loop_handler.stop()  # type: ignore
                                self.loop.display_loop_handler.behaviors = viewer_behaviors
                                history_console.is_rendered=True

                            elif main_console and history_console and history_console.is_rendered:
                                self.loop.sequenced_loop_handler.start()
                                if main_console and history_console:
                                    history_console.is_rendered=False
                    
                    case tcod.event.KeySym.I:
                        if self.display and self.loop.display_loop_handler:
                            main_console = self.display.get_window_by_name('main_window')                                        
                            inventory_console = self.display.get_window_by_name('inventory_window')
                                                                            
                            if main_console and inventory_console and not inventory_console.is_rendered:
                                self.loop.sequenced_loop_handler.stop()  # type: ignore
                                self.loop.display_loop_handler.behaviors = selector_behaviors
                                inventory_console.is_rendered=True

                            elif main_console and inventory_console and inventory_console.is_rendered:
                                self.loop.sequenced_loop_handler.start()
                                if main_console and inventory_console:
                                    inventory_console.is_rendered=False

        except Exception as e:
            print(f"An error occured with system action. {e}")
            traceback.print_exc()

system_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('inputevent', SystemKeyDownAction()),
}