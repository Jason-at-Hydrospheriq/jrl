#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations  
from typing import TYPE_CHECKING, Dict, Tuple, cast
import numpy as np
import tcod
import traceback

from entities.behaviors.entity import EntityUseItemAction
from entities.behaviors.system import WaitAction, NoAction
from baseclasses import BaseGameAction

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler


class SelectorKeyDownAction(BaseGameAction):
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
                player = self.store.portfolio.player if self.store.portfolio else None # type: ignore
                
                if player and self.store and self.handler:
                    index = self.input_event.sym - tcod.event.KeySym.A
                    items = [item for item in player.inventory.slots.values() if player.inventory]

                    if 0 <= index <= 26 and index < len(items):
                        item_name = items[index].name
                        EntityUseItemAction(self.store, self.handler, item_name).perform() # type: ignore | The store for this action must be GameStore.

        except Exception as e:
            print(f"An error occured with selector action. {e}")
            traceback.print_exc()

selector_behaviors = {
    ('nonevent', NoAction()),
    ('waitevent', WaitAction()),
    ('inputevent', SelectorKeyDownAction()),
}