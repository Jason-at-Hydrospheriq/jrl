#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, runtime_checkable, Set, Tuple, TypeVar, TYPE_CHECKING
from queue import Queue

if TYPE_CHECKING:
    from core_components.store import GameStore


@runtime_checkable
class GameStateObject(Protocol):
    state: GameStore | None


@runtime_checkable
class StateTransitionObject(GameStateObject, Protocol):
    transformer: object | None
    

@runtime_checkable
class GameAction(StateTransitionObject, Protocol):
    """ The Game Action is created by the Dispatcher and is sent to the State Actions queue.
    Actions have a 'perform' method that wraps the execution of a Dispatcher method. When the GameState pulls the Game Action from the queue, it
    calls the 'perform' method to execute the Handler method."""

    state: GameStore | None
    transformer: object | None # This should be set to the Handler that will handle any associated reaction events.
    
    def __init__(self) -> None:
        self.state = None
        self.transformer = None
    
    def perform(self) -> None:
        ...


@runtime_checkable
class GameEvent(StateTransitionObject, Protocol):
    """ The Game Event is created by a Handler and sent to the State Events queue. 
    Game Events have a 'trigger' method that wraps the execution of an associated 
    Dispatcher method. When the GameState pulls the Game Event from the queue, it
    calls the 'trigger' method to execute the Dispatcher method."""
    state: GameStore | None
    transformer: object | None # This should be set to the Dispatcher that will dispatch the associated action.

    def __init__(self) -> None:
        self.state = None
        self.transformer = None
        
    def trigger(self) -> None:
        ...


@runtime_checkable
class StateTransformer(Protocol):
    """The StateFormer Protocol is a mixin class that has a 'transform' method. The 'transform' method
      provides sets the attributes of StateTransitionObject instances with the Game State data required
      by the STO methods."""
    templates: Set[Tuple[str, StateTransitionObject]]

    T = TypeVar('T', bound=StateTransitionObject)

    def _enqueue(self, input_item: StateTransitionObject)  -> bool:
        
        if input_item.state is not None:
            output_item: StateTransitionObject | None
            output_items: Queue[StateTransitionObject]

            if isinstance(input_item, GameEvent):
                output_items = input_item.state.actions
            else:
                output_items = input_item.state.events

            try:

                output_item_name = type(input_item).__name__.lower()
                output_item = self.get_template(output_item_name)

                if output_item:
                    transformed_item = self.transform(output_item, input_item.state)
                    output_items.put(transformed_item)
                    return True
                
                return False
        
            except Exception as e:
                raise e
            
        return False
    
    def get_template(self, name: str) -> StateTransitionObject | None:
        for template in self.templates:
            if template[0] == name:
                return template[1]
        return None
    
    def transform(self, item: T, state: GameStore) -> T:
        item.state = state
        item.transformer = self
        return item

