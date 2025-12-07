#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from components.entities.factory import *
from typing import Set, List, Callable, TYPE_CHECKING
import random
import numpy as np

if TYPE_CHECKING:
    from src.components.entities.library import BaseEntity, BlockingEntity, Charactor, AICharactor
    from components.maps.base import MapCoords, BaseMapGenerator
    from components.game_map import GameMap

from src.components.entities.library import *


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
    
    def initialize_random_mobs(self, game_map: GameMap, max_total_mobs: int, max_mobs_per_room: int) -> None:
        """Generate mobs """
        n_total_mobs_spawned_in_this_map = 0
        min_total_mobs_in_this_map = len(game_map.rooms) * max_mobs_per_room
        max_total_mobs_in_this_map = random.randint(min_total_mobs_in_this_map, max_total_mobs)
        
        # Generate mobs in rooms
        for room in game_map.rooms:
            max_mobs_in_this_room = random.randint(1, max_mobs_per_room)

            if room.contains(self.player.location):
                continue  # Skip room if player is inside
            
            else:
                n_mobs_spawned_in_this_room = 0
                while n_mobs_spawned_in_this_room < max_mobs_in_this_room:
                    current_mob_locations = [mob.location for mob in self.live_ai_actors]
                    spawn_location = room.random_location()
                    if not any(mob_location == spawn_location for mob_location in current_mob_locations):
                        if random.random() < 0.8:
                            spawn(ORC, spawn_location)
                        else:
                            spawn(TROLL, spawn_location)
                                
                        n_total_mobs_spawned_in_this_map += 1
                        n_mobs_spawned_in_this_room += 1

        # Generate remainder of mobs in corridors
        while n_total_mobs_spawned_in_this_map < max_total_mobs_in_this_map:
            current_mob_locations = [mob.location for mob in self.live_ai_actors]

            for corridor in game_map.corridors:
                walkable = np.argwhere(corridor)
                spawn_location = random.choice(walkable)
                spawn_location = MapCoords(int(spawn_location[0]), int(spawn_location[1]))

                if not any(room.contains(spawn_location) for room in game_map.rooms):
                    if not any(mob_location == spawn_location for mob_location in current_mob_locations):
                        if random.random() < 0.8:
                            spawn(ORC, spawn_location)
                        else:
                            spawn(TROLL, spawn_location)

                n_total_mobs_spawned_in_this_map += 1