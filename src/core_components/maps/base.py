#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
import random
from typing import Protocol, Dict, Tuple, List
from copy import deepcopy
import numpy as np

# Defined as a global constant for graphic dtype
ascii_graphic = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ], metadata={"__name__": "ascii_graphic"}
)

class MapCoords:
    """A simple class for x,y map coordinates. This class does not initialize the x,y attributes by default and can be 
    instantiated without parameters.
    
    Attributes:
        x: int, The x coordinate on the map
        y: int, The y coordinate on the map
    Empty Initialization:
        coords = MapCoords()
    Parameterized Initialization:
        coords = MapCoords(3, 4)
    Methods:
        __eq__(other: object) -> bool:  Compare two MapCoords instances for equality
    Raises:
        ValueError: If x or y are not integers.
        AttributeError: If x or y are accessed before being set.
    """
    __slots__ = ("x", "y")

    x: int 
    y: int 

    def __init__(self, x: int | None = None, y: int | None = None) -> None:
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MapCoords):
            return False
        return self.x == other.x and self.y == other.y

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y])
    
    def to_list(self) -> list[int]:
        return [self.x, self.y]
    

class BaseTileMap(Protocol):
    __slots__ = ("_resources", "_width", "_height", "_tiles")

    _width: int
    _height: int
    _resources: Dict
    _tiles: np.ndarray
        
    @property
    def width(self) -> int:
        return self._width
    @property
    def height(self) -> int:
        return self._height
    @property
    def resources(self) -> dict:
        return deepcopy(self._resources)
    @property
    def tiles(self) -> np.ndarray:
        return self._tiles
    
    def initialize_resources(self) -> None:
        """Initializes the resources for the tile map, including graphics, dtypes, and tiles."""
        self._generate_graphics()
        self._generate_dtypes()
        self._generate_tiles()

    def initialize_map(self) -> None:
        """Initializes the tile map with default tiles."""
        tile_location_dtype = self._resources["dtypes"]["tile_location"]
        self._tiles = np.full((self._width, self._height), fill_value=False, order="F", dtype=tile_location_dtype)
        self._tiles['type'] = self._resources['tiles']['default']
        self._tiles['graphic'] = self._resources['tiles']['default']['g_shroud']

    def _generate_dtypes(self) -> None:

        """Generates the tile and tile location dtypes based on the graphic definitions"""

        graphic_fields = [(field, ascii_graphic) for field in self._resources['tile_type_graphic_fields']]
        tile_type =  np.dtype([("name", "U16")] + graphic_fields, metadata={"__name__": "tile_type"})
        self._resources["dtypes"]["tile_type"] = tile_type

        tile_location = np.dtype(
                            [   ("type", tile_type), # The type of the tile, e.g., 'floor', 'wall', etc. with associated graphic options.
                                ("traversable", np.bool),  # True if this tile can be occupied by or passed through by an entity.
                                ("transparent", np.bool),  # True if this tile doesn't block FOV.
                                ('visible', np.bool),  # True if this tile is currently visible.
                                ('explored', np.bool),  # True if this tile has been explored.
                                ('graphic', ascii_graphic) # The current graphic representation of the tile.
                            ], metadata={"__name__": "tile_location"})

        self._resources["dtypes"]["tile_location"] = tile_location
    
    def _generate_graphics(self) -> None:
        """Generates the graphic definitions for the map"""
        for graphic_name, graphic_def in self._resources['graphics'].items():
            self._resources['graphics'][graphic_name] = np.array(graphic_def, dtype=ascii_graphic)
    
    def _generate_tiles(self) -> None:
        for tile_name, tile_def in self._resources['tiles'].items():
            values = (tile_name,) + tuple(
                self._resources['graphics'][tile_def[field]]
                for field in self._resources['tile_type_graphic_fields']
            )
            tile = np.array(values, dtype=self._resources['dtypes']['tile_type'])
            self._resources['tiles'][tile_name] = tile

    def add_area(self, area: np.ndarray | tuple[slice, slice], tile_type: str = "floor") -> None:
        """Add tiles to the map at the specified area."""
        self.tiles['type'][area] = self._resources['tiles'][tile_type]
        self.tiles['graphic'][area] = self._resources['tiles'][tile_type]['g_shroud']


class BaseRoom(Protocol):
    __slots__ = ("_center", "width", "height", "_upperLeft_corner", "_lowerRight_corner")
    _center: MapCoords
    width: int
    height: int
    _upperLeft_corner: MapCoords
    _lowerRight_corner: MapCoords
    
    @property
    def center(self) -> MapCoords:
        return self._center
    
    @center.setter
    def center(self, value: MapCoords) -> None:
        self._center = value
    
    @property
    def upperLeft_corner(self) -> MapCoords:
        return self._upperLeft_corner
    
    @upperLeft_corner.setter
    def upperLeft_corner(self, value: MapCoords) -> None:
        self._upperLeft_corner = value

    @property
    def lowerRight_corner(self) -> MapCoords:
        return self._lowerRight_corner

    @lowerRight_corner.setter
    def lowerRight_corner(self, value: MapCoords) -> None:
        self._lowerRight_corner = value
    
    @property
    def inner_area(self) -> np.ndarray:
        raise NotImplementedError()

    def area_coordinates(self) -> np.ndarray:
        """ Return the coordinates of the area covered by this room as a 2D numpy array of MapCoords."""
        return np.argwhere(self.inner_area) + np.array([self.upperLeft_corner.x, self.upperLeft_corner.y])
    
    def intersects(self, other_room: BaseRoom) -> bool:
        """ Return True if this room intersects with another room."""
        this_room_x = set(np.arange(self.upperLeft_corner.x, self.lowerRight_corner.x))
        this_room_y = set(np.arange(self.upperLeft_corner.y, self.lowerRight_corner.y))

        other_room_x = set(np.arange(other_room.upperLeft_corner.x, other_room.lowerRight_corner.x))
        other_room_y = set(np.arange(other_room.upperLeft_corner.y, other_room.lowerRight_corner.y))
        
        return not this_room_x.isdisjoint(other_room_x) and not this_room_y.isdisjoint(other_room_y)
    
    def contains(self, location: MapCoords) -> bool:
        """ Return True if the given location is within this room."""
        
        return any((location.to_array() == coord).all() for coord in self.area_coordinates())
        
    def random_location(self) -> MapCoords:
        """Return a random location within this room."""
        area_coords = self.area_coordinates()
        x_range = area_coords[:, 0]
        y_range = area_coords[:, 1]
        x_choice = random.choice(x_range)
        y_choice = random.choice(y_range)
        return MapCoords(int(x_choice), int(y_choice))


class BaseMapGenerator(Protocol):
    """Base class for map generators."""
    tilemap: BaseTileMap
    room_templates: Dict[str, BaseRoom]

    def generate(self, *args, **kwargs) -> BaseTileMap:
        raise NotImplementedError()