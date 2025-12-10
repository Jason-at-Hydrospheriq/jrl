#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
import numpy as np
import random
from typing import Protocol, Dict, Tuple, List, NewType
from copy import deepcopy
import numpy as np

# Defined as a global constant types and dtypes
ascii_graphic = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ], metadata={"__name__": "ascii_graphic"}
)

def new_tile_dtype(tile_type: np.dtype, graphic_dtype: np.dtype = ascii_graphic) -> np.dtype:
    """Generates the tile location dtype based on the provided tile_type dtype"""
    return np.dtype(
                    [   ("type", tile_type), # The type of the tile, e.g., 'floor', 'wall', etc. with associated graphic options.
                        ("traversable", np.bool),  # True if this tile can be occupied by or passed through by an entity.
                        ("transparent", np.bool),  # True if this tile doesn't block FOV.
                        ('visible', np.bool),  # True if this tile is currently visible.
                        ('explored', np.bool),  # True if this tile has been explored.
                        ('graphic', graphic_dtype) # The current graphic representation of the tile.
                    ], metadata={"__name__": "tile_location"})

TileTuple = NewType("TileTuple", tuple[List[int], List[int]])


class TileCoordinateSystem(Protocol):

    """A protocol defining methods for coordinate systems using TileTuple."""

    __slots__ = ("_size",)
    _size: TileTuple
    
    @property
    def _origin(self) -> TileTuple:
        return TileTuple( ([0], [0]) )
    
    @property
    def _system_coordinates(self) -> TileTuple:
        top_left = self._origin
        bottom_right = self._size
        
        return self._tiletuple_to_area_tiletuple(top_left, bottom_right)
    
    def _xy_to_tiletuple(self, x: int, y: int) -> TileTuple:
        return TileTuple(([x], [y]))
    
    def _tiletuple_to_area_tiletuple(self, top_left: TileTuple, lower_right: TileTuple) -> TileTuple:
        return TileTuple( (list(range(top_left[0][0], lower_right[0][0])),
                           list(range(top_left[1][0], lower_right[1][0])) ) )
    
    def _area_to_tiletuple(self, area: TileTuple) -> Tuple[TileTuple, TileTuple]:
        top_left = TileTuple( ([area[0][0]], [area[1][0]]) )
        lower_right = TileTuple( ([area[0][-1]], [area[1][-1]]) )
        return top_left, lower_right
    
    def _tiletuple_to_xy_tuple(self, x_y: TileTuple) -> Tuple[int, int]:
        return (x_y[0][0], x_y[1][0])
    
    def _tiletuple_to_tile_coordinate(self, x_y: TileTuple) -> TileCoordinate:
        return TileCoordinate(x_y, self._size)
    
    def _tiletuple_to_tile_area(self, area: TileTuple) -> TileArea:
        top_left, lower_right = self._area_to_tiletuple(area)

        return TileArea(self._tiletuple_to_tile_coordinate(top_left), 
                        self._tiletuple_to_tile_coordinate(lower_right))

    @staticmethod
    def _overhang(dimension1: TileTuple, dimension2: TileTuple) -> bool:
        dim1_set1 = set(dimension1[0])
        dim1_set2 = set(dimension2[0])
        dim1_overhang = dim1_set2.issubset(dim1_set1)

        dim2_set1 = set(dimension1[1])
        dim2_set2 = set(dimension2[1])
        dim2_overhang = dim2_set2.issubset(dim2_set1)
    
        return not (dim1_overhang and dim2_overhang)

    @staticmethod
    def _overlap(dimension1: TileTuple, dimension2: TileTuple) -> bool:
        dim1_set1 = set(dimension1[0])
        dim1_set2 = set(dimension2[0])
        dim1_overlap = dim1_set1.isdisjoint(dim1_set2)

        dim2_set1 = set(dimension1[1])
        dim2_set2 = set(dimension2[1])
        dim2_overlap = dim2_set1.isdisjoint(dim2_set2)
        
        return not (dim1_overlap or dim2_overlap)   


