#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import random
from warnings import warn
from typing import Tuple
import numpy as np

from core_components.tiles.base import BaseTileGrid, TileCoordinate, TileArea, TileTuple

DEFAULT_GRID_SIZE = TileTuple( ([10], [10]) )
DEFAULT_CENTER_LOCATION = TileTuple( ([5], [5]) )
DEFAULT_CENTER_COORDINATE = TileCoordinate(DEFAULT_CENTER_LOCATION, DEFAULT_GRID_SIZE)

class GenericMapArea(TileArea):
    wall_thickness: int = 1

    def __init__(self, center: TileCoordinate = DEFAULT_CENTER_COORDINATE, 
                 height: int=5, width: int=5) -> None:
        self.parent_map_size = center.parent_map_size
        self.center = center
        self.width = width
        self.height = height

    @property
    def to_mask(self) -> np.ndarray:
        """Override TileArea.to_mask to return a mask of the room area."""
        raise NotImplementedError("Subclasses must implement the to_mask property.")


class GenericCorridor(GenericMapArea):
    start: TileCoordinate
    end: TileCoordinate

    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this corridor as a 2D array index."""
        
        grid_tuple = self._tiletuple_to_xy_tuple(self.parent_map_size)
        mask = np.full(grid_tuple, fill_value=False, dtype=bool)
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y
        width = random.randint(0, 2)

        if random.random() < 0.5:
            # Horizontal first, then vertical
            for x in range(min(x1, x2), max(x1, x2) + 1):
                mask[x, y1] = True
                mask[x, max(0, y1 - width):min(self.height, y1 + width)] = True
            for y in range(min(y1, y2), max(y1, y2) + 1):
                mask[x2, y] = True
                mask[max(0, x2 - width):min(self.width, x2 + width), y] = True
        else:
            # Vertical first, then horizontal
            for y in range(min(y1, y2), max(y1, y2) + 1):
                mask[x1, y] = True
                mask[max(0, x1 - width):min(self.width, x1 + width), y] = True
            for x in range(min(x1, x2), max(x1, x2) + 1):
                mask[x, y2] = True
                mask[x, max(0, y2 - width):min(self.height, y2 + width)] = True

        return mask


class RectangularRoom(GenericMapArea):
    height: int
    width: int

    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        grid_tuple = self._tiletuple_to_xy_tuple(self.parent_map_size)

        area_indices = self.to_area_indicies_tuple
        x_left_ = area_indices[0][0] + self.wall_thickness
        x_right_ = area_indices[0][-1] - self.wall_thickness + 1
        self.width = (x_right_ - x_left_)

        y_top_ = area_indices[1][0] + self.wall_thickness
        y_bottom_ = area_indices[1][-1] - self.wall_thickness + 1
        self.height = y_bottom_ - y_top_
        
        x_slice = slice(x_left_, x_right_)
        y_slice = slice(y_top_, y_bottom_)

        mask = np.full(grid_tuple, fill_value=False, dtype=bool)

        mask[x_slice, y_slice] = True

        return mask


class CircularRoom(GenericMapArea):
    _radius: int

    def __init__(self, center: TileCoordinate = DEFAULT_CENTER_COORDINATE, 
                 radius: int = 3):
        super().__init__(center=center, width=radius * 2, height=radius * 2)
        self._radius = radius

    @property
    def radius(self) -> int:
        return self._radius
    
    @radius.setter
    def radius(self, value: int) -> None:
        self._radius = value
        self.width = value * 2
        self.height = value * 2
        self._align_corners()
        
    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        grid_tuple = self._tiletuple_to_xy_tuple(self.parent_map_size)
        inner_radius = self.radius - self.wall_thickness
        center = self.center.to_xy_tuple
        mask = np.fromfunction(lambda xx, yy: (xx - center[0]) ** 2 + (yy - center[1]) ** 2 + 2 <= inner_radius ** 2,
                               grid_tuple, dtype=int)
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
 
