#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
import numpy as np
from typing import Generator
import random

from atlas.components.tiles import *
from game_types import BaseMapGenerator, GraphicTileMap
from atlas.components.tilemaps import DefaultTileMap
from game_types import TileCoordinate, TileTuple

RECTANGULAR_ROOM_TEMPLATE = RectangularRoom()
CIRCULAR_ROOM_TEMPLATE = CircularRoom()
CORRIDOR_TEMPLATE = GenericCorridor()
DEFAULT_MAP_TEMPLATE = DefaultTileMap()

class DungeonGenerator(BaseMapGenerator):
    """Generates dungeons using various algorithms."""
    width: int
    height: int
    rectangular_room_template: RectangularRoom
    circular_room_template: CircularRoom
    corridor_template: GenericCorridor

    def __init__(self, template: GraphicTileMap=DEFAULT_MAP_TEMPLATE) -> None:
            
        self.map_template = template
        self.width = template.grid.width
        self.height = template.grid.height
        self.rectangular_room_template = RectangularRoom(center=template.center, width=template.grid.width, height=template.grid.height)
        self.circular_room_template = CircularRoom(center=template.center, radius=min(template.grid.width, template.grid.height) // 2)
        self.corridor_template = GenericCorridor(center=template.center, width=template.grid.width, height=template.grid.height)

    def generate(self, 
                 max_rooms: int=10, 
                 min_room_size: int=5, 
                 max_room_size: int=20) -> GraphicTileMap:
        #TODO Use LLM to generate more complex dungeons
        dungeon = self.spawn_map()
        
        self.add_rooms(dungeon=dungeon, max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size)
        self.add_corridors(dungeon=dungeon)
        for area in dungeon.areas.values():
            dungeon.set_tiles(area.to_mask, "floor")
        dungeon.update_state()

        return dungeon
    
    def spawn_map(self) -> GraphicTileMap:
        """Spawn a new map instance based on the generator's template."""
        dungeon = deepcopy(self.map_template)
        self.width = dungeon.grid.width
        self.height = dungeon.grid.height
        dungeon.set_tiles(graphic_name='wall') # Initialize all tiles as walls
        dungeon.update_state()
        
        return dungeon

    def add_rooms(self, dungeon: GraphicTileMap, max_rooms: int, min_room_size: int, max_room_size: int) -> None:
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

    def add_corridors(self, dungeon: GraphicTileMap) -> None:
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
            
    def room_generator(self, dungeon: GraphicTileMap, max_rooms: int, min_room_size: int, max_room_size: int) -> Generator[TileArea | None]:

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
    

class GravPulseShipHangerDeck(BaseMapGenerator):

    def __init__(self, template: GraphicTileMap=DEFAULT_MAP_TEMPLATE) -> None:
        
        self.map_template = template

    def generate(self) -> GraphicTileMap:
        map = self.spawn_map()
        
        a = GravPulseShipDeck(radius=10, corridor_width=0)
        map.areas['main_corridor'] = a
        b = GravPulseShipDeck(radius=25, corridor_width=8)
        map.areas['main_hanger'] = b
        c = GravPulseShipBulkhead(angle = 55, thickness=4)
        d = GravPulseShipBulkhead(angle = -55, thickness=4)
        e = GravPulseShipBulkhead(angle = 0, thickness=2)
        bulkheads = c.to_mask & d.to_mask & e.to_mask
        floor_layout = (a.to_mask | bulkheads) & (a.to_mask | b.to_mask)
        map.set_tiles(floor_layout.astype(bool), "floor")

        door_layout = map.get_tile_layout('solid_door')
        if door_layout is not None:
            door_layout[13:16, 24:27] = True  # add a door 
            door_layout[35:38, 24:27] = True  # add another door
            map.set_tiles(door_layout.astype(bool), "solid_door")
            blocked_layout = ~floor_layout.astype(bool) | door_layout.astype(bool)
            map.set_state_bits('blocks_movement', blocked_layout)
            map.set_state_bits('blocks_vision', blocked_layout)
        
        map.update_state()
        return map
    
    def spawn_map(self) -> GraphicTileMap:
        """Spawn a new map instance based on the generator's template."""
        map = deepcopy(self.map_template)
        self.width = map.grid.width
        self.height = map.grid.height
        map.set_tiles(graphic_name='wall') # Initialize all tiles as walls
        map.update_state()
        
        return map