#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import random
from warnings import warn
from typing import Tuple
import numpy as np
from math import cos, pi, sin

from game_types import TileArea, BaseTileGrid, TileCoordinate, TileTuple

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
    _height: int
    _width: int

    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        grid_tuple = self._tiletuple_to_xy_tuple(self.parent_map_size)
        area_indices = TileTuple(([],[]))
        
        try:    
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

        except Exception as e:
            e.add_note(f"Area indices: {area_indices}")
            raise e
        
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
        center = self.center.to_xy_tiletuple
        mask = np.fromfunction(lambda xx, yy: (xx - center[0]) ** 2 + (yy - center[1]) ** 2 + 2 <= inner_radius ** 2,
                               grid_tuple, dtype=int)
        return mask


class GravPulseShipDeck(GenericMapArea):
    _radius: int
    _corridor_width: int

    def __init__(self, center: TileCoordinate = DEFAULT_CENTER_COORDINATE, corridor_width: int = 3, 
                 radius: int = 18) -> None:
        
        self.wall_thickness = 2
        self._corridor_width = corridor_width
        self._radius = radius
        center = TileCoordinate.from_tuple((25,25), parent_map_size=TileTuple( ([50], [50]) ))
        super().__init__(center=center)
        self.width = 50
        self.height = 50

    @property
    def radius(self) -> int:
        return self._radius

    @property
    def corridor_width(self) -> int:
        return self._corridor_width

    @property
    def outer_radius(self) -> int:
        return self._radius

    @property
    def inner_radius(self) -> int:
        return self.radius - self.corridor_width - 2 * self.wall_thickness
        
    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        # Inner Hull
        center = (self.width / 2, self.height / 2)
        y, x = np.ogrid[:self.height, :self.width]
        distance_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2 + 2)
        
        return (distance_from_center >= self.inner_radius) & (distance_from_center <= self.outer_radius)
    

class GravPulseShipBulkhead(GenericMapArea):
    
    def __init__(self, center: TileCoordinate = DEFAULT_CENTER_COORDINATE, thickness: int=2, angle: int=0) -> None:
        self.wall_thickness = thickness
        self.angle = angle
        center = TileCoordinate.from_tuple((25,25), parent_map_size=TileTuple( ([50], [50]) ))
        super().__init__(center=center)
        self.width = 50
        self.height = 50

    @property
    def to_mask(self) -> np.ndarray:
        """Return the inner area of this room as a 2D array index."""
        y, x = np.ogrid[:self.height, :self.width]
        
        m = (sin(self.angle/ 360 * 2 * pi) / cos(self.angle/ 360 * 2 * pi))
        y1 = m * (self.center.x - x) - self.wall_thickness / 2 + self.width / 2
        y2 = m * (self.center.x - x) + self.wall_thickness / 2 + self.width / 2

        mask = ~( (y >= y1) & (y <= y2) )
        
        return mask
    

