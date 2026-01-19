#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set, List, Callable, TYPE_CHECKING, TypeVar
import random
import numpy as np
from copy import deepcopy

from manifests import DEFAULT_TILEMAP_MANIFEST
from entities import AICharacter, Character
from atlas.components.tilemaps import DefaultTileMap
from baseclasses import BaseGameEntity, BaseItem
from game_types import TileCoordinate
from game_types import TileTuple
from entities import MobCharacter, PlayerCharacter, HealingConsumable

if TYPE_CHECKING:
    from store import GameStore
    from loop.loop import GameLoops

M = TypeVar('M', bound=BaseGameEntity)

class Portfolio:
    store: GameStore
    entities: Set[BaseGameEntity]
    spawn: Callable
    game_ai: GameLoops | None = None

    PARENT_MAP_SIZE = DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size']
    PLAYER = PlayerCharacter(   name="Player", 
                                symbol=chr(64), 
                                color=(130, 200, 255),
                                location=TileCoordinate.from_tuple((0,0), 
                                                    parent_map_size=PARENT_MAP_SIZE),
                                hp=150,
                                max_hp=150)
    ORC = MobCharacter(     name="Orc", 
                            symbol=chr(65), 
                            color=(63, 127, 63),
                            location=TileCoordinate.from_tuple((0,0), 
                                                    parent_map_size=PARENT_MAP_SIZE),
                            hp=25,
                            max_hp=25,
                            drop_rate=0.6)
    TROLL = MobCharacter(   name="Troll", 
                            symbol=chr(65), 
                            color=(0, 127, 0), 
                            location=TileCoordinate.from_tuple((0,0), 
                                                    parent_map_size=PARENT_MAP_SIZE),
                            hp=35,
                            max_hp=35,
                            drop_rate=0.8)
    HEALING_POTION = HealingConsumable( name="Healing Potion",
                                    symbol='!',
                                    color=(255, 0, 255),
                                    location=TileCoordinate.from_tuple((0,0), 
                                                    parent_map_size=PARENT_MAP_SIZE)
    )
    def __init__(self, store: GameStore | None = None, game_ai: GameLoops | None = None) -> None:

        if store is not None:
            self.store = store
        if game_ai is not None:
            self.game_ai = game_ai
    
        self.entities = set()    

    @property
    def entity_locations(self) -> List[TileCoordinate | None]:
        return [entity.location for entity in self.entities if hasattr(entity, 'location')]

    @property
    def player(self) -> Character | None:
        for entity in self.entities:
            if isinstance(entity, PlayerCharacter):
                return entity
      
    @player.setter
    def player(self, new_player: Character) -> None:
        if self.player is not None:
            self.entities.remove(self.player)
    
        self.entities.add(new_player)

    @property
    def all_actors(self) -> List[Character]:
        return [entity for entity in self.entities if isinstance(entity, Character)]

    @property
    def all_ai_actors(self) -> List[AICharacter]:
        return [entity for entity in self.entities if isinstance(entity, AICharacter)]
    
    @property
    def all_non_actors(self) -> List[BaseGameEntity]:
        return [entity for entity in self.entities if not isinstance(entity, Character)]

    @property
    def entity_blocked_locations(self) -> List[TileCoordinate]:
        potential_blockers = [obj for obj in self.entities if hasattr(obj, 'blocks_movement')]
        return [blocker.location for blocker in potential_blockers if blocker.blocks_movement] #type: ignore
    
    @property
    def live_actors(self) -> List[Character]:
        return [entity for entity in self.all_actors if entity.is_alive]
    
    @property
    def live_ai_actors(self) -> List[AICharacter]:
        return [entity for entity in self.live_actors if isinstance(entity, AICharacter)]
    
    @property
    def live_mobs(self) -> List[MobCharacter]:
        return [entity for entity in self.live_ai_actors if isinstance(entity, MobCharacter)]
    
    @property
    def visible_mobs(self) -> List[MobCharacter]:
        return [entity for entity in self.live_mobs if entity.player_visible]

    @property
    def all_items(self) -> List[BaseGameEntity]:
        return [entity for entity in self.entities if isinstance(entity, BaseItem)]
    
    def get_entity_at_location(self, location: TileCoordinate) -> List[BaseGameEntity]:
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
        self.player.ai = self.game_ai.sequenced_loop_handler

    def spawn_at_location(self, *, entity: M, location: TileCoordinate) -> M:
        """Spawn a copy of this entity at the given location and return it."""
        clone = deepcopy(entity)
        clone.location = location
        clone.store = self.store
        if isinstance(clone, AICharacter) and self.game_ai is not None:
            clone.ai = self.game_ai.sequenced_loop_handler
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

            if self.player and self.player.location is not None:    
                if room.contains(self.player.location):
                    continue  # Skip room if player is inside

                n_mobs_spawned_in_this_room = 0
                attempts = 100  # Prevent infinite loops

                while n_mobs_spawned_in_this_room < max_mobs_in_this_room and attempts > 0:
                    current_mob_locations = [mob.location for mob in self.live_ai_actors]

                    spawn_location = room.get_random_location()
                    attempts -= 1
                    
                    if not any(mob_location == spawn_location for mob_location in current_mob_locations):
                        random_number = random.random()
                        if random_number < 0.8:
                            self.spawn_at_location(entity=self.ORC, location=spawn_location)
                        elif 0.8 <= random_number < 0.9:
                            self.spawn_at_location(entity=self.TROLL, location=spawn_location)
                        elif random_number >= 0.9:
                            self.spawn_at_location(entity=self.HEALING_POTION, location=spawn_location)
                            
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

        self.spawn_at_location(entity=self.HEALING_POTION, location=self.player.location)  # type: ignore
    
    def update(self) -> None:
        """Update all entities in the portfolio."""
        for actor in self.live_ai_actors:
            actor.update()