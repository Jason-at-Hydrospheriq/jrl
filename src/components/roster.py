#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from src.resources.entities import BlockingEntity, Charactor, AICharactor, BaseEntity, TargetableEntity
from components.attributes.stats import PhysicalStats, MentalStats, CombatStats
from typing import Set, List
from components.game_map import MapCoords

    
# Spawnable entity templates
PLAYER = Charactor(name="Player", char="@", color=(255, 255, 255),
                   physical=PhysicalStats(max_hp=30, constitution=14),
                   combat=CombatStats(defense=2, attack_power=5))

ORC = AICharactor(name="Orc", char="o", color=(63, 127, 63),
                  ai_cls=None, 
                  physical=PhysicalStats(max_hp=10, constitution=12),
                  combat=CombatStats(defense=0, attack_power=3))

TROLL = AICharactor(name="Troll", char="T", color=(0, 127, 0), 
                    ai_cls=None,
                    physical=PhysicalStats(max_hp=16, constitution=12),
                    combat=CombatStats(defense=1, attack_power=4))


class Roster:
    """ The Roster component manages the collection of all entities in the game. """

    __slots__ = ("entities",)
    
    entities: Set[BaseEntity]

    def __init__(self) -> None:
        self.entities = set()    

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
    
    def spawn(self, original: BaseEntity, location: MapCoords):
        """Spawn a copy of this entity at the given location."""
        clone = deepcopy(original)
        clone.location = location
        self.entities.add(clone)
    
    def get_entity_at_location(self, location: MapCoords) -> List[BaseEntity]:
        found_entity = []
        for entity in self.entities:
            if entity.location == location:
                found_entity += [entity]
        
        return found_entity