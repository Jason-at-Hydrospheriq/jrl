#!/usr/bin/env python3
# -*- coding: utf-8 -*-M

from __future__ import annotations
from copy import deepcopy
from typing import Tuple, TypeVar, TypedDict, TYPE_CHECKING
import numpy as np  

if TYPE_CHECKING:
    from core_components.store import GameStore
    from core_components.entities.library import AICharactor, TargetableEntity

from core_components.ai.events import CharactorEvent, EntityEvent, AIEvent

AE = TypeVar('AE', bound=AIEvent)
EE = TypeVar('EE', bound=CharactorEvent)

# A typed dictionary for AI bots
class EntityStateTableDict(TypedDict):
    bits: Tuple[str, ...]
    vector_tuples: Tuple[Tuple[int, ...], ...]
    mapping: Tuple[TypeVar('E', bound=[AIEvent, EntityEvent])| None, ...] # type: ignore


manifest_example = EntityStateTableDict({   'bits': ('is_alive', 'is_spotted', 'is_spotting', 'is_targeting'),
                                        'vector_tuples': (  (0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 0, 1, 1),
                                                            (0, 1, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 1, 1, 1),
                                                            (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0), (1, 0, 1, 1),
                                                            (1, 1, 0, 0), (1, 1, 0, 1), (1, 1, 1, 0), (1, 1, 1, 1) ),
                                        'mapping': (  (None), (None), (None), (None),
                                                        (None), (None), (None), (None),
                                                        (None), (None), (AIEvent), (EntityEvent),
                                                        (None), (None), (AIEvent), (EntityEvent) ),
                    })


class BaseMachine:
    __slots__ = ("entity", "state", "state_table", "_state_matrix", "_state_mapping")
    entity: AICharactor
    state_table: EntityStateTableDict
    _state_matrix: np.ndarray
    _state_mapping: np.ndarray

    def __init__(self, entity: AICharactor | None, state_table: EntityStateTableDict | None = manifest_example) -> None:
        if entity:
            self.entity = entity

        if state_table:
            self.state_table = state_table
            self._set_state_matrix()
            self._set_state_mapping()

    def get_state_vector(self) -> np.ndarray:
        state_vector = [0, 0, 0, 0]  # Default state vector  

        try:
            for idx, bit in enumerate(self.state_table['bits']):
                state_name = str(bit)
                state_value = getattr(self.entity, state_name, 0)
                state_vector[idx] = int(state_value)
            return np.array(state_vector)
    
        except Exception as e:     
            raise e
    
    def get_event_from_state_vector(self, state_vector: np.ndarray) -> AIEvent | EntityEvent | float:
        try:
            index = np.where((self._state_matrix == state_vector).all(axis=1))[0]
            if index and index.size > 0:
                event = self._state_mapping[index[0]][0]
                return event
            return np.nan # shold be zero
            
        except Exception as e:     
            raise e
    
    def _set_state_matrix(self) -> None:
        try:

            state_vectors = self.state_table['vector_tuples']
            self._state_matrix = np.array(state_vectors)

        except Exception as e:     
            raise e

    def _set_state_mapping(self) -> None:
        try:

            state_mappings = np.full((len(self.state_table['mapping']),1), 0, dtype=object)
            for idx, mapping in enumerate(self.state_table['mapping']):
                if mapping:
                    state_mappings[idx] = mapping()
            
            self._state_mapping = state_mappings

        except Exception as e:     
            raise e

    def create_event(self, event: AE | EE, target: TargetableEntity, state: GameStore ) -> AE | EE | None:
        try:
            if event is not None:
                clone = deepcopy(event)
                clone.entity = self.entity

                if hasattr(clone, 'target'):
                    setattr(clone, 'target', target)
                if hasattr(clone, 'state'):
                    setattr(clone, 'state', state)
                
                return clone
            
        except Exception as e:     
            print(f"Error creating event: {e}")
            raise e
        
    def update_state(self, state: GameStore) -> None:
        v = self.get_state_vector()
        event_type = self.get_event_from_state_vector(v)
        event = None

        if event_type != 0 and self.entity.target is not None:
            event = self.create_event(event_type, target=self.entity.target, state=state) # type: ignore
        elif state.roster.player and event_type != 0 and self.entity.target is None:
            if self.entity.is_spotting and state.roster.player.is_spotted:
                event = self.create_event(event_type, target=state.roster.player, state=state) # type: ignore
            if event is not None: # type: ignore
                state.events.put(event) # type: ignore
        if event is not None:
            state.events.put(event)