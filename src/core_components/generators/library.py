#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
import numpy as np
from typing import Generator, Tuple
import random

from core_components.tiles.library import *
from core_components.generators.base import BaseMapGenerator
from core_components.maps.library import GraphicTileMap, DefaultTileMap, DEFAULT_MANIFEST

RECTANGULAR_ROOM_TEMPLATE = RectangularRoom()
CIRCULAR_ROOM_TEMPLATE = CircularRoom()
CORRIDOR_TEMPLATE = GenericCorridor()
DEFAULT_MAP_TEMPLATE = DefaultTileMap()

class DungeonGenerator(BaseMapGenerator):
    """Generates dungeons using various algorithms."""
    width: int
    height: int
    map_template: DefaultTileMap
    rectangular_room_template: RectangularRoom
    circular_room_template: CircularRoom
    corridor_template: GenericCorridor

    def __init__(self, template: DefaultTileMap=DEFAULT_MAP_TEMPLATE) -> None:
            
        self.map_template = template
        self.width = template.grid.width
        self.height = template.grid.height
        self.rectangular_room_template = RectangularRoom(center=template.center, width=template.grid.width, height=template.grid.height)
        self.circular_room_template = CircularRoom(center=template.center, radius=min(template.grid.width, template.grid.height) // 2)
        self.corridor_template = GenericCorridor(center=template.center, width=template.grid.width, height=template.grid.height)

    def generate(self, 
                 max_rooms: int=10, 
                 min_room_size: int=5, 
                 max_room_size: int=20) -> DefaultTileMap:
        #TODO Use LLM to generate more complex dungeons
        dungeon = self.spawn_map()
        
        self.add_rooms(dungeon=dungeon, max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size)
        self.add_corridors(dungeon=dungeon)
        for area in dungeon.areas.values():
            dungeon.set_tiles(area.to_mask, "floor")
        dungeon.update_state()

        return dungeon
    
    def spawn_map(self) -> DefaultTileMap:
        """Spawn a new map instance based on the generator's template."""
        dungeon = deepcopy(self.map_template)
        self.width = dungeon.grid.width
        self.height = dungeon.grid.height
        dungeon.set_tiles(graphic_name='wall') # Initialize all tiles as walls
        dungeon.update_state()
        
        return dungeon

    def add_rooms(self, dungeon: DefaultTileMap, max_rooms: int, min_room_size: int, max_room_size: int) -> None:
        """Add rooms to the tile map."""
        rooms = self.room_generator(dungeon=dungeon, max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size)
        map_rooms = []
        for idx, new_room in enumerate(rooms):
            if new_room is not None:
                no_overlap = all(not new_room.intersects(existing_room) for existing_room in map_rooms)
                inbounds = new_room.is_inbounds
                
                if no_overlap and inbounds and new_room.to_mask.any():
                    map_rooms.append(new_room)
                    dungeon.areas[str(idx)] = new_room

    def add_corridors(self, dungeon: DefaultTileMap) -> None:
        """Carve out a corridor between two points in the tile map."""
        area_idx = list(dungeon.areas.keys())
        for idx, area_name in enumerate(area_idx):

            prev_area_name = area_idx[idx-1]
            prev_area = dungeon.areas[prev_area_name]
            prev_area_location = prev_area.center
            if idx == 0:
                prev_area_location = prev_area.center
                continue
            current_area = dungeon.areas[area_name]
            current_area_location = current_area.center

            corridor = deepcopy(CORRIDOR_TEMPLATE)
            corridor.center = dungeon.center
            corridor.width = dungeon.grid.width
            corridor.height = dungeon.grid.height
            corridor.start = prev_area_location
            corridor.end = current_area_location

            dungeon.areas[str(f'_corridor_{idx}')] = corridor
            
    def room_generator(self, dungeon: DefaultTileMap, max_rooms: int, min_room_size: int, max_room_size: int) -> Generator[GenericMapArea | None]:

        for _ in range(max_rooms):
            room_type = random.choice(['rectangular', 'circular'])
            parent_map_size = dungeon.center.parent_map_size

            x_loc = random.randint(0, dungeon.grid.width - 1)
            y_loc = random.randint(0, dungeon.grid.height - 1)
            location = TileTuple( ([x_loc], [y_loc]) )
            center = TileCoordinate(location, parent_map_size=parent_map_size)

            x_size = random.randint(min_room_size, max_room_size)
            y_size = random.randint(min_room_size, max_room_size)
            
            if room_type == 'rectangular':
                size = TileTuple((  [x_size], [y_size]))
                yield self.add(self.rectangular_room_template, center=center, size=size)
                
            elif room_type == 'circular':
                size = TileTuple((  [x_size], [x_size]))
                yield self.add(self.circular_room_template, center=center, size=size)
                
    def _add_rectangularroom(self,
                                room: RectangularRoom,
                                center: TileCoordinate, 
                                size: TileTuple) -> GenericMapArea:
        
        """Spawn a room of the specified type at the given center with the given size."""
        clone = deepcopy(room)
        clone.center = center
        clone.width = size[0][0]
        clone.height = size[1][0]

        return clone
    
    def _add_circularroom(self, 
                   room: CircularRoom,
                   center: TileCoordinate, 
                   size: TileTuple) -> GenericMapArea: 
        clone = deepcopy(room)
        clone.center = center
        clone.radius = size[0][0] // 2

        return clone
    
