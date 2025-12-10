#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
import numpy as np
import random
from typing import Protocol, Dict, Tuple, List
from copy import deepcopy
import numpy as np

from core_components.tiles.base import TileArea, TileCoordinates, ascii_graphic


class BaseTileMap(TileArea):
    __slots__ = ("_resources",)
    _resources: Dict
   
    def __init__(self, size: Tuple[int, int]) -> None:
        self._width, self._height = size

        self._resources = {
            "graphics": {},
            "tiles": {},
            "tile_type_graphic_fields": ['g_shroud', 'g_visible', 'g_explored'],
            "dtypes": {}
        }

        self.initialize_resources()
        self.initialize_map()

    @property
    def resources(self) -> dict:
        return deepcopy(self._resources)
    
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
            # TODO: Consider moving this to BaseTileGrid protocol

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
    
    def get_map_coordinate(self, x: int, y: int) -> TileCoordinates:
        return TileCoordinates(x=x, y=y, map_size=self.size)

    def get_map_area(self, top_left_x: int, bottom_right_x: int, top_left_y: int, bottom_right_y: int) -> TileArea:
        top_left = TileCoordinates(x=top_left_x, y=top_left_y, map_size=self.size)
        bottom_right = TileCoordinates(x=bottom_right_x, y=bottom_right_y, map_size=self.size)
        return TileArea(top_left=top_left, bottom_right=bottom_right)

    def get_type_at(self, location: TileCoordinates) -> str:
        """Return the tile type at the given location."""
        if not location.is_inbounds:
            return ""
        
        return str(self.tiles["tile_types"][location.x, location.y])
    
    def get_graphic_at(self, location: TileCoordinates) -> np.ndarray:
        """Return the tile color at the given location."""
        if not location.is_inbounds:
            return np.empty((3,))
        
        return self.tiles["colors"][location.x, location.y]
    
    def set_area(self, 
                 area: TileArea | np.ndarray, 
                 tile_type: str = "floor",
                 traversable: bool = True,
                 transparent: bool = True) -> None:
        
        """Set tiles on the map at the specified area."""
        
        if isinstance(area, np.ndarray):
            area_slice = [area[:,0], area[:,1]]

        elif isinstance(area, TileArea):
            area_slice = area.to_slices()
            
        self.tiles['type'][area_slice[0], area_slice[1]] = self._resources['tiles'][tile_type]
        self.tiles['graphic'][area_slice[0], area_slice[1]] = self._resources['tiles'][tile_type]['g_shroud']
        self.tiles['traversable'][area_slice[0], area_slice[1]] = traversable
        self.tiles['transparent'][area_slice[0], area_slice[1]] = transparent

        #TODO Update unit tests for add_area method

    def set_visible(self, fov: np.ndarray) -> None:
        """Set the visible state of the tiles based on the field of view."""
        self.tiles["visible"][:] = fov
    
    def update_explored(self, fov: np.ndarray) -> None:
        """Update the explored state of the tiles based on the field of view."""
        self.tiles["explored"][:] |= fov
    
    def update_graphics(self, graphics: np.ndarray) -> None:
        """Update the graphic state of the tiles."""
        self.tiles["graphic"][:] = graphics
        
    def reset_visibility(self) -> None:
        """Reset the visibility of all tiles on the map to not visible."""
        self.tiles["visible"][:, :] = False

    def reset_exploration(self) -> None:

        """Reset the exploration state of all tiles on the map to not explored."""
        self.tiles["explored"][:, :] = False 

        