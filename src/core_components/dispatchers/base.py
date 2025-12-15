# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
import queue
from typing import List, Protocol, TYPE_CHECKING
from queue import Queue
import tcod
import tcod.event

if TYPE_CHECKING:
    from core_components.state import GameState

from core_components.events.library import BaseGameEvent
from core_components.actions.library import BaseGameAction, NoAction, SystemExitAction


class BaseEventDispatcher(Protocol):
    # List of all possible actions that can be dispatched.
    # A similar list should be included in each subclass of BaseEventDispatcher.

    SYSTEMEXIT = SystemExitAction()
    NOACTION = NoAction()

    def test(self,  
                 event_queue: Queue[BaseGameEvent],
                 action_queue: Queue[BaseGameAction]) -> None:
        
        while True:
            try:
                event = event_queue.get()
                print(f"Processing event: {event.__class__.__name__.lower()}")
                action_queue.put(NoAction())  # If no method is found, return a list with a NoAction.
                event_queue.task_done()

            except:
                break

    def dispatch(self, 
                 event: BaseGameEvent | tcod.event.Event,
                 actions: Queue[BaseGameAction],
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
            
    @staticmethod
    def create_state_action(action: BaseGameAction, 
                      state: GameState) -> BaseGameAction:
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
                 state: GameState) -> List[BaseGameAction]:
        return [self.create_state_action(self.SYSTEMEXIT, state)]