class TileCoordinateSystemElement(TileCoordinateSystem):
    """A protocol defining elements with parent coordinate systems that utilize TileCoordinateSystem methods."""
    
    @property
    def parent_map_size(self) -> TileTuple:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._size
    
    @parent_map_size.setter
    def parent_map_size(self, value: TileTuple) -> None:
        self._size = value

    @property
    def parent_map_width(self) -> int:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._size[0][0]
    
    @property
    def parent_map_height(self) -> int:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._size[1][0]
    
    @property
    def parent_map_coords(self) -> TileTuple:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._system_coordinates
 

class BaseTileGrid(TileCoordinateSystem):
    """A simple class for defining rectangular areas of Tiles using TileCoordinate for top-left and bottom-right corners.
    A TileArea is a 2D numpy array of Tiles. Tiles are defined using a custom numpy dtype defined in the new_tile_type
    function. A TileArea can be initialized with or without parameters."""

    _tiles: np.ndarray
    _dtype: np.dtype
    
    def __init__(self, dtype: np.dtype, size: TileTuple | None = None) -> None:

        warn("BaseTileGrid is an abstract class and should not be instantiated directly.", UserWarning)

        self._dtype = dtype
        if self._dtype.names:
            for prop in self._dtype.names:
                if not prop.startswith("_"):
                    setattr(self, prop, self._dtype[prop])
            
        if size is not None:
            self.size = size

    @property
    def width(self) -> int:
        return self.size[0][0]
    
    @property
    def height(self) -> int:
        return self.size[1][0]
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.width // 2, self.height // 2)
    
    @property
    def size(self) -> TileTuple:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'size' has not been set.")
        return self._size
    
    @size.setter
    def size(self, value: TileTuple) -> None:
        self._size = value
        if hasattr(self, "_dtype"):
            self._initialize_grid()

    @property
    def dtype(self) -> np.dtype:
        if not hasattr(self, "_dtype"):
            raise AttributeError("Attribute 'dtype' has not been set.")
        return self._dtype
    
    @property
    def tiles(self) -> np.ndarray:
        if not hasattr(self, "_tiles"):
            raise AttributeError("Attribute 'tiles' has not been set.")
        return self._tiles
    
    def get_location(self, x: int, y: int) -> TileCoordinate:
        return TileCoordinate( TileTuple( ([x], [y]) ), self._size )
    
    def get_area(self, top_left_xy: Tuple[int, int], bottom_right_xy: Tuple[int, int]) -> TileArea:
        top_left = TileCoordinate( TileTuple( ([top_left_xy[0]], [top_left_xy[1]]) ), self._size )
        bottom_right = TileCoordinate( TileTuple( ([bottom_right_xy[0]], [bottom_right_xy[1]]) ), self._size )
        return TileArea(top_left, bottom_right)
    
    def set_area(self, *args, **kwargs) -> None:
        raise NotImplementedError()
        
    def _initialize_grid(self) -> None:
        """This method should be overridden by subclasses to initialize the tile grid."""
        self._tiles = np.zeros((self.width, self.height), dtype=self._dtype)
        

