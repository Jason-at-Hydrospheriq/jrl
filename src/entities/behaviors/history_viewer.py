#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  
from typing import TYPE_CHECKING, Dict, Tuple, cast
import numpy as np
import tcod
import traceback

from entities.behaviors.system import WaitAction, NoAction
from baseclasses import BaseGameAction

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler


class KeyDownAction(BaseGameAction):
    input_event: tcod.event.Event | None
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
        try:
            if isinstance(self.input_event, tcod.event.KeyboardEvent) and self.store:
                log_length = len(self.store.log.messages)  # type: ignore
                cursor = self.store.log.cursor  # type: ignore

                key_sym = self.input_event.sym
                if key_sym in self.cursor_keys:
                    adjust = self.cursor_keys[key_sym]
                    # Parse movement keys
                    if adjust < 0 and cursor == 0:
                        # Only move from the top to the bottom when you're on the edge.
                        cursor = log_length - 1
                    elif adjust > 0 and cursor == log_length - 1:
                        cursor = 0
                    else:
                        cursor = max(0, min(cursor + adjust, log_length - 1))

                elif key_sym == tcod.event.KeySym.HOME:
                    cursor = 0  # Move directly to the top message.
                
                elif key_sym == tcod.event.KeySym.END:
                    cursor = log_length - 1

                self.store.log.cursor = cursor  # type: ignore
        
        except Exception as e:
            print(f"An error occured with viewer action. {e}")
            traceback.print_exc()

viewer_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('inputevent', KeyDownAction()),
}