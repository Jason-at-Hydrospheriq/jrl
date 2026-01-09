#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine
from game_types import StatefulObject
from typing import Dict, Tuple, TYPE_CHECKING
import numpy as np

from atlas_components.tiles.base import TileCoordinate, TileTuple

if TYPE_CHECKING:
    from engine_components.store import GameStore

from functools import wraps

def is_locked(func):
    """A decorator to wrap each method with a condition check."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # Access the condition from the instance (self)
        if self.action_locked:
            return None # Or raise an exception, or handle as needed
        return func(self, *args, **kwargs)
    return wrapper

def action_locked(cls):
    """A class decorator to apply the condition_checker to all methods."""
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith('__'):
            # Wrap the method with the condition checker
            setattr(cls, attr_name, is_locked(attr_value))

        if isinstance(attr_value, property):
            if attr_value.fset:
                # Wrap the setter method of the property
                setter = attr_value.fset
                if setter and callable(setter):
                    wrapped_setter = is_locked(setter)
                else:
                    wrapped_setter = setter

                # Create a new property with the wrapped methods
                new_property = property(attr_value.fget, wrapped_setter)
                setattr(cls, attr_name, new_property)

    return cls


class BaseSubState:
    machine: Machine
    name: str
    store: StatefulObject

    # Set defaults in subclasses
    _state_bits: Tuple[str, ...]
    _states: Tuple[Dict, ...]
    _transitions: Tuple[Dict, ...]
    _initial_state: str

    def __init__(self, name: str, store: StatefulObject):
        self.name = name
        self.store = store
    
        machine = Machine(model=self, states=self._states, transitions=self._transitions, initial=self._initial_state)
        self.machine = machine

    def set_bits(self) -> None:
        pass # Define in subclasses


class BaseParentState:
    machine: Machine
    substates: list[BaseSubState]
    state_vector: Dict[str, bool]
    state_vector_dtype: np.dtype
    # Define in subclasses
    _substates_manifest: Tuple[Tuple[str, type[BaseSubState]], ...]

    def __init__(self):
        self.substates = []
        self.state_vector = {}
        self.machine = Machine(model=self, states=[], transitions=[])
        
        for name, substate in self._substates_manifest:        
            self._add_substate(substate(name=name, store=self))

    def update(self) -> None:
        for substate in self.substates:
            try:
                substate.set_bits()
                substate.update() # type: ignore
                
            except Exception as e:
                raise e
    
    def _add_substate(self, substate: BaseSubState) -> None:
        self.substates.append(substate)
        for bit in substate._state_bits:
            self.state_vector[bit] = False
        self.__setattr__(substate.name.lower(), substate) #type: ignore


class BaseGameSubState(BaseSubState):
    """
    A generic substate for game entity_components

    Duck Types: EntitySubState, BaseSubState
    """
    _state_bits = ('on_map',)
    _states = ({'name': 'in_play'}, 
               {'name': 'not_in_play'})
    _transitions = (
        {'trigger':'update', 'source':'not_in_play', 'dest':'in_play', 'conditions':['is_on_map']},
        {'trigger':'update', 'source':'in_play', 'dest':'not_in_play', 'conditions':['is_not_on_map']})
    _initial_state = 'not_in_play'

    def set_bits(self) -> None:
        self.store.state_vector['on_map'] = self.store.location is not None #type: ignore

    # All substates must have the primary state bit methods
    def is_on_map(self) -> bool:
        return self.store.state_vector['on_map'] # type: ignore

    def is_not_on_map(self) -> bool:
        return not self.store.state_vector['on_map'] # type: ignore
    
@action_locked
class BaseGameEntity(BaseParentState):
    """
    A generic object to represent players, enemies, items, etc.

    Duck Types: StatefulObject, StateStoreObject, GameEntity, BaseParentState
    """
    store: StatefulObject | None
    machine: Machine
    location: TileCoordinate | None
    blocks_movement: bool | None
    is_invulnerable: bool | None
    action_locked: bool | None
    _hp: int | None
    _max_hp: int | None
    name: str
    symbol: str
    color: Tuple[int, int, int] # Do this like the maps. Numpy datatypes mapped to state.

    # Substate definition
    _substates_manifest = (
        ("spawn", BaseGameSubState),
    )

    def __init__(self,
                 store: GameStore | None = None,
                 *,                 
                 location: TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__()
        
        self.store = store
        parent_map_size = TileTuple(([100], [100]))

        if self.store:
            parent_map_size = self.store.atlas.active.grid.size  # type: ignore
        
        if not hasattr(self, 'location'):
            self.location = location

        if not hasattr(self, 'symbol'):
            self.symbol = symbol
    
        if not hasattr(self, 'color'):
            self.color = color
        
        if not hasattr(self, 'name'):
            self.name = name

        self.blocks_movement = True
        self.is_invulnerable = False
        self._hp = 0
        self._max_hp = 1
        self.action_locked = False

        self.update()
    
    @property
    def hp(self) -> int | None:
        if not self.is_invulnerable:
            return self._hp
        return None
    
    @hp.setter
    def hp(self, value: int | None) -> None:
        if not self.is_invulnerable:
            self._hp = value
            self.update()

    @property
    def max_hp(self) -> int | None:
        if not self.is_invulnerable:
            return self._max_hp
        return None
    
    @max_hp.setter
    def max_hp(self, value: int | None) -> None:
        if not self.is_invulnerable:
            self._max_hp = value
            self.update()