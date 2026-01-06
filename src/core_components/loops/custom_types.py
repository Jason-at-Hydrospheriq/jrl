#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from queue import Queue

from transitions import Machine
from protocols import StatefulObject, StoredStateObject
from typing import TYPE_CHECKING, Any, Protocol, Set, Tuple, runtime_checkable

from core_components.maps.tiles.base import TileCoordinate


@runtime_checkable
class StateActionObject(Protocol):
    """
    A StateActionObject is any object with 'store' and 'handler' attributes. The 'store' attribute refers to a StatefulObject instance for context,
    and the 'handler' attribute refers to a StateHandler instance that can transform and send the object to a State queue.

    Duck Types: StatefulObject

    """
    store: StatefulObject | None
    handler: StateHandler | None


@runtime_checkable
class StateBehaviorObject(Protocol):
    """The StatefulBehaviorObject Protocol is a mixin class that has a 'state' and 'behaviors' attribute."""
    behaviors: Set[Tuple[str, StateActionObject]] | None # Has a set of behaviors (events/actions) that can be queued for execution by the game engine.


@runtime_checkable
class EventTransformer(Protocol):
    """
    The EventTransformer Protocol is a mixin class that has methods for sending events and transformed actions to queues.
    
    Duck Types: StatefulObject
    """
    store: StatefulObject | None
    behaviors: set[tuple[str, StateActionObject]] | None

    def transform(self, event: StateActionObject) -> StateActionObject | None:
        """Transforms an event into an action based on the defined behaviors."""
        ...


@runtime_checkable
class GameLoopObject(Protocol):
    """
    The GameLoopObject Protocol is a mixin class that has an events and actions queue.
    
    Duck Types: StatefulObject
    """
    store: StatefulObject | None
    events: Queue[StateActionObject]
    actions: Queue[StateActionObject]
    
    def send(self, loop_item: StateActionObject) -> bool:
        """Sends an event or action to the appropriate queue."""
        ...


@runtime_checkable
class StateHandler(EventTransformer, GameLoopObject, Protocol):
    """
    The StateHandler Protocol is a mixin class that combines the EventTransformer and GameLoopObject Protocols.
    
    Duck Types: StatefulObject
    """
    store: StatefulObject | None
    behaviors: set[tuple[str, StateActionObject]] | None
    events: Queue[StateActionObject]
    actions: Queue[StateActionObject]
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



