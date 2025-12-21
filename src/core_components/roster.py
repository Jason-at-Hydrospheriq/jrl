#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set, List, Callable, TYPE_CHECKING, TypeVar
import random
import numpy as np
from copy import deepcopy

from core_components.entities.library import *
from core_components.entities import attributes
from core_components.maps.tilemaps import DEFAULT_MANIFEST, DefaultTileMap
from core_components.maps.tiles import TileTuple

if TYPE_CHECKING:
    from state import GameState

M = TypeVar('M', bound='BaseEntity')

class Roster:
    PARENT_MAP_SIZE = DEFAULT_MANIFEST['dimensions']['grid_size']
    PLAYER = PlayerCharactor(   name="Player", 
                            symbol=chr(64), 
                            color=(130, 200, 255),
                            location=TileCoordinate(TileTuple(([0], [0])), 
                                                    parent_map_size=PARENT_MAP_SIZE),
                            physical=attributes.PhysicalStats(max_hp=30, constitution=14),
                            combat=attributes.CombatStats(defense=2, attack_power=5))

    ORC = MobCharactor( name="Orc", 
                        symbol=chr(65), 
                        color=(63, 127, 63),
                        location=TileCoordinate(TileTuple(([0], [0])), 
                                                parent_map_size=PARENT_MAP_SIZE),
                        physical=attributes.PhysicalStats(max_hp=10, constitution=12),
                        combat=attributes.CombatStats(defense=0, attack_power=3))

    TROLL = MobCharactor(   name="Troll", 
                            symbol=chr(65), 
                            color=(0, 127, 0), 
                            location=TileCoordinate(TileTuple(([0], [0])), 
                                                    parent_map_size=PARENT_MAP_SIZE),
                            physical=attributes.PhysicalStats(max_hp=16, constitution=12),
                            combat=attributes.CombatStats(defense=1, attack_power=4))

    """ The Roster component manages the state of all entities in the game. """

    __slots__ = ("state", "entities", "spawn")
    
    state: GameState
    entities: Set[BaseEntity]
    spawn: Callable

    def __init__(self, state: GameState | None = None) -> None:
        if state is not None:
            self.state = state
    
        self.entities = set()    

    @property
    def entity_locations(self) -> List[TileCoordinate]:
        return [entity.location for entity in self.entities if hasattr(entity, 'location')]

    @property
    def player(self) -> Charactor | None:
        for entity in self.entities:
            if isinstance(entity, PlayerCharactor):
                return entity
      
    @player.setter
    def player(self, new_player: Charactor) -> None:
        if self.player is not None:
            self.entities.remove(self.player)
    
        self.entities.add(new_player)

    @property
    def all_actors(self) -> List[BaseEntity]:
        potential_actors = [entity for entity in self.entities if hasattr(entity, 'is_alive')]
        return [entity for entity in potential_actors] #type: ignore
    
    @property
    def all_non_actors(self) -> List[BaseEntity]:
        potential_non_actors = [entity for entity in self.entities if not hasattr(entity, 'is_alive')]
        return [entity for entity in potential_non_actors] #type: ignore

    @property
    def entity_blocked_locations(self) -> List[TileCoordinate]:
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
    
    def get_entity_at_location(self, location: TileCoordinate) -> List[BaseEntity]:
        found_entity = []
        for entity in self.entities:
            if entity.location == location:
                found_entity += [entity]
        
        return found_entity
    
    def spawn_player(self, game_map: DefaultTileMap) -> None:
        """Spawn the player in a random room."""
        
        start_rooms = [area for area in game_map.areas.keys() if not area.startswith('_')]
        start_room = random.choice(start_rooms)
        spawn_location = game_map.areas[start_room].get_random_location()
        self.player = self.spawn_at_location(entity=self.PLAYER, location=spawn_location)  # type: ignore

    def spawn_at_location(self, *, entity: M, location: TileCoordinate) -> M:
        """Spawn a copy of this entity at the given location and return it."""
        clone = deepcopy(entity)
        clone.location = location
        self.entities.add(clone)
        return clone
    
    def initialize_random_mobs(self, game_map: DefaultTileMap, max_mobs_per_area: int) -> None:
        """Generate mobs """
        n_total_mobs_spawned_in_this_map = 0
        max_total_mobs_in_this_map = len(game_map.areas) * max_mobs_per_area
        
        rooms = [area for name, area in game_map.areas.items() if not name.startswith('_corridor')]
        corridors = [area for name, area in game_map.areas.items() if name.startswith('_corridor')]

        # Generate mobs in rooms
        for room in rooms:
            max_mobs_in_this_room = random.randint(1, max_mobs_per_area)

            if room.contains(self.player.location) if self.player is not None else False:
                continue  # Skip room if player is inside
            
            else:
                n_mobs_spawned_in_this_room = 0
                attempts = 100  # Prevent infinite loops

                while n_mobs_spawned_in_this_room < max_mobs_in_this_room and attempts > 0:
                    current_mob_locations = [mob.location for mob in self.live_ai_actors]

                    spawn_location = room.get_random_location()
                    attempts -= 1
                    
                    if not any(mob_location == spawn_location for mob_location in current_mob_locations):
                        if random.random() < 0.8:
                            self.spawn_at_location(entity=self.ORC, location=spawn_location)
                        else:
                            self.spawn_at_location(entity=self.TROLL, location=spawn_location)
                                
                        n_total_mobs_spawned_in_this_map += 1
                        n_mobs_spawned_in_this_room += 1

        # Generate remainder of mobs in corridors
        corridors = [area for name, area in game_map.areas.items() if name.startswith('_corridor')]

        while n_total_mobs_spawned_in_this_map < max_total_mobs_in_this_map:
            current_mob_locations = [mob.location for mob in self.live_ai_actors]

            for corridor in corridors:
                
                open_terrain_layout = game_map.blocks_movement == False
                open_terrain_in_corridor = open_terrain_layout & corridor.to_mask
                open_terrain_coords = np.argwhere(open_terrain_in_corridor)
                spawn_choice = random.choice(open_terrain_coords)
                location_tuple = TileTuple(([int(spawn_choice[0])], [int(spawn_choice[1])]))
                spawn_location = TileCoordinate(location_tuple, corridor.parent_map_size)

                if not any(room.contains(spawn_location) for room in game_map.areas.values()):
                    if not any(mob_location == spawn_location for mob_location in current_mob_locations):
                        if random.random() < 0.8:
                            self.spawn_at_location(entity=self.ORC, location=spawn_location)
                        else:
                            self.spawn_at_location(entity=self.TROLL, location=spawn_location)

                n_total_mobs_spawned_in_this_map += 1