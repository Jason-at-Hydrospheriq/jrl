#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
from typing import Tuple
import numpy as np

from core_components.tiles.base import BaseTileGrid, TileCoordinate, TileArea

class GenericRoom(TileArea):

    def __init__(self, center: TileCoordinate, size: Tuple[int, int]) -> None:
        self.parent_map_size = center.parent_map_size
        self.center = center
        self.width = size[0]
        self.height = size[1]

    @property
    def to_mask(self) -> np.ndarray:
        """Override TileArea.to_mask to return a mask of the room area."""
        raise NotImplementedError("Subclasses must implement the to_mask property.")


class RectangularRoom(GenericRoom):

    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        mask = np.full((self.width, self.height), False, dtype=bool)
        mask[1:-1, 1:-1] = True

        return mask


class CircularRoom(GenericRoom):
    _radius: int

    def __init__(self, center: TileCoordinate, radius: int = 3):
        super().__init__(center, (radius * 2, radius * 2))
        self._radius = radius

    @property
    def radius(self) -> int:
        return self._radius
    
    @radius.setter
    def radius(self, value: int) -> None:
        self._radius = value
        self.width = value * 2
        self.height = value * 2
        
    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        center = (self.width // 2, self.height // 2)
        mask = np.fromfunction(lambda xx, yy: (xx - center[0]) ** 2 + (yy - center[1]) ** 2 + 2 <= self.radius ** 2,
                               (self.width + 1, self.height + 1), dtype=int)
        return mask

        # @property
    # def tile_types(self) -> np.ndarray:
    #     return self.tiles["type"]
    
    # @property
    # def visible_tiles(self) -> np.ndarray:
    #     return self.tiles["visible"]
    
    # @property
    # def explored_tiles(self) -> np.ndarray:
    #     return self.tiles["explored"]
    
    # @property
    # def traversable_tiles(self) -> np.ndarray:
    #     return self.tiles["traversable"]
    
    # @property
    # def transparent_tiles(self) -> np.ndarray:
    #     return self.tiles["transparent"]

    # @property
    # def tile_graphics(self) -> np.ndarray:
    #     return self.tiles["graphic"]
    
    # def _initialize_grid(self) -> None:
    #     """Initializes the tile grid with default values."""
    #     self._tiles = np.full((self._width, self._height), fill_value=False, dtype=self._dtype)

    # def get_type_at(self, location: TileCoordinate) -> np.ndarray:
    #     """Return the tile type at the given location."""
    #     if not location.is_inbounds:
    #         return np.empty((1,))
        
    #     return self.tiles["type"][location.x, location.y]
    
    # def get_graphic_at(self, location: TileCoordinate) -> np.ndarray:
    #     """Return the tile color at the given location."""
    #     if not location.is_inbounds:
    #         return np.empty((3,))
        
    #     return self.tiles["colors"][location.x, location.y]
    
    # def is_traversable_at(self, location: TileCoordinate) -> bool:
    #     """Return True if the tile at location is traversable."""
    #     if not location.is_inbounds:
    #         return False
        
    #     return bool(self.tiles["traversable"][location.x, location.y].all())
           
    # def is_transparent_at(self, location: TileCoordinate) -> bool:
    #     """Return True if the tile at location is transparent."""
    #     if not location.is_inbounds:
    #         return False
        
    #     return bool(self.tiles["transparent"][location.x, location.y].all())
    
    # def is_visible_at(self, location: TileCoordinate) -> bool:
    #     """Return True if the tile at location is visible."""
    #     if not location.is_inbounds:
    #         return False
        
    #     return bool(self.tiles["visible"][location.x, location.y].all())
    
    # def is_explored_at(self, location: TileCoordinate) -> bool:
    #     """Return True if the tile at location has been explored."""
    #     if not location.is_inbounds:
    #         return False
        
    #     return bool(self.tiles["explored"][location.x, location.y].all())
 
