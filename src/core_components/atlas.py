#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from collections import OrderedDict
import numpy as np

from core_components.generators.base import BaseMapGenerator
from core_components.generators.library import DungeonGenerator
from core_components.maps.base import GraphicTileMap, TileCoordinate
from core_components.maps.library import DefaultTileMap        

class Atlas:
    """The Atlas component is a collection of map generators and a history of their generated maps. 
    It allows for the creation and management of multiple maps, and provides a way to switch between them.
    It also provides a way to save and load maps from a file.

    """
    
    __slots__ = ("generators", "library", "active")
    
    generators: OrderedDict[str, BaseMapGenerator]
    library: OrderedDict[str, GraphicTileMap]
    active: GraphicTileMap

    def __init__(self) -> None:

        self.generators = OrderedDict({'dungeon': DungeonGenerator()})
        self.library = OrderedDict({})
        self.library['_empty'] = DefaultTileMap()
        self.set_active_map('_empty')

    def set_active_map(self, map_name: str) -> None:
        """Set the active map to the one specified by map_name."""
        if map_name in self.library:
            self.active = self.library[map_name]
        else:
            raise ValueError(f"Map '{map_name}' does not exist in the library.")
    
    def get_map(self, map_name: str) -> GraphicTileMap:
        """Return the map specified by map_name."""
        if map_name in self.library:
            return self.library[map_name]
        else:
            raise ValueError(f"Map '{map_name}' does not exist in the library.")
    
    def create_map(self) -> None:
        """Create a new map using the specified generator and add it to the library."""
        if len(self.library.keys()) < 1:
            self.library['level_0'] = self.generators['dungeon'].generate()
            self.set_active_map('level_0')
        else:
            new_map_name = f"level_{len(self.library.keys())-1}"
            self.library[new_map_name] = self.generators['dungeon'].generate()
            self.set_active_map(new_map_name)