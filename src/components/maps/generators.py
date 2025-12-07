#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from copy import deepcopy
import numpy as np
from typing import Iterator, Sequence, Set, List
import random

from components.maps.room_library import *
from components.maps.dtype_library import map_dtype, new_tile_type
from components.maps.base import BaseTileMap, MapCoords

FLOOR = new_tile_type(name="floor",
                      dark=(ord(" "), (255, 255, 255), (50, 50, 150)), 
                      light=(ord(" "), (255, 255, 255), (200, 180, 50)))
WALL = new_tile_type(name="wall",
                     dark=(ord(" "), (255, 255, 255), (0, 0, 100)), 
                     light=(ord(" "), (255, 255, 255), (130, 110, 50)))

RECTANGULAR_ROOM = RectangularRoom(0, 0, 10, 10)
CIRCULAR_ROOM = CircularRoom(0, 0, 5)

class DungeonGenerator:
    """Generates dungeons using various algorithms."""
    rooms: List[BaseRoom]
    corridors: List[np.ndarray]
    tile_map: BaseTileMap

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
    
    def clear(self) -> None:
        self.rooms.clear()
        self.corridors.clear()

# def random_mobs(rooms: List[Room], max_total_mobs: int, max_mobs_per_room: int, game_map: GameMap) -> None:
#     """Generate mobs """
#     n_total_mobs_spawned_in_this_map = 0
#     min_total_mobs_in_this_map = len(rooms) * max_mobs_per_room
#     max_total_mobs_in_this_map = random.randint(min_total_mobs_in_this_map, max_total_mobs)
    
#     # Generate mobs in rooms
#     for room in rooms:
#         max_mobs_in_this_room = random.randint(1, max_mobs_per_room)

#         if room.contains(game_map.player.location):
#             continue  # Skip room if player is inside
        
#         else:
#             n_mobs_spawned_in_this_room = 0
#             while n_mobs_spawned_in_this_room < max_mobs_in_this_room:
#                 current_mob_locations = [mob.location for mob in game_map.live_ai_actors]
#                 spawn_location = room.random_location()
#                 if not any(mob_location == spawn_location for mob_location in current_mob_locations):
#                     if random.random() < 0.8:
#                         mob_factory.ORC.spawn(game_map, spawn_location)
#                     else:
#                         mob_factory.TROLL.spawn(game_map, spawn_location)
                            
#                     n_total_mobs_spawned_in_this_map += 1
#                     n_mobs_spawned_in_this_room += 1

#     # Generate remainder of mobs in corridors
#     while n_total_mobs_spawned_in_this_map < max_total_mobs_in_this_map:
#         x, y = random.randint(0, game_map.width - 1), random.randint(0, game_map.height - 1)
#         spawn_location = MapCoords(int(x), int(y))
#         current_mob_locations = [mob.location for mob in game_map.live_ai_actors]

#         for room in rooms:
#             if room.contains(spawn_location):
#                 continue  # Skip if inside a room

#             else: 
#                 if game_map.tiles[spawn_location.x, spawn_location.y]["walkable"] and not any(mob_location == spawn_location for mob_location in current_mob_locations):
#                     if random.random() < 0.8:
#                         mob_factory.ORC.spawn(game_map, spawn_location)
#                     else:
#                         mob_factory.TROLL.spawn(game_map, spawn_location)
#                 n_total_mobs_spawned_in_this_map += 1