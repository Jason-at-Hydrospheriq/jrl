#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from components.entities.factory import *
from typing import Set, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from components.entities.entity_lib import BaseEntity, BlockingEntity, Charactor, AICharactor
    from components.game_map import MapCoords

from components.entities.entity_lib import *
from components.game_map import MapCoords


class Roster:
    """ The Roster component manages the collection of all entities in the game. """

    __slots__ = ("entities", "spawn")
    
    entities: Set[BaseEntity]
    spawn: Callable

    def __init__(self) -> None:
        self.entities = set()    
        self.spawn = spawn

    @property
    def entity_locations(self) -> List[MapCoords]:
        return [entity.location for entity in self.entities if hasattr(entity, 'location')]

    @property
    def player(self) -> Charactor:
        for entity in self.entities:
            if isinstance(entity, Charactor) and entity.name == "Player":
                return entity
        raise ValueError("Player entity not found in roster.")
    
    @property
    def all_actors(self) -> List[BaseEntity]:
        potential_actors = [entity for entity in self.entities if hasattr(entity, 'is_alive')]
        return [entity for entity in potential_actors] #type: ignore
    
    @property
    def all_non_actors(self) -> List[BaseEntity]:
        potential_non_actors = [entity for entity in self.entities if not hasattr(entity, 'is_alive')]
        return [entity for entity in potential_non_actors] #type: ignore

    @property
    def entity_blocked_locations(self) -> List[MapCoords]:
        potential_blockers = [obj for obj in self.entities if hasattr(obj, 'blocks_movement')]
        return [blocker.location for blocker in potential_blockers if blocker.blocks_movement] #type: ignore
    
    @property
    def live_actors(self) -> List[BaseEntity]:
        potential_actors = [entity for entity in self.entities if hasattr(entity, 'is_alive')]
        return [entity for entity in potential_actors if entity.is_alive] #type: ignore
    
    @property
    def live_ai_actors(self) -> List[AICharactor]:
        return [entity for entity in self.live_actors if isinstance(entity, AICharactor)]

    def entity_collision(self, entity) -> BlockingEntity | None:
        """Check if the given entity's destination collides with any other entity that blocks movement."""
    
        for location in self.entity_blocked_locations:
            potential_blocker = self.get_entity_at_location(location)[0]
            if entity.destination == location and isinstance(potential_blocker, BlockingEntity):
                return potential_blocker  # Return the first blocking entity found.

        return None
    
    def get_entity_at_location(self, location: MapCoords) -> List[BaseEntity]:
        found_entity = []
        for entity in self.entities:
            if entity.location == location:
                found_entity += [entity]
        
        return found_entity