class TileCoordinate(TileCoordinateSystemElement):
    """A simple class for x,y map coordinates. This class does not initialize the x,y attributes by default and can be 
    instantiated without parameters.
    
    Attributes:
        x: int, The x coordinate on the map
        y: int, The y coordinate on the map
    Empty Initialization:
        coords = TileCoordinate()
    Parameterized Initialization:
        coords = TileCoordinate(3, 4)
    Methods:
        __eq__(other: object) -> bool:  Compare two TileCoordinate instances for equality
    Raises:
        ValueError: If x or y are not integers.
        AttributeError: If x or y are accessed before being set.
    """
    __slots__ = ("x", "y")

    x: int 
    y: int

    def __init__(self, 
                 location: Tuple[List[int], List[int]] | None = None, 
                 parent_map_size: TileTuple | None = None) -> None:
        if location is not None:
            if not location[0]:
                pass
            else:
                self.x = location[0][0]
            if not location[1]:
                pass
            else:
                self.y = location[1][0]
        if parent_map_size is not None:
            if not parent_map_size[0] or not parent_map_size[1]:
                pass
            else:
                self._size = parent_map_size

    def __eq__(self, other: object) -> bool:
        try:
            if not isinstance(other, TileCoordinate):
                return False
            
            return hash(self) == hash(other)
        
        except AttributeError as e:
            e.add_note("Both TileCoordinate instances must have 'x', 'y', and 'map_size' attributes set for comparison.")
            raise
          
    def __repr__(self) -> str:
        rep = "TileCoordinate("

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
        return hash((self.x, self.y, self.parent_map_size[0][0], self.parent_map_size[1][0]))

    @property
    def to_xy_tuple(self) -> TileTuple:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to tuple.")
        
        return TileTuple( ([self.x], [self.y]) )
    
    @property
    def is_inbounds(self) -> bool:
        if not hasattr(self, "x") or not hasattr(self, "y") or not hasattr(self, "_size"):
            raise AttributeError("Attributes 'x', 'y', and 'parent_map_size' must be set to check inbounds status.")
        
        return self._overlap(self.parent_map_coords, self.to_xy_tuple)
    
    @property
    def to_tuple(self) -> Tuple[int, int]:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to tuple.")
        
        return (self.x, self.y)
    
    @property
    def to_array(self) -> np.ndarray:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to array.")
        
        return np.array([self.x, self.y])
    
    @property
    def to_list(self) -> list[int]:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to list.")
        
        return [self.x, self.y]


