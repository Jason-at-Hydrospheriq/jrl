#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
from typing import Tuple
import numpy as np

from core_components.tiles.base import BaseTileGrid, TileCoordinates, new_tile_location_dtype, ascii_graphic

DEFAULT_TILE_LOCATION_DTYPE = new_tile_location_dtype(np.dtype([("name", "U16"),("g_shroud", ascii_graphic)], metadata={"__name__": "tile_type"}))

class TileArea(BaseTileGrid):
    """A simple class for defining rectangular areas on a map using TileCoordinates for top-left and bottom-right corners.
    
    Attributes:
        top_left: TileCoordinates, The top-left corner of the area
        bottom_right: TileCoordinates, The bottom-right corner of the area
    Initialization:
        area = TileArea(top_left: TileCoordinates, bottom_right: TileCoordinates)
    Methods:
        width() -> int: Returns the width of the area
        height() -> int: Returns the height of the area
    Raises:
        ValueError: If top_left or bottom_right are not TileCoordinates instances.
    """
    __slots__ = ("_top_left", "_bottom_right", "parent_map_size")

    _top_left: TileCoordinates
    _bottom_right: TileCoordinates
    parent_map_size: Tuple[int, int]

    def __init__(self, top_left: TileCoordinates | None = None, bottom_right: TileCoordinates | None = None, tile_location_dtype: np.dtype = DEFAULT_TILE_LOCATION_DTYPE) -> None:
        
        self._dtype = tile_location_dtype

        if top_left is not None:
            self.top_left = top_left
        if bottom_right is not None:
            self.bottom_right = bottom_right

    @property
    def top_left(self) -> TileCoordinates:
        return self._top_left
    
    @top_left.setter
    def top_left(self, value: TileCoordinates) -> None:
        self._top_left = value
        if hasattr(self, "_bottom_right"):
            self.initialize()

    @property
    def bottom_right(self) -> TileCoordinates:
        return self._bottom_right
    
    @bottom_right.setter
    def bottom_right(self, value: TileCoordinates) -> None:
        self._bottom_right = value
        if hasattr(self, "_top_left"):
            self.initialize()

    @property
    def is_inbounds(self) -> bool:
        return self.top_left.is_inbounds and self.bottom_right.is_inbounds

    def __repr__(self) -> str:
        return f"TileArea(top_left={self.top_left}, bottom_right={self.bottom_right})"
    
    def __hash__(self) -> int:
        return hash((self.top_left, self.bottom_right))
    
    def __eq__(self, other: object) -> bool:
        try:
            if not isinstance(other, TileArea):
                return False
            
            return hash(self) == hash(other)
        
        except AttributeError as e:
            e.add_note("Both MapArea instances must have 'top_left' and 'bottom_right' attributes set for comparison.")
            raise
 
    def _initialize_dimensions(self) -> None:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            warn("Both 'top_left' and 'bottom_right' attributes must be set to determine dimensions. Width and height not set.")
        
        if hasattr(self, "top_left") and hasattr(self, "bottom_right"):
            self._width = self.bottom_right.x - self.top_left.x + 1
            self._height = self.bottom_right.y - self.top_left.y + 1

    def _initialize_parent_map_size(self) -> None:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            warn("Both 'top_left' and 'bottom_right' attributes must be set to determine map_size. Map size not set.")
        
        if self.top_left.parent_map_size != self.bottom_right.parent_map_size:
            warn("Both 'top_left' and 'bottom_right' must have the same 'map_size' attribute. Map size not set.")

        if hasattr(self, "top_left") and hasattr(self, "bottom_right"):
            self.parent_map_size = self.top_left.parent_map_size

    def initialize(self) -> None:
        self._initialize_dimensions()
        self._initialize_parent_map_size()
        self._initialize_grid()
    
    def to_slices(self):
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before converting to slices.")
        
        return (slice(self.top_left.x, self.bottom_right.x + 1), slice(self.top_left.y, self.bottom_right.y + 1))