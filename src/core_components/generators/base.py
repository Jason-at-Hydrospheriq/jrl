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
from core_components.tilemaps.library import GenericTileMap
from core_components.tiles.library import GenericRoom

class BaseMapGenerator(Protocol):
    """Base class for map generators."""
    tilemap: GenericTileMap

    def generate(self, *args, **kwargs) -> GenericTileMap:
        raise NotImplementedError()
    
    def spawn_room(self,
                   room: GenericRoom,
                   center: TileCoordinate,
                   size: Tuple[int, int]) -> GenericRoom | None:
        
        method_name = "_spawn_" + room.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method:
            return method(room, center, size)
        return None