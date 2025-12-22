#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from type_protocols import *
from typing import TYPE_CHECKING, Set, Tuple, TypeVar
import tcod
from transitions import Machine

if TYPE_CHECKING:
    from core_components.store import GameStore


class BaseLoopHandler:
    """The GameHandler is responsible for tranforming Game Inputs and AI Actions into Game Events
    and sending them to the State Action Queue."""
    store: StatefulObject | None
    machine: Machine
    behaviors: Set[Tuple[str, StateActionObject]] | None # Has a set of behaviors (events/actions) that can be queued for execution by the game engine.
    T = TypeVar('T', bound=StateActionObject)

    def __init__(self, store: StatefulObject | None = None, behaviors: Set[Tuple[str, StateActionObject]] | None = None) -> None:
        self.store = store
        self.behaviors = behaviors
        states = ['started', 'stopped']
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]
        
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')
        
    def _transform(self, name: str) -> StateActionObject | None:
        """Should NOT be overidden by subclasses. Retrieves a behavior (Event or Action) by name from the behaviors set."""
        if self.behaviors is not None and self.is_started(): # type: ignore
            for behavior in self.behaviors:
                if name == behavior[0]:
                    action = behavior[1]
                    return deepcopy(action)

            raise ValueError(f"Behavior not found for event: {name}")
        raise ValueError(f"State behaviors object not found: {name}")
    
    def _set_context(self, action: T, *args, **kwargs) -> T:
        """Can be overidden by subclasses. Sets the context of the StateActionObject item with the arguments."""
        action.store = self.store
        action.transformer = self
        return action

    def _send(self, action: StateActionObject)  -> bool:
        "This method must be overidden by subclasses. Enqueues the contextualized input_item into a GameState queue."
        ...

    def _transform_send(self, event: StateActionObject | tcod.event.Event) -> bool:
        if self.is_started(): # type: ignore
            try:
                action = self._transform(event.__class__.__name__.lower())
                contextualized_action = None
                if action:
                    contextualized_action = self._set_context(action)
                
                if contextualized_action:
                    return self._send(contextualized_action)
                else:
                    return False
                
            except Exception as e:
                print(f"Handler error: {e}")
                return False
            
        return False

class BaseGameAction:
    store: StatefulObject | None
    transformer: BaseLoopHandler | None
    
    def __init__(self, store: GameStore| None = None, transformer: BaseLoopHandler | None = None) -> None:
        self.store = store
        self.transformer = transformer

    def perform(self) -> None:
        raise NotImplementedError("Subclasses must implement the perform method.")


class BaseGameEvent:
    store: StatefulObject | None
    transformer: BaseLoopHandler | None
    
    def __init__(self, store: GameStore| None = None, transformer: BaseLoopHandler | None = None) -> None:
        self.store = store
        self.transformer = transformer

    def trigger(self) -> None:
        if self.transformer:
            self.transformer._transform_send(self)
        
