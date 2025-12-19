#!/usr/bin/env python3
# -*- coding: utf-8 -*-M

from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, Tuple, TypeVar, TypedDict, TYPE_CHECKING
import numpy as np  
import tcod

from core_components.entities.library import AICharactor, AIEntity, BaseEntity, Charactor, MobCharactor, TargetableEntity
from core_components.events.library import BaseGameEvent, EntityEvent, AIEvent

if TYPE_CHECKING:
    from state import GameState

AE = TypeVar('AE', bound=AIEvent)
EE = TypeVar('EE', bound=EntityEvent)

# A typed dictionary for AI bots
class AIStateTableDict(TypedDict):
    bits: Tuple[str, ...]
    vector_tuples: Tuple[Tuple[int, ...], ...]
    mapping: Tuple[TypeVar('E', bound=[AIEvent, EntityEvent])| None, ...] # type: ignore


manifest_example = AIStateTableDict({   'bits': ('is_alive', 'is_spotted', 'is_spotting', 'is_targeting'),
                                        'vector_tuples': (  (0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 0, 1, 1),
                                                            (0, 1, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 1, 1, 1),
                                                            (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0), (1, 0, 1, 1),
                                                            (1, 1, 0, 0), (1, 1, 0, 1), (1, 1, 1, 0), (1, 1, 1, 1) ),
                                        'mapping': (  (None), (None), (None), (None),
                                                        (None), (None), (None), (None),
                                                        (None), (None), (AIEvent), (EntityEvent),
                                                        (None), (None), (AIEvent), (EntityEvent) ),
                    })
class BaseAI:
    __slots__ = ("entity", "state", "state_table", "_state_matrix", "_state_mapping")
    entity: AICharactor
    state: GameState
    state_table: AIStateTableDict
    _state_matrix: np.ndarray
    _state_mapping: np.ndarray

    def __init__(self, entity: AICharactor | None, state: GameState | None = None, state_table: AIStateTableDict | None = manifest_example) -> None:
        if entity:
            self.entity = entity
        if state:
            self.state = state
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
            return np.nan
            
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
                    state_mappings[idx] = mapping
            
            self._state_mapping = state_mappings

        except Exception as e:     
            raise e

    def create_event(self, event: AE | EE, target: TargetableEntity, state: GameState ) -> AE | EE | None:

        if event is not None:
            clone = deepcopy(event)
            clone.entity = self.entity

            if hasattr(clone, 'target'):
                setattr(clone, 'target', target)
            if hasattr(clone, 'state'):
                setattr(clone, 'state', state)
            
            return clone
    
    def update_state(self) -> None:
        v = self.get_state_vector()
        event_type = self.get_event_from_state_vector(v)
        if event_type is not None and self.entity.target is not None:
            event = self.create_event(event_type, target=self.entity.target, state=self.state)
            if event is not None:
                self.state.events.put(event)



class MobAI(BaseAI):
    def __init__(self, entity: MobCharactor | None) -> None:
        super().__init__(entity)

    def perceive_state(self) -> None:
        pass

        # State perception
        # self.entity.is_alive
        # self.entity.is_near_death
        # self.entity.targeted
        # self.entity.targeting
        # self.entity.in_target_missile_range
        # self.entity.target_in_missile_range
        # self.entity.in_target_melee_range
        # self.entity.target_in_melee_range
        # self.entity.in_target_spell_range
        # self.entity.target_in_spell_range

        

    # def create_event(self) -> AIEvent | None:
    #     pass











        # # Acquire target if none exists or if target is dead
        # if self.entity.in_player_fov:
        #     if not self.target or not self.target.is_alive:
        #         self.target = self.engine.player

        #     # Recalculate path to target
        #     self.path = self.get_path_to(self.target.location) if self.target else []

        # if self.target:
        #     if self.distance_to_target is not None:
        #         if self.distance_to_target <= 1:
        #             return AIEventTargetInMeleeRange(self.entity, self.target)
                
        #         else:
        #             if self.path:
        #                 return AIEventPathToTarget(self.entity, self.path[0])
            
        # return AIEventNone(self.entity)
