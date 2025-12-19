# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
import queue
from typing import List, Protocol, TYPE_CHECKING, TypeVar
from queue import Queue
import tcod
import tcod.event

if TYPE_CHECKING:
    from state import GameState

from core_components.events.library import BaseGameEvent
from core_components.actions.library import BaseGameAction, GeneralAction, NoAction, SystemExitAction

T = TypeVar('T', bound=GeneralAction)

class BaseEventDispatcher(Protocol):
    # List of all possible actions that can be dispatched.
    # A similar list should be included in each subclass of BaseEventDispatcher.

    SYSTEMEXIT = SystemExitAction()
    NOACTION = NoAction()

    def dispatch(self, 
                 event: BaseGameEvent | tcod.event.Event,
                 actions: Queue[GeneralAction],
                 state: GameState) -> bool:
            
        try:

            method_name = "_ev_" + event.__class__.__name__.lower()
            method = getattr(self, method_name, None)

            if method is not None:
                actions.put(method(event, state)) # Convert the event into a list of actions to take.
                return True
            
            return False
            
        except Exception as e:
            raise e
        
    @classmethod
    def create_state_action(cls, action: T, state: GameState) -> T:
        
        """ This method creates a copy of the action and adds the state to it. If the action is not a subclass of GeneralAction, it will raise an error. 
        Subclasses of BaseEventDispatcher can override this method to add additional state information to the action. """

        clone = deepcopy(action)
        clone.state = state
        return clone

    @staticmethod        
    def is_subclass(instance, cls: type) -> bool:
        instance_mro = set([x.__name__ for x in instance.__class__.mro()])
        cls_mro = set([x.__name__ for x in cls.mro()])
        return instance_mro.issuperset(cls_mro)

    def _ev_quit(self, 
                 event: tcod.event.Quit, 
                 state: GameState) -> List[GeneralAction]:
        return [self.create_state_action(self.SYSTEMEXIT, state)]