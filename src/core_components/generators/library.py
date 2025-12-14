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
    
class DefaultDungeonGenerator(BaseMapGenerator):
    """Generates dungeons using various algorithms."""
    
    def __init__(self) -> None:
        self.rooms = []
        self.corridors = []

        self.map = DefaultTileMap()

    def generate(self, 
                 max_rooms: int=10, 
                 min_room_size: int=5, 
                 max_room_size: int=20) -> GraphicTileMap:
        #TODO Use LLM to generate more complex dungeons
        self.clear()
        self.map.set_tiles(graphic_name='wall')
        self.map.update_state()
        
        self.add_rooms(max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size)
        self.add_corridors()
        
        return deepcopy(self.map)
    
    def add_rooms(self, max_rooms: int, min_room_size: int, max_room_size: int):
        """Add rooms to the tile map."""
        rooms = self.room_generator(max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size)
        for idx, new_room in enumerate(rooms):
            if new_room is not None:
                no_overlap = all(not new_room.intersects(existing_room) for existing_room in self.rooms)
                inbounds = new_room.is_inbounds
                
                if no_overlap and inbounds and new_room.to_mask.any():
                    self.map.areas[str(idx)] = new_room

    def add_corridors(self) -> None:
        """Carve out a corridor between two points in the tile map."""
        area_idx = list(self.map.areas.keys())

        for idx, area_name in enumerate(area_idx):

            prev_area_name = area_idx[idx-1]
            prev_area = self.map.areas[prev_area_name]
            prev_area_location = prev_area.center
            if idx == 0:
                prev_area_location = prev_area.center
                continue
            current_area = self.map.areas[area_name]
            current_area_location = current_area.center

            corridor = deepcopy(CORRIDOR_TEMPLATE)
            corridor.center = self.map.center
            corridor.width = self.map.grid.width
            corridor.height = self.map.grid.height
            corridor.start = prev_area_location
            corridor.end = current_area_location

            self.map.areas[str(f'corridor_{idx}')] = corridor
            
    def room_generator(self, max_rooms: int, min_room_size: int, max_room_size: int) -> Generator[GenericMapArea | None]:

        for _ in range(max_rooms):
            room_type = random.choice(['rectangular', 'circular'])

            x_loc = random.randint(0, self.map.grid.width - 1)
            y_loc = random.randint(0, self.map.grid.height - 1)
            location = TileTuple( ([x_loc], [y_loc]) )
            center = TileCoordinate(location, parent_map_size=self.map.grid.size)

            x_size = random.randint(min_room_size, max_room_size)
            y_size = random.randint(min_room_size, max_room_size)
            
            if room_type == 'rectangular':
                size = TileTuple((  [x_size], [y_size]))
                yield self.add(RECTANGULAR_ROOM_TEMPLATE, center=center, size=size)
                
            elif room_type == 'circular':
                size = TileTuple((  [x_size], [x_size]))
                yield self.add(CIRCULAR_ROOM_TEMPLATE, center=center, size=size)

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
    
    def clear(self) -> None:
        self.map.reset_tiles()
        self.map.reset_state()
        self.map.areas.clear()
        self.map.paths.clear()

