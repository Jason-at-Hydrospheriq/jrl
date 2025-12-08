#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
import numpy as np
from typing import Iterator, Sequence, Set, List
import random

from core_components.maps.room_library import *
from core_components.maps.base import BaseMapGenerator, BaseTileMap, MapCoords, map_dtype, new_tile_type, graphic_dtype, tile_dtype

# GRAPHIC CONSTANTS
SHROUD = (ord(" "), (255, 255, 255), (0, 0, 0))  # Unknown tile

# TILE TYPES
FLOOR = new_tile_type(name="floor",
                      shroud=SHROUD,
                      dark=(ord(" "), (255, 255, 255), (50, 50, 150)), 
                      light=(ord(" "), (255, 255, 255), (200, 180, 50)))
WALL = new_tile_type(name="wall",
                     shroud=SHROUD,
                     dark=(ord(" "), (255, 255, 255), (0, 0, 100)), 
                     light=(ord(" "), (255, 255, 255), (130, 110, 50)))

# ROOM TEMPLATES
RECTANGULAR_ROOM = RectangularRoom(0, 0, 10, 10)
CIRCULAR_ROOM = CircularRoom(0, 0, 5)


class DungeonGenerator(BaseMapGenerator):
    """Generates dungeons using various algorithms."""
    rooms: List[BaseRoom]
    corridors: List[np.ndarray]

    def __init__(self) -> None:
        self.rooms = []
        self.corridors = []

    def generate(self, map_width: int, map_height: int, max_rooms: int=10, min_room_size: int=5, max_room_size: int=20) -> BaseTileMap:
        #TODO Use LLM to generate more complex dungeons

        dungeon = BaseTileMap(height=map_height, width=map_width)

        # Create rooms
        for new_room in self.random_rooms(dungeon, max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size):
            if all(not new_room.intersects(existing_room) for existing_room in self.rooms):
                dungeon.add_area(new_room.inner_area, FLOOR)
                self.rooms.append(new_room)

        # Connect rooms with corridors
        for idx, room in enumerate(self.rooms):
            prev_room_location = list(self.rooms)[idx - 1].random_location()
            curr_room_location = room.random_location()
            corridor = self.spawn_corridor(prev_room_location, curr_room_location)
            self.corridors.append(corridor)
            dungeon.add_area(corridor, FLOOR)

        return dungeon

    def spawn_room(self, room: BaseRoom, x: int, y: int, width: int = -1, height: int = -1, radius: int = -1) -> BaseRoom:
        clone = deepcopy(room)

        if clone == RECTANGULAR_ROOM and radius == -1:
            clone.width = width #type: ignore
            clone.height = height #type: ignore
        
        elif clone == CIRCULAR_ROOM and width == -1 and height == -1:
            clone.radius = radius #type: ignore

        clone.center = MapCoords(x, y)

        return clone
       
    def spawn_corridor(self, start: MapCoords, end: MapCoords) -> np.ndarray:
        """Carve out a corridor between two points in the tile map."""

        x1, y1 = start.x, start.y
        x2, y2 = end.x, end.y
        width = random.randint(0, 2)
        mask = np.full((self.tile_map.width, self.tile_map.height), fill_value=False, order="F", dtype=int)

        if random.random() < 0.5:
            # Horizontal first, then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                mask[x, y1] = True
                mask[x, max(0, y1 - width):min(self.tile_map.height, y1 + width)] = True
            for y in range(min(y1, y2), max(y1, y2) + 1):
                mask[x2, y] = True
                mask[max(0, x2 - width):min(self.tile_map.width, x2 + width), y] = True
        else:
            # Vertical first, then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                mask[x1, y] = True
                mask[max(0, x1 - width):min(self.tile_map.width, x1 + width), y] = True
            for x in range(min(x1, x2), max(x1, x2) + 1):
                mask[x, y2] = True
                mask[x, max(0, y2 - width):min(self.tile_map.height, y2 + width)] = True

        return mask

    def random_rooms(self, map: BaseTileMap, max_rooms: int, min_room_size: int, max_room_size: int) -> Iterator[BaseRoom]:

        for _ in range(max_rooms):
            room_type = random.choice(['rectangular', 'circular'])

            if room_type == 'rectangular':
                yield self.spawn_room(RECTANGULAR_ROOM,
                                    x=random.randint(0, map.width - 1),
                                    y=random.randint(0, map.height - 1),
                                    width=random.randint(min_room_size, max_room_size),
                                    height=random.randint(min_room_size, max_room_size))
            elif room_type == 'circular':
                yield self.spawn_room(CIRCULAR_ROOM,
                                    x=random.randint(0, map.width - 1),
                                    y=random.randint(0, map.height - 1),
                                    radius=random.randint(min_room_size // 2, max_room_size // 2))
             
    def clear(self) -> None:
        self.rooms.clear()
        self.corridors.clear()