class TileArea(TileCoordinateSystemElement):

    """A simple class for defining rectangular areas on a map using TileCoordinate for top-left and bottom-right corners.
    
    Attributes:
        top_left: TileCoordinate, The top-left corner of the area
        bottom_right: TileCoordinate, The bottom-right corner of the area
    Initialization:
        area = TileArea(top_left: TileCoordinate, bottom_right: TileCoordinate)
    Methods:
        width() -> int: Returns the width of the area
        height() -> int: Returns the height of the area
    Raises:
        ValueError: If top_left or bottom_right are not TileCoordinate instances.
    """
    __slots__ = ("_top_left", "_bottom_right", "_center", "_height", "_width")

    _top_left: TileCoordinate
    _bottom_right: TileCoordinate
    _center: TileCoordinate
    _height: int
    _width: int

    def __init__(self, top_left: TileCoordinate | None = None, bottom_right: TileCoordinate | None = None) -> None:

        if top_left is not None:
            self.top_left = top_left
        if bottom_right is not None:
            self.bottom_right = bottom_right

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
    
    @property
    def top_left(self) -> TileCoordinate:
        if not hasattr(self, "_top_left"):
            raise AttributeError("Attribute 'top_left' has not been set.")
        return self._top_left
    
    @top_left.setter
    def top_left(self, value: TileCoordinate) -> None:
        if hasattr(self, "bottom_right"):
            if value.x > self.bottom_right.x or value.y > self.bottom_right.y:
                raise ValueError("top_left coordinates must be less than or equal to bottom_right coordinates.")
            if not value.parent_map_size == self.bottom_right.parent_map_size:
                raise ValueError("Parent_map_size of top_left and bottom_right must match. Parent map size cannot be inferred from TileCoordinate instances.")

        self._size = value.parent_map_size
        self._top_left = value
        
        if hasattr(self, "bottom_right"):
            self._width = self._calculated_width()
            self._height = self._calculated_height()
            self._align_center()

    @property
    def bottom_right(self) -> TileCoordinate:
        if not hasattr(self, "_bottom_right"):
            raise AttributeError("Attribute 'bottom_right' has not been set.")
        return self._bottom_right
    
    @bottom_right.setter
    def bottom_right(self, value: TileCoordinate) -> None:
        if hasattr(self, "top_left"):
            if value.x < self.top_left.x or value.y < self.top_left.y:
                raise ValueError("Top_left coordinates must be less than or equal to bottom_right coordinates.")
            if not value.parent_map_size == self.top_left.parent_map_size:
                raise ValueError("Parent_map_size of top_left and bottom_right must match. Parent map size cannot be inferred from TileCoordinate instances.")
            
        self._size = value.parent_map_size
        self._bottom_right = value

        if hasattr(self, "top_left"):
            self._width = self._calculated_width()
            self._height = self._calculated_height()
            self._align_center()

    @property
    def width(self) -> int:
        return self._width
    
    @width.setter
    def width(self, value: int) -> None:
        self._width = value
        self._align_corners()

    @property
    def height(self) -> int:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before accessing height.")
        
        return self.bottom_right.y - self.top_left.y + 1
    
    @height.setter
    def height(self, value: int) -> None:
        self._height = value
        self._align_corners()

    @property
    def center(self) -> TileCoordinate:
        return self._center
    
    @center.setter
    def center(self, value: TileCoordinate) -> None:
        self._center = value
        self._size = value.parent_map_size
        self._align_corners()

    @property
    def to_area_tuple(self) -> TileTuple:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before converting to area tuple.")
        
        return self._tiletuple_to_area_tiletuple(self.top_left.to_xy_tuple, self.bottom_right.to_xy_tuple)
    
    @property
    def is_inbounds(self) -> bool:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right") or not hasattr(self, "_size"):
            raise AttributeError("Attributes 'top_left', 'bottom_right', and 'parent_map_size' must be set to check inbounds status.")
        
        overhang = self._overhang(self.parent_map_coords, self.to_area_tuple)
        overlap = self._overlap(self.parent_map_coords, self.to_area_tuple)

        return overlap and not overhang

    @property
    def to_slices(self):
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before converting to slices.")
        
        return (slice(self.top_left.x, self.bottom_right.x + 1), slice(self.top_left.y, self.bottom_right.y + 1))

    @property
    def to_mask(self) -> np.ndarray:
        """ Return the coordinates of the area covered by this TileArea as a 2D numpy array of TileCoordinates."""
        map_tuple = self._tiletuple_to_xy_tuple(self.parent_map_size)
        mask = np.full(map_tuple, fill_value=False, dtype=bool)
        mask[self.to_slices] = True
        return mask
    
    def intersects(self, another_area: TileArea):
        """Check if this area intersects with another area."""
        if not isinstance(another_area, TileArea):
            raise TypeError("another_area must be an instance of TileArea.")
        
        return self._overlap(self.to_area_tuple, another_area.to_area_tuple)   
    
    def get_random_location(self) -> TileCoordinate:
        """Return a random location within this area."""
    
        x, y = random.choice(np.argwhere(self.to_mask))

        return TileCoordinate(TileTuple(([int(x)], [int(y)])), self.parent_map_size)

    def _align_corners(self) -> None:
        if not hasattr(self, "_center"):
            raise AttributeError("Center coordinate must be set before aligning corners.")
        
        half_width = self._width // 2
        half_height = self._height // 2

        top_left_xy = TileTuple( ([self._center.x - half_width], [self._center.y - half_height]) )
        bottom_right_xy = TileTuple( ([self._center.x + half_width], [self._center.y + half_height]) )

        self._top_left = TileCoordinate(top_left_xy, self._center.parent_map_size)
        self._bottom_right = TileCoordinate(bottom_right_xy, self._center.parent_map_size)

    def _align_center(self) -> None: 
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before aligning center.")
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' must be set before aligning center.")
        
        center_x = (self.top_left.x + self.bottom_right.x) // 2
        center_y = (self.top_left.y + self.bottom_right.y) // 2
        self._center = TileCoordinate(TileTuple(([center_x], [center_y])), self.parent_map_size)

    def _calculated_width(self) -> int:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before calculating width.")
        return self.bottom_right.x - self.top_left.x + 1
    
    def _calculated_height(self) -> int:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before calculating height.")
        return self.bottom_right.y - self.top_left.y + 1

