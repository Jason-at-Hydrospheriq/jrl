#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from core_components.loops.custom_types import StateActionObject, StateHandler
from protocols import *
from typing import TYPE_CHECKING, Any, Set, Tuple, TypeVar
from queue import Queue
import tcod
from transitions import Machine

if TYPE_CHECKING:
    from core_components.store import GameStore


class BaseGameAction:
    store: StatefulObject | None
    handler: StateHandler | None
    
    def __init__(self, store: StatefulObject | None = None, handler: StateHandler | None = None) -> None:
        self.store = store
        self.handler = handler
    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")


class BaseGameEvent:
    store: StatefulObject | None
    handler: StateHandler | None
    
    def __init__(self, store: StatefulObject | None = None, handler: StateHandler | None = None) -> None:
        self.store = store
        self.handler = handler
        
    def trigger(self) -> None:
        raise NotImplementedError("Subclasses must implement the trigger method.")
        

class BaseGameTransformer:
    """The BaseGameTransformer is responsible for tranforming Game Inputs and AI Actions into Game Events."""
    store: StatefulObject | None
    behaviors: Set[Tuple[str, StateActionObject]] | None # Has a set of behaviors (events/actions) that can be queued for execution by the game engine.
    T = TypeVar('T', bound=StateActionObject)

    def __init__(self, store: StatefulObject | None = None, behaviors: Set[Tuple[str, StateActionObject]] | None = None) -> None:
        self.store = store
        self.behaviors = behaviors

    def _transform(self, name: str) -> StateActionObject | None:
        """Should NOT be overidden by subclasses. Retrieves a behavior (Event or Action) by name from the behaviors set."""
        if self.behaviors is not None and self.is_started(): # type: ignore
            for behavior in self.behaviors:
                if name == behavior[0]:
                    action = behavior[1]
                    return self._set_context(deepcopy(action))

            raise ValueError(f"Behavior not found for event: {name}")
        raise ValueError(f"State behaviors object not found: {name}")
    
    def _set_context(self, action: T, *args, **kwargs) -> T:
        """Can be overidden by subclasses. Sets the context of the StateActionObject item with the arguments."""
        action.store = self.store # type: ignore
        action.handler = self # type: ignore
        return action


class BaseGameLoop:
    store: StatefulObject | None
    events: Queue[StateActionObject]
    actions: Queue[StateActionObject]

    def __init__(self, store: StatefulObject | None = None) -> None:
        self.store = store
        self.events = Queue()
        self.actions = Queue()

    def _send(self, action: StateActionObject)  -> bool:
        try:

            if isinstance(action, BaseGameEvent):
                self.events.put(action)
                return True
            
            elif isinstance(action, BaseGameAction):
                self.actions.put(action)
                return True
                    
            return False
        
        except Exception as e:
            raise e
        
        
class BaseGameHandler(BaseGameLoop, BaseGameTransformer):
    """The BaseGameHandler is responsible for tranforming Game Inputs and AI Actions into Game Events
    and sending them to the appropriate Queue."""
    machine: Machine

    def __init__(self, store: StatefulObject | None = None, behaviors: Set[Tuple[str, StateActionObject]] | None = None) -> None:
        super().__init__(store=store)
        BaseGameTransformer.__init__(self, store=store, behaviors=behaviors) # type: ignore
        states = ['started', 'stopped']
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]
        
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')

    def handle(self, event: StateActionObject | Any | None = None) -> bool:
        if event is not None:
            return self._transform_send(event) # type: ignore
        
        return False