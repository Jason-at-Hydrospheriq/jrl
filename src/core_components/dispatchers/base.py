# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from typing import List, Protocol, TYPE_CHECKING
import tcod
import tcod.event

if TYPE_CHECKING:
    from state import GameState

from core_components.events.library import BaseGameEvent
from core_components.actions.library import BaseStateAction, NoAction, GameStartAction, SystemExitAction, GameOverAction


NOACTION = NoAction()
GAMEOVER = GameOverAction()
GAMESTART = GameStartAction()
SYSTEMEXIT = SystemExitAction()


class BaseEventDispatcher(Protocol):

    def dispatch(self, 
                 event: tcod.event.Event | BaseGameEvent | None = None,
                 state: GameState | None = None) -> List[BaseStateAction]:
       
        method_name = "_ev_" + event.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method:
            return method(event)
        return []
    
    @staticmethod
    def create_state_action(action: BaseStateAction, 
                      state: GameState) -> BaseStateAction:
        clone = deepcopy(action)
        clone.state = state
        return clone

    def _ev_quit(self, 
                 event: tcod.event.Quit, 
                 state: GameState) -> List[BaseStateAction]:
        return [self.create_state_action(SYSTEMEXIT, state)]
