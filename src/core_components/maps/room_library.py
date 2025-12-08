#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np

from components.maps.dtype_library import *
from components.maps.base import BaseRoom, MapCoords, BaseTileMap


class RectangularRoom(BaseRoom):
    width: int
    height: int
    upperLeft_corner: MapCoords
    lowerRight_corner: MapCoords

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y)
        self.width = width
        self.height = height

    @property
    def center(self) -> MapCoords:
        return self._center
    
    @center.setter
    def center(self, value: MapCoords) -> None:
        self._center = value
        self.upperLeft_corner = MapCoords(value.x - self.width // 2, value.y - self.height // 2)
        self.lowerRight_corner = MapCoords(value.x + self.width // 2, value.y + self.height // 2)
    
    @property
    def inner_area(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        mask = np.fromfunction(lambda xx, yy: (self.upperLeft_corner.x <= xx) & (xx < self.lowerRight_corner.x) & (self.upperLeft_corner.y <= yy) & (yy < self.lowerRight_corner.y),
                               (self.tile_map.width, self.tile_map.height), dtype=int)
        return mask


class CircularRoom(BaseRoom):
    radius: int

    def __init__(self, x: int, y: int, radius: int):
        super().__init__(x, y)
        self.radius = radius

    @property
    def inner_area(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        mask = np.fromfunction(lambda xx, yy: (xx - self.center.x) ** 2 + (yy - self.center.y) ** 2 <= self.radius ** 2 + 2,
                               (self.tile_map.width, self.tile_map.height), dtype=int)
        return mask