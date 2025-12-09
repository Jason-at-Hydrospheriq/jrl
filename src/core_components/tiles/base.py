#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
import numpy as np
import random
from typing import Protocol, Dict, Tuple, List
from copy import deepcopy
import numpy as np

# Defined as a global constant dtypes
ascii_graphic = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ], metadata={"__name__": "ascii_graphic"}
)

def new_tile_location_dtype(tile_type: np.dtype, graphic_dtype: np.dtype = ascii_graphic) -> np.dtype:
    """Generates the tile location dtype based on the provided tile_type dtype"""
    return np.dtype(
                    [   ("type", tile_type), # The type of the tile, e.g., 'floor', 'wall', etc. with associated graphic options.
                        ("traversable", np.bool),  # True if this tile can be occupied by or passed through by an entity.
                        ("transparent", np.bool),  # True if this tile doesn't block FOV.
                        ('visible', np.bool),  # True if this tile is currently visible.
                        ('explored', np.bool),  # True if this tile has been explored.
                        ('graphic', graphic_dtype) # The current graphic representation of the tile.
                    ], metadata={"__name__": "tile_location"})


class TileCoordinates:
    """A simple class for x,y map coordinates. This class does not initialize the x,y attributes by default and can be 
    instantiated without parameters.
    
    Attributes:
        x: int, The x coordinate on the map
        y: int, The y coordinate on the map
    Empty Initialization:
        coords = TileCoordinates()
    Parameterized Initialization:
        coords = TileCoordinates(3, 4)
    Methods:
        __eq__(other: object) -> bool:  Compare two TileCoordinates instances for equality
    Raises:
        ValueError: If x or y are not integers.
        AttributeError: If x or y are accessed before being set.
    """
    __slots__ = ("x", "y", "parent_map_size")

    x: int 
    y: int 
    parent_map_size: Tuple[int, int]

    def __init__(self, x: int | None = None, y: int | None = None, parent_map_size: Tuple[int, int] | None = None) -> None:
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if parent_map_size is not None:
            self.parent_map_size = parent_map_size

    def __eq__(self, other: object) -> bool:
        try:
            if not isinstance(other, TileCoordinates):
                return False
            
            return hash(self) == hash(other)
        
        except AttributeError as e:
            e.add_note("Both TileCoordinates instances must have 'x', 'y', and 'map_size' attributes set for comparison.")
            raise
          
    def __repr__(self) -> str:
        rep = "TileCoordinates("

        if hasattr(self, "x"):
            rep += f"x={self.x}, "
        else:
            rep += "x=None, "

        if hasattr(self, "y"):
            rep += f"y={self.y}, "
        else:
            rep += "y=None, "

        if hasattr(self, "parent_map_size"):
            rep += f"parent_map_size={self.parent_map_size})"
        else:
            rep += "parent_map_size=None)"
        
        return rep
    
    def __hash__(self) -> int:
        return hash((self.x, self.y, self.parent_map_size))
    
    @property
    def is_inbounds(self) -> bool:
        if not hasattr(self, "x") or not hasattr(self, "y") or not hasattr(self, "parent_map_size"):
            raise AttributeError("Attributes 'x', 'y', and 'parent_map_size' must be set to check inbounds status.")
        
        width, height = self.parent_map_size
        return 0 <= self.x < width and 0 <= self.y < height
        
    def to_tuple(self) -> Tuple[int, int]:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to tuple.")
        
        return (self.x, self.y)
    
    def to_array(self) -> np.ndarray:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to array.")
        
        return np.array([self.x, self.y])
    
    def to_list(self) -> list[int]:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to list.")
        
        return [self.x, self.y]


class BaseTileGrid(Protocol):
    __slots__ = ("_width", "_height", "_tiles", "_dtype")

    _width: int
    _height: int
    _tiles: np.ndarray
    _dtype: np.dtype

    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def size(self) -> Tuple[int, int]:
        return (self._width, self._height)
    
    @property
    def dtype(self) -> np.dtype:
        return self._dtype
    
    @property
    def tiles(self) -> np.ndarray:
        return self._tiles
    
    @property
    def types(self) -> np.ndarray:
        return self.tiles["type"]
    
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
    def graphics(self) -> np.ndarray:
        return self.tiles["graphic"]
    
    def _initialize_grid(self) -> None:
        """Initializes the tile grid with default values."""
        self._tiles = np.full((self._width, self._height), fill_value=False, dtype=self._dtype)
        
    def get_coordinate(self, x: int, y: int) -> TileCoordinates:
        return TileCoordinates(x=x, y=y, parent_map_size=self.size)
    
    def get_type_at(self, location: TileCoordinates) -> np.ndarray:
        """Return the tile type at the given location."""
        if not location.is_inbounds:
            return np.empty((1,))
        
        return self.tiles["type"][location.x, location.y]
    
    def get_graphic_at(self, location: TileCoordinates) -> np.ndarray:
        """Return the tile color at the given location."""
        if not location.is_inbounds:
            return np.empty((3,))
        
        return self.tiles["colors"][location.x, location.y]
    
    def is_traversable_at(self, location: TileCoordinates) -> bool:
        """Return True if the tile at location is traversable."""
        if not location.is_inbounds:
            return False
        
        return bool(self.tiles["traversable"][location.x, location.y].all())
           
    def is_transparent_at(self, location: TileCoordinates) -> bool:
        """Return True if the tile at location is transparent."""
        if not location.is_inbounds:
            return False
        
        return bool(self.tiles["transparent"][location.x, location.y].all())
    
    def is_visible_at(self, location: TileCoordinates) -> bool:
        """Return True if the tile at location is visible."""
        if not location.is_inbounds:
            return False
        
        return bool(self.tiles["visible"][location.x, location.y].all())
    
    def is_explored_at(self, location: TileCoordinates) -> bool:
        """Return True if the tile at location has been explored."""
        if not location.is_inbounds:
            return False
        
        return bool(self.tiles["explored"][location.x, location.y].all())
 
