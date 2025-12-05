#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
from components.entities import Charactor, AICharactor, BaseEntity, EntityTypes, ActorTypes, PhysicalObject
from components.attributes.stats import PhysicalStats, MentalStats, CombatStats
from typing import Set, List
from components.game_map import MapCoords

    
#Type variable used for type hinting 'self' returns
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
    entities: Set[BaseEntity | PhysicalObject | Charactor | AICharactor]

    def __init__(self) -> None:
        self.entities = set()    

    @property
    def entity_locations(self) -> List[MapCoords]:
        return [entity.location for entity in self.entities if hasattr(entity, 'location')]

    @property
    def entity_blocked_locations(self) -> List[MapCoords]:
        potential_blockers = [obj for obj in self.entities if hasattr(obj, 'blocks_movement')]
        return [blocker.location for blocker in potential_blockers if blocker.blocks_movement] #type: ignore
    
    @property
    def live_actors(self) -> List[EntityTypes]:
        potential_actors = [entity for entity in self.entities if hasattr(entity, 'is_alive')]
        return [entity for entity in potential_actors if entity.is_alive] #type: ignore
    
    @property
    def live_ai_actors(self) -> List[AICharactor]:
        return [entity for entity in self.live_actors if isinstance(entity, AICharactor)]

    def entity_collision(self, entity) -> bool:
        """Check if the given entity's destination collides with any other entity that blocks movement."""
    
        for location in self.entity_blocked_locations:
            if entity.destination == location:
                return True
        return False
    
    def spawn(self, original: BaseEntity, location: MapCoords):
        """Spawn a copy of this entity at the given location."""
        clone = deepcopy(original)
        clone.location = location
        self.entities.add(clone)
    
    def get_entity_at_location(self, location: MapCoords) -> List[EntityTypes]:
        found_entity = []
        for entity in self.entities:
            if entity.location == location:
                found_entity += [entity]
        
        return found_entity