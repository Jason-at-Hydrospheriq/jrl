#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
from components.display import tile_types

tile_dtype = np.dtype(
    [   ("tile_type", np.str_), # The type of the tile, e.g., 'floor', 'wall', etc. 
        ("traversable", np.bool),  # True if this tile can be occupied by or passed through by an entity.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ('visible', np.bool),  # True if this tile is currently visible.
        ('explored', np.bool),  # True if this tile has been explored.
        ('color', tile_types.graphic_dtype)
    ])


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


class GameMap:
    """The Game Map is a stateful coordinate system of Tiles. The Tiles have a State (traversable, transparent, visible, explored, color) that is
    managed by the Game Engine and rendered by the Game UI. The tile color is determined by the Map UI component based on the tile state and type.
    
    tiles: np.ndarray,  width x height x dimension tensor of tile_dtype
    width: int,  The width of the map in tiles and the rendered map object
    height: int,  The height of the map in tiles and the rendered map object

    """
    
    __slots__ = ("width", "height", "tiles")

    width: int
    height: int
    tiles: np.ndarray 

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles = np.full((width, height), fill_value=False, order="F", dtype=tile_dtype)
    
    @property
    def tile_types(self) -> np.ndarray:
        return self.tiles["tile_type"]
    
    @property
    def visible(self) -> np.ndarray:
        return self.tiles["visible"]
    
    @property
    def explored(self) -> np.ndarray:
        return self.tiles["explored"]
    
    @property
    def traversable(self) -> np.ndarray:
        return self.tiles["traversable"]
    
    @property
    def transparent(self) -> np.ndarray:
        return self.tiles["transparent"]

    @property
    def colors(self) -> np.ndarray:
        return self.tiles["color"]
    
    @staticmethod
    def get_map_coords(x: int, y: int) -> MapCoords:
        return MapCoords(x=x, y=y)
        
    def in_bounds(self, location: MapCoords) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        if not location.x is None and not location.y is None:
            return 0 <= location.x < self.width and 0 <= location.y < self.height
        return False
    
    def is_traversable(self, location: MapCoords) -> bool:
        """Return True if the tile at location is traversable."""
        if not self.in_bounds(location):
            return False
        
        return bool(self.tiles["traversable"][location.x, location.y].all())
           
    def is_transparent(self, location: MapCoords) -> bool:
        """Return True if the tile at location is transparent."""
        if not self.in_bounds(location):
            return False
        
        return bool(self.tiles["transparent"][location.x, location.y].all())
    
    def is_visible(self, location: MapCoords) -> bool:
        """Return True if the tile at location is visible."""
        if not self.in_bounds(location):
            return False
        
        return bool(self.tiles["visible"][location.x, location.y].all())
    
    def is_explored(self, location: MapCoords) -> bool:
        """Return True if the tile at location has been explored."""
        if not self.in_bounds(location):
            return False
        
        return bool(self.tiles["explored"][location.x, location.y].all())
    
    def get_tile_type(self, location: MapCoords) -> str:
        """Return the tile type at the given location."""
        if not self.in_bounds(location):
            return ""
        
        return str(self.tiles["tile_types"][location.x, location.y])
    
    def get_tile_color(self, location: MapCoords) -> np.ndarray:
        """Return the tile color at the given location."""
        if not self.in_bounds(location):
            return np.empty((3,))
        
        return self.tiles["colors"][location.x, location.y]
    
    def set_visible(self, fov: np.ndarray) -> None:
        """Set the visible state of the tiles based on the field of view."""
        self.tiles["visible"][:] = fov
    
    def update_explored(self, fov: np.ndarray) -> None:
        """Update the explored state of the tiles based on the field of view."""
        self.tiles["explored"][:] |= fov
    
    def reset_visibility(self) -> None:
        """Reset the visibility of all tiles on the map to not visible."""
        self.tiles["visible"][:, :] = False 