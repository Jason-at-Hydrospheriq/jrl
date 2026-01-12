#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  
from typing import TYPE_CHECKING, Dict, Tuple, cast
import numpy as np
import tcod

from entities.behaviors.system import WaitAction, NoAction
from baseclasses import BaseGameAction

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler


class KeyDownAction(BaseGameAction):
    input_event: tcod.event.Event | None
    cursor_position: int = 0
    cursor_keys: Dict[tcod.event.KeySym, int] = {
        tcod.event.KeySym.UP: -1,
        tcod.event.KeySym.DOWN: 1,
        tcod.event.KeySym.PAGEUP: -5,
        tcod.event.KeySym.PAGEDOWN: 5
    }
    def __init__(self, store: GameStore | None = None, handler: SubLoopHandler | None = None, input_event: tcod.event.KeyboardEvent | None = None) -> None:
        super().__init__(store, handler)
        self.input_event = input_event

    def perform(self) -> None:
        if isinstance(self.input_event, tcod.event.KeyboardEvent):
            key_sym = self.input_event.sym
            if key_sym in self.cursor_keys:
                adjust = self.cursor_keys[key_sym]
                # Parse movement keys
                if adjust < 0 and self.cursor_position == 0:
                    pass
                
viewer_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('inputevent', KeyDownAction()),
}