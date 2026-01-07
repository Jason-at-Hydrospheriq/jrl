#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import Protocol, AbstractSet, Tuple, TypeVar, runtime_checkable
from transitions import Machine
from queue import Queue
import numpy as np

from atlas_components.tiles.base import TileCoordinate


@runtime_checkable
class StatefulObject(Protocol):
    """The StatefulObject Protocol is a mixin class that has a 'machine' attribute."""
    machine: Machine # Has a state machine that defines states and transitions.


@runtime_checkable
class StoredStateObject(Protocol):
    """The StoredStateObject Protocol is a mixin class that has a 'store' attribute. It is used to refer to a StatefulObject instance for context."""
    store: StatefulObject | None 


@runtime_checkable
class StateActionObject(Protocol):
    """
    A StateActionObject is any object with 'store' and 'handler' attributes. The 'store' attribute refers to a StatefulObject instance for context,
    and the 'handler' attribute refers to a StateHandler instance that can transform and send the object to a State queue.

    Duck Types: StatefulObject

    """
    store: StatefulObject | None
    handler: StateHandler | None

S = TypeVar('S', bound=StateActionObject, covariant=True)

@runtime_checkable
class StateBehaviorObject[S](Protocol):
    """The StatefulBehaviorObject Protocol is a mixin class that has a 'state' and 'behaviors' attribute."""
    behaviors: AbstractSet[Tuple[str, S]] | None # Has a set of behaviors (events/actions) that can be queued for execution by the game engine.


@runtime_checkable
class EventTransformer[S](StateBehaviorObject, Protocol):
    """
    The EventTransformer Protocol is a mixin class that has methods for sending events and transformed actions to queues.
    
    Duck Types: StatefulObject
    """
    store: StatefulObject | None

    def transform(self, event: StateActionObject) -> StateActionObject | None:
        """Transforms an event into an action based on the defined behaviors."""
        ...


@runtime_checkable
class GameLoopObject[S](Protocol):
    """
    The GameLoopObject Protocol is a mixin class that has an events and actions queue.
    
    Duck Types: StatefulObject
    """
    store: StatefulObject | None
    events: Queue[S]
    actions: Queue[S]
    
    def send(self, loop_item: StateActionObject) -> bool:
        """Sends an event or action to the appropriate queue."""
        ...


@runtime_checkable
class StateHandler[S](EventTransformer, GameLoopObject, Protocol):
    """
    The StateHandler Protocol is a mixin class that combines the EventTransformer and GameLoopObject Protocols.
    
    Duck Types: StatefulObject
    """
    machine: Machine
    
    def handle(self, event: StateActionObject | None) -> bool:
        """Handles an event by transforming and sending it to the appropriate queue."""
        ...


@runtime_checkable
class EntityActionObject(StateActionObject, Protocol):
    """The EntityActionObject Protocol is a mixin class that has an 'entity' attribute."""
    entity: StatefulObject | None


@runtime_checkable
class EntityDestinationObject(EntityActionObject, Protocol):
    """The EntityDestinationObject Protocol is a mixin class that has a 'destination' attribute."""
    destination: TileCoordinate | None


@runtime_checkable
class EntityTargetObject(EntityActionObject, Protocol):
    """The EntityTargetObject Protocol is a mixin class that has a 'target' attribute."""
    target: StatefulObject | None


@runtime_checkable
class GameAction(StateActionObject, Protocol):
    """
    The GameAction Protocol is a mixin class that has 'store' and 'handler' attributes. The 'store' attribute refers to a StatefulObject instance for context,
    and the 'handler' attribute refers to a StateHandler instance that can transform and send the action to a State queue.

    Duck Types: StatefulObject

    """

    def perform(self) -> None:
        """Performs the action."""
        ... 
    
@runtime_checkable
class GameEvent(StateActionObject, Protocol):
    """
    The GameEvent Protocol is a mixin class that has 'store' and 'handler' attributes. The 'store' attribute refers to a StatefulObject instance for context,
    and the 'handler' attribute refers to a StateHandler instance that can transform and send the action to a State queue.

    Duck Types: StatefulObject

    """

    def trigger(self) -> None:
        """Performs the action."""
        ... 

@runtime_checkable
class EntitySubState(Protocol):
    machine: Machine
    name: str
    store: StatefulObject
    state_bit_dtypes: Tuple[np.dtype, ...]


@runtime_checkable
class EntityParentState(Protocol):
    machine: Machine
    substates: list[EntitySubState]


@runtime_checkable
class GameEntity(Protocol):
    """The EntityActionObject Protocol is a mixin class that has an 'entity' attribute."""
    store: StatefulObject | None
    machine: Machine
    location: TileCoordinate | None
    blocks_movement: bool | None