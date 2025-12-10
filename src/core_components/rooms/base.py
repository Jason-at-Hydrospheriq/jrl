#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
import random
from typing import Protocol, Dict, Tuple, List
from copy import deepcopy
import numpy as np

from core_components.tiles.base import TileCoordinates

class BaseRoom(Protocol):
    __slots__ = ("_center", "width", "height", "_upperLeft_corner", "_lowerRight_corner")
    _center: TileCoordinates    
    width: int
    height: int
    _upperLeft_corner: TileCoordinates
    _lowerRight_corner: TileCoordinates
    
    @property
    def center(self) -> TileCoordinates:
        return self._center
    
    @center.setter
    def center(self, value: TileCoordinates) -> None:
        self._center = value
    
    @property
    def upperLeft_corner(self) -> TileCoordinates:
        return self._upperLeft_corner
    
    @upperLeft_corner.setter
    def upperLeft_corner(self, value: TileCoordinates) -> None:
        self._upperLeft_corner = value

    @property
    def lowerRight_corner(self) -> TileCoordinates:
        return self._lowerRight_corner

    @lowerRight_corner.setter
    def lowerRight_corner(self, value: TileCoordinates) -> None:
        self._lowerRight_corner = value
    
    @property
    def inner_area(self) -> np.ndarray:
        raise NotImplementedError()

    def resize(self, new_size: Tuple[int, int]) -> None:
        """ Resize the room to the new size."""
        self.width = new_size[0]
        self.height = new_size[1]
        self.upperLeft_corner = TileCoordinates(self.center.x - self.width // 2, self.center.y - self.height // 2)
        self.lowerRight_corner = TileCoordinates(self.center.x + self.width // 2, self.center.y + self.height // 2)
    
    def area_coordinates(self) -> np.ndarray:
        """ Return the coordinates of the area covered by this room as a 2D numpy array of TileCoordinates."""
        return np.argwhere(self.inner_area) + np.array([self.upperLeft_corner.x, self.upperLeft_corner.y])
    
    def intersects(self, other_room: BaseRoom) -> bool:
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
