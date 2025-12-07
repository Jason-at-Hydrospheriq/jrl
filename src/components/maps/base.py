#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
import random
from typing import Tuple
import numpy as np

# Define Structured Data Types for Tile Maps

graphic_dtype = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)
tile_dtype = np.dtype([("name", np.str_, 16), ("shroud", graphic_dtype), ("dark", graphic_dtype), ("light", graphic_dtype)])
map_dtype = np.dtype(
    [   ("type", tile_dtype), # The type of the tile, e.g., 'floor', 'wall', etc. 
        ("traversable", np.bool),  # True if this tile can be occupied by or passed through by an entity.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ('visible', np.bool),  # True if this tile is currently visible.
        ('explored', np.bool),  # True if this tile has been explored.
        ('color', graphic_dtype)
    ])

SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dtype)  # Unknown tile

def new_tile_type(name: str,
                  dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]], 
                  light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
                  ) -> np.ndarray:
    """Helper function for defining tile types"""

    return np.array((name, SHROUD, dark, light), dtype=tile_dtype)


class MapCoords:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MapCoords):
            return NotImplemented
        return self.x == other.x and self.y == other.y


class BaseTileMap:
    """The Tile Map is a stateful coordinate system of Tiles. The Tiles have a State (traversable, transparent, visible, explored, color).
    
    tiles: np.ndarray,  width x height x dimension tensor of tile_dtype
    width: int,  The width of the map in tiles and the rendered map object
    height: int,  The height of the map in tiles and the rendered map object

    """
    
    __slots__ = ("width", "height", "tiles")

    width: int
    height: int
    tiles: np.ndarray 

    def __init__(self, width: int = 0, height: int = 0, default_tile: np.ndarray | None = None) -> None:

        self.width = width
        self.height = height
        self.tiles = np.full((width, height), fill_value=False, order="F", dtype=map_dtype)
        if default_tile is not None:
            self.tiles["type"] = default_tile

    def add_area(self, area: np.ndarray, tile_types: np.ndarray) -> None:
        """Add tiles to the map at the specified area."""
        self.tiles[area] = tile_types


class BaseRoom:
    __slots__ = ("_center", "tile_map")
    _center: MapCoords
    tile_map: BaseTileMap

    def __init__(self, x: int, y: int, tile_map: BaseTileMap | None = None):
        self._center = MapCoords(x, y)
        if tile_map:
            self.tile_map = tile_map

    @property
    def center(self) -> MapCoords:
        return self._center
    
    @center.setter
    def center(self, value: MapCoords) -> None:
        self._center = value
    
    @property
    def inner_area(self) -> np.ndarray:
        raise NotImplementedError()
    
    def contains(self, location: MapCoords) -> np.bool_:
        return self.inner_area[location.x, location.y]
    
    def intersects(self, other_room: BaseRoom) -> np.bool_:
        """Return True if this room intersects with another room."""
        own_area = self.inner_area
        intersection = own_area * other_room.inner_area
        return intersection.any()   
    
    def random_location(self) -> MapCoords:
        """Return a random location within this room."""
        area_indices = np.argwhere(self.inner_area)
        choice = random.choice(area_indices)
        return MapCoords(int(choice[0]), int(choice[1]))


class BaseMapGenerator:
    """Base class for map generators."""
    tile_map: BaseTileMap

    def generate(self, *args, **kwargs) -> BaseTileMap:
        raise NotImplementedError()