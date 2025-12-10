#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
from typing import Tuple
import numpy as np

from core_components.tiles.base import TileArea, TileCoordinates, new_tile_dtype, ascii_graphic

DEFAULT_TILE_LOCATION_DTYPE = new_tile_dtype(np.dtype([("name", "U16"),("g_shroud", ascii_graphic)], metadata={"__name__": "tile_type"}))

class TileArea(TileArea):


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
           