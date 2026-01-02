#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from transitions import Machine
from type_protocols import StatefulObject
from typing import Dict, Tuple, TYPE_CHECKING
import numpy as np

from core_components.maps.tiles.base import TileCoordinate, TileTuple

if TYPE_CHECKING:
    from core_components.store import GameStore

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
    
        for name, substate in self._substates_manifest:        
            self._add_substate(substate(name=name, store=self))

    def update(self) -> None:
        for substate in self.substates:
            substate.set_bits()
            substate.update() # type: ignore
    
    def _add_substate(self, substate: BaseSubState) -> None:
        self.substates.append(substate)
        for bit in substate._state_bits:
            self.state_vector[bit] = False
        self.__setattr__(substate.name.lower(), substate) #type: ignore


class BaseGameSubState(BaseSubState):
    """
    A generic substate for game entities.

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
    

class BaseGameEntity(BaseParentState):
    """
    A generic object to represent players, enemies, items, etc.

    Duck Types: StatefulObject, StateStoreObject, GameEntity, BaseParentState
    """
    store: StatefulObject | None
    machine: Machine
    location: TileCoordinate | None
    blocks_movement: bool | None
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
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__()
        self.store = store
        parent_map_size = TileTuple(([100], [100]))
        
        if isinstance(location, tuple):
            self.location = TileCoordinate.from_tuple(location, parent_map_size=parent_map_size)
        else:
            self.location = location
            
        self.blocks_movement = True
        self.symbol = symbol
        self.color = color
        self.name = name
        self.update()