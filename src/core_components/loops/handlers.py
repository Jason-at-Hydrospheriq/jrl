#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from queue import Queue
from typing import TYPE_CHECKING
import tcod
from type_protocols import *

if TYPE_CHECKING:
    from core_components.store import GameStore

from core_components.loops.base import BaseLoopHandler, BaseGameAction, BaseGameEvent
from core_components.loops.actions import NoAction


class GameLoopHandler(BaseLoopHandler):
    """The GameLoopHandler is responsible for tranforming Game Inputs and AI Actions into Game Events
    and sending them to the Store Action Queue."""
    
    events: Queue[BaseGameEvent | tcod.event.Event]
    actions: Queue[BaseGameAction]

    def __init__(self, store: GameStore | None = None) -> None:
        game_behaviors = {
                        ('nonevent', NoAction()),
                        }
        
        super().__init__(store=store, behaviors=game_behaviors) # type: ignore
    
    def _send(self, action: StateActionObject)  -> bool:
        try:

            if isinstance(action, BaseGameEvent) and isinstance(action.store, GameStore):
                self.events.put(action)
                return True
            
            elif isinstance(action, BaseGameAction) and isinstance(action.store, GameStore):
                self.actions.put(action)
                return True
                    
            return False
        except Exception as e:
            raise e
        
    def handle(self, event: BaseGameEvent | tcod.event.Event | None = None) -> bool:
        if event is not None:
                return self._transform_send(event)
        
        return False