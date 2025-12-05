# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# from __future__ import annotations
# import random
# from typing import Iterator, List, Tuple
# import numpy as np

# from game_map import GameMap, MapCoords
# from entities import Charactor
# from engine import Engine
# import tile_types
# import mob_factory


# class Room:
#     def __init__(self, x: int, y: int, game_map: GameMap):
#         self.center = MapCoords(x, y)
#         self.game_map = game_map

#     @property
#     def _inner_area(self) -> np.ndarray:
#         raise NotImplementedError()
    
#     def contains(self, location: MapCoords) -> np.bool_:
#         return self._inner_area[location.x, location.y]
    
#     def intersects(self, other_room: Room) -> np.bool_:
#         """Return True if this room intersects with another room."""
#         own_area = self._inner_area
#         intersection = own_area * other_room._inner_area
#         return intersection.any()

#     def add_to_map(self, game_map: GameMap) -> None:
#         """Carve out this room in the given game map."""
#         game_map.tiles[self._inner_area] = tile_types.floor      
    
#     def random_location(self) -> MapCoords:
#         """Return a random location within this room."""
#         area_indices = np.argwhere(self._inner_area)
#         choice = random.choice(area_indices)
#         return MapCoords(int(choice[0]), int(choice[1]))


# class RectangularRoom(Room):
#     def __init__(self, x: int, y: int, width: int, height: int, game_map: GameMap):
#         super().__init__(x, y, game_map)
#         self.upper_left_corner = MapCoords(x - width // 2, y - height // 2)
#         self.lower_right_corner = MapCoords(x + width // 2, y + height // 2)

#     @property
#     def _inner_area(self) -> np.ndarray:
#         """Return the inner area of this room as a 2D array index."""
#         mask = np.fromfunction(lambda xx, yy: (self.upper_left_corner.x <= xx) & (xx < self.lower_right_corner.x) & (self.upper_left_corner.y <= yy) & (yy < self.lower_right_corner.y),
#                                (self.game_map.width, self.game_map.height), dtype=int)
#         return mask


# class CircularRoom(Room):
#     def __init__(self, x: int, y: int, radius: int, game_map: GameMap):
#         super().__init__(x, y, game_map)
#         self.radius = radius

#     @property
#     def _inner_area(self) -> np.ndarray:
#         """Return the inner area of this room as a 2D array index."""
#         mask = np.fromfunction(lambda xx, yy: (xx - self.center.x) ** 2 + (yy - self.center.y) ** 2 <= self.radius ** 2 + 2,
#                                (self.game_map.width, self.game_map.height), dtype=int)
#         return mask
 

# def random_dungeon(engine: Engine, map_width: int, map_height: int, player: Charactor, max_rooms: int=10, min_room_size: int=5, max_room_size: int=20, max_total_mobs: int=50, max_mobs_per_room: int=5) -> GameMap:
#     #TODO Use LLM to generate more complex dungeons

#     dungeon = GameMap(engine=engine, width=map_width, height=map_height, player=player)
#     rooms: List[Room] = []

#     # Create rooms
#     for new_room in random_rooms(dungeon, max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size):
#         if all(not new_room.intersects(existing_room) for existing_room in rooms):
#             new_room.add_to_map(dungeon)

#             if len(rooms) == 0:
#                 player.location = new_room.center  # Place player in first room

#             rooms.append(new_room)

#     # Connect rooms with corridors
#     for i in range(1, len(rooms)):
#         prev_room_location = rooms[i - 1].random_location()
#         curr_room_location = rooms[i].random_location()
#         sequential_corridors(prev_room_location, curr_room_location, dungeon)

#     # Populate dungeion with mobs
#     random_mobs(rooms, max_total_mobs, max_mobs_per_room, dungeon)

#     return dungeon

# def random_rooms(game_map: GameMap, max_rooms: int, min_room_size: int, max_room_size: int) -> Iterator[Room]:

#     for _ in range(max_rooms):
#         room_type = random.choice(['rectangular', 'circular'])

#         if room_type == 'rectangular':
#             width = random.randint(min_room_size, max_room_size)
#             height = random.randint(min_room_size, max_room_size)
#             x = random.randint(0, game_map.width - width - 1)
#             y = random.randint(0, game_map.height - height - 1)
#             yield RectangularRoom(x, y, width, height, game_map=game_map)

#         else:  # circular
#             radius = random.randint(min_room_size // 2, max_room_size // 2)
#             x = random.randint(radius, game_map.width - radius - 1)
#             y = random.randint(radius, game_map.height - radius - 1)
#             yield CircularRoom(x, y, radius, game_map=game_map)

# def sequential_corridors(start: MapCoords, end: MapCoords, game_map: GameMap) -> None:
#     """Carve out a corridor between two points in the game map."""
#     x1, y1 = start.x, start.y
#     x2, y2 = end.x, end.y
#     width = random.randint(0, 2)

#     if random.random() < 0.5:
#         # Horizontal first, then vertical
#         for x in range(min(x1, x2), max(x1, x2) + 1):
#             game_map.tiles[x, y1] = tile_types.floor
#             game_map.tiles[x, max(0, y1 - width):min(game_map.height, y1 + width)] = tile_types.floor
#         for y in range(min(y1, y2), max(y1, y2) + 1):
#             game_map.tiles[x2, y] = tile_types.floor
#             game_map.tiles[max(0, x2 - width):min(game_map.width, x2 + width), y] = tile_types.floor
#     else:
#         # Vertical first, then horizontal
#         for y in range(min(y1, y2), max(y1, y2) + 1):
#             game_map.tiles[x1, y] = tile_types.floor
#             game_map.tiles[max(0, x1 - width):min(game_map.width, x1 + width), y] = tile_types.floor
#         for x in range(min(x1, x2), max(x1, x2) + 1):
#             game_map.tiles[x, y2] = tile_types.floor
#             game_map.tiles[x, max(0, y2 - width):min(game_map.height, y2 + width)] = tile_types.floor

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