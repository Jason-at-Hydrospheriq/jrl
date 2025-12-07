# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from typing import List, Protocol, Sequence
import tcod
import tcod.event

from components.queues.event_lib import BaseGameEvent
from src.state import GameState
from components.dispatchers.action_lib import BaseStateAction, NoAction, GameStartAction, SystemExitAction, GameOverAction

NOACTION = NoAction()
GAMEOVER = GameOverAction()
GAMESTART = GameStartAction()
SYSTEMEXIT = SystemExitAction()


class BaseEventDispatcher(Protocol):
    state: GameState

    def dispatch(self, 
                 event: tcod.event.Event | BaseGameEvent | None = None) -> List[BaseStateAction]:
       
        method_name = "_ev_" + event.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method:
            return method(event)
        return []
    
    def create_action(self, action: BaseStateAction) -> BaseStateAction:
        clone = deepcopy(action)
        clone.state = self.state
        return clone

    def _ev_quit(self, event: tcod.event.Quit) -> List[BaseStateAction]:
        return [self.create_action(SYSTEMEXIT)]
