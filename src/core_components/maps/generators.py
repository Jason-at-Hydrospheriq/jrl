#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
import numpy as np
from typing import Iterator, List
import random

from core_components.maps.rooms import *
from core_components.maps.base import BaseMapGenerator, BaseTileMap
from core_components.maps.tilemaps import GenericTileMap


class GenericDungeonGenerator(BaseMapGenerator):
    """Generates dungeons using various algorithms."""
    rooms: List[BaseRoom]
    corridors: List[np.ndarray]
    
    def __init__(self, size: tuple[int, int] | None = None) -> None:
        self.rooms = []
        self.corridors = []
        self.room_templates = {"rectangular": RectangularRoom(), "circular": CircularRoom()}
        if size is None:
            self.tilemap = GenericTileMap()
        else:
            self.tilemap = GenericTileMap(size=size)

    def generate(self, max_rooms: int=10, min_room_size: int=5, max_room_size: int=20) -> BaseTileMap:
        #TODO Use LLM to generate more complex dungeons
        self.clear()
        self.tilemap.tiles[:] = self.tilemap.resources['tile_types']["wall"]

        # Create rooms
        for new_room in self.random_rooms(max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size):
            if all(not new_room.intersects(existing_room) for existing_room in self.rooms):
                self.tilemap.add_area(new_room.inner_area, "floor")
                self.rooms.append(new_room)

        # Connect rooms with corridors
        for idx, room in enumerate(self.rooms):
            prev_room_location = list(self.rooms)[idx - 1].random_location()
            curr_room_location = room.random_location()
            corridor = self.spawn_corridor(prev_room_location, curr_room_location)
            self.corridors.append(corridor)
            self.tilemap.add_area(corridor, "floor")
        
        return deepcopy(self.tilemap)

    def spawn_room(self, room_name: str, center: MapCoords, size: Tuple[int, int] = (-1, -1), radius: int = -1) -> BaseRoom:
        clone = deepcopy(self.room_templates[room_name])

        if clone == self.room_templates["rectangular"] and radius == -1:
            clone.width = size[0] #type: ignore
            clone.height = size[1] #type: ignore
        
        elif clone == self.room_templates["circular"] and size == (-1, -1):
            clone.radius = radius #type: ignore

        clone.center = center

        return clone
       
    def spawn_corridor(self, start: MapCoords, end: MapCoords) -> np.ndarray:
        """Carve out a corridor between two points in the tile map."""

        x1, y1 = start.x, start.y
        x2, y2 = end.x, end.y
        width = random.randint(0, 2)
        mask = np.full((self.tilemap.width, self.tilemap.height), fill_value=False, order="F", dtype=int)

        if random.random() < 0.5:
            # Horizontal first, then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                mask[x, y1] = True
                mask[x, max(0, y1 - width):min(self.tilemap.height, y1 + width)] = True
            for y in range(min(y1, y2), max(y1, y2) + 1):
                mask[x2, y] = True
                mask[max(0, x2 - width):min(self.tilemap.width, x2 + width), y] = True
        else:
            # Vertical first, then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                mask[x1, y] = True
                mask[max(0, x1 - width):min(self.tilemap.width, x1 + width), y] = True
            for x in range(min(x1, x2), max(x1, x2) + 1):
                mask[x, y2] = True
                mask[x, max(0, y2 - width):min(self.tilemap.height, y2 + width)] = True

        return mask

    def random_rooms(self, max_rooms: int, min_room_size: int, max_room_size: int) -> Iterator[BaseRoom]:

        for _ in range(max_rooms):
            room_type = random.choice(['rectangular', 'circular'])

            if room_type == 'rectangular':
                yield self.spawn_room('rectangular',
                                    center=MapCoords(random.randint(0, self.tilemap.width - 1),
                                                     random.randint(0, self.tilemap.height - 1)),
                                    size=(random.randint(min_room_size, max_room_size),
                                          random.randint(min_room_size, max_room_size)))
            elif room_type == 'circular':
                yield self.spawn_room('circular',
                                    center=MapCoords(random.randint(0, self.tilemap.width - 1),
                                                     random.randint(0, self.tilemap.height - 1)),
                                    radius=random.randint(min_room_size // 2, max_room_size // 2))
             
    def clear(self) -> None:
        self.rooms.clear()
        self.corridors.clear()
        self.tilemap.initialize_map()

