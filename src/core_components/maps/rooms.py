#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
from typing import Tuple
from core_components.maps.base import BaseRoom, MapCoords


class RectangularRoom(BaseRoom):

    def __init__(self, center: MapCoords = MapCoords(0, 0), size: Tuple[int, int] = (4, 4)) -> None:
        self.center = center
        self.width = size[0]
        self.height = size[1]
        self.upperLeft_corner = MapCoords(center.x - self.width // 2, center.y - self.height // 2)
        self.lowerRight_corner = MapCoords(center.x + self.width // 2, center.y + self.height // 2)

    @property
    def center(self) -> MapCoords:
        return self._center
    
    @center.setter
    def center(self, value: MapCoords) -> None:
        self._center = value
    
    @property
    def inner_area(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        mask = np.full((self.width, self.height), False, dtype=bool)
        mask[1:-1, 1:-1] = True

        return mask


class CircularRoom(RectangularRoom):
    radius: int

    def __init__(self, center: MapCoords = MapCoords(0, 0), radius: int = 3):
        super().__init__(center, (radius * 2, radius * 2))
        
        self.radius = radius

    @property
    def inner_area(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        center = (self.width // 2, self.height // 2)
        mask = np.fromfunction(lambda xx, yy: (xx - center[0]) ** 2 + (yy - center[1]) ** 2 + 2 <= self.radius ** 2,
                               (self.width + 1, self.height + 1), dtype=int)
        return mask