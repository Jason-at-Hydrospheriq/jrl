#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
from typing import Tuple
import numpy as np

from core_components.tiles.base import TileArea, TileCoordinates, new_tile_dtype, ascii_graphic

DEFAULT_TILE_LOCATION_DTYPE = new_tile_dtype(np.dtype([("name", "U16"),("g_shroud", ascii_graphic)], metadata={"__name__": "tile_type"}))

class GenericRoom(TileArea):
    


    def intersects(self, other_room: ) -> bool:
        """ Return True if this room intersects with another room."""
        this_room_x = set(np.arange(self.upperLeft_corner.x, self.lowerRight_corner.x))
        this_room_y = set(np.arange(self.upperLeft_corner.y, self.lowerRight_corner.y))

        other_room_x = set(np.arange(other_room.upperLeft_corner.x, other_room.lowerRight_corner.x))
        other_room_y = set(np.arange(other_room.upperLeft_corner.y, other_room.lowerRight_corner.y))
        
        return not this_room_x.isdisjoint(other_room_x) and not this_room_y.isdisjoint(other_room_y)
    
    def contains(self, location: TileCoordinates) -> bool:
        """ Return True if the given location is within this room."""
        
        return any((location.to_array() == coord).all() for coord in self.area_coordinates())
        
    def random_location(self) -> TileCoordinates:
        """Return a random location within this room."""
        area_coords = self.area_coordinates()
        x_range = area_coords[:, 0]
        y_range = area_coords[:, 1]
        x_choice = random.choice(x_range)
        y_choice = random.choice(y_range)
        return TileCoordinates(int(x_choice), int(y_choice))

    def resize(self, new_size: Tuple[int, int]) -> None:
        """ Resize the room to the new size."""
        self.width = new_size[0]
        self.height = new_size[1]
        self.upperLeft_corner = TileCoordinates(self.center.x - self.width // 2, self.center.y - self.height // 2)
        self.lowerRight_corner = TileCoordinates(self.center.x + self.width // 2, self.center.y + self.height // 2)
    

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
 
