#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
import random
from typing import Protocol, Dict, Tuple, List
from copy import deepcopy
import numpy as np

# Defined as a global constant for graphic dtype
from core_components.tiles.base import TileCoordinate, TileTuple
from core_components.maps.base import GraphicTileMap
from core_components.tiles.library import GenericMapArea

class BaseMapGenerator(Protocol):
    """
    The BaseMapGenerator Protocol defines the methods that all map generators must implement. This protocol ensures that all map generators can be used 
    interchangeably in the game engine. The generator is a component of the Atlas object and is responsible for creating and populating the map with rooms, 
    corridors, and other elements. The generator does NOT handle the placement of entities or items on the map. It only creates the map object and returns a copy
    of it to the Atlas object.

    For a full implementation, see the `core_components.generators` module.
    """
    map: GraphicTileMap

    def generate(self, *args, **kwargs) -> GraphicTileMap:
        raise NotImplementedError()
    
    def add(self,
                area: GenericMapArea,
                center: TileCoordinate,
                size: TileTuple) -> GenericMapArea | None:
        
        method_name = "_add_" + area.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method:
            return method(area, center, size)
        return None