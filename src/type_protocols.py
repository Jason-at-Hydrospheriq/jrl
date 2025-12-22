#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable, TypeVar, Set, Tuple
from transitions import Machine

@runtime_checkable
class StatefulObject(Protocol):
    """The StatefulObject Protocol is a mixin class that has a 'machine' attribute."""
    machine: Machine # Has a state machine that defines states and transitions.

@runtime_checkable
class StateStoreObject(Protocol):
    """The StateReferenceObject Protocol is a mixin class that has a 'state' attribute. It is used to refer to a StatefulObject instance for context."""
    store: StatefulObject | None 

@runtime_checkable
class StateActionObject(Protocol):
    """
    The StateActionObject Protocol is a mixin class that has a 'state' and 'transformer' attributes.
    
    Duck Types: StatefulObject
    
    """
    store: StatefulObject | None 
    transformer: Any | None

@runtime_checkable
class StateBehaviorObject(Protocol):
    """The StatefulBehaviorObject Protocol is a mixin class that has a 'state' and 'behaviors' attribute."""
    behaviors: Set[Tuple[str, StateActionObject]] | None # Has a set of behaviors (events/actions) that can be queued for execution by the game engine.

@runtime_checkable
class StateTransformer(StateStoreObject, StateBehaviorObject, Protocol):
    """
    The StateTransformer Protocol contains StateActionObject mappings (behaviors) and methods for queuing them
     in the Queue component of the STO State component. The execution flow is, given an STO as an input, the StateTransformer
     uses it to 'get_behavior' from the mapping, uses the STO's State component to 'set_context' on the behavior, then 
     'send_behavior' enqueues the contextualized behavior into the State component's Queue.
     
     Duck Types: StateStoreObject, StateBehaviorObject
     """

    T = TypeVar('T', bound=StateActionObject)
    
    def _transform(self, name: str) -> StateActionObject | None:
        """Retrieves a behavior (GameEvent or GameAction) by name from the behaviors set."""
        ...
    
    def _set_context(self, action: T, *args, **kwargs) -> T:
        """Must be overidden by subclasses. Sets the context of the StateActionObject item with the arguments."""
        ...

    def _send(self, action: StateActionObject)  -> bool:
        "This method should be overidden by subclasses. Enqueues the contextualized input_item into a GameState queue."
        ...
    
