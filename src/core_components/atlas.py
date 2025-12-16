#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from collections import OrderedDict
import numpy as np

from core_components.generators.base import BaseMapGenerator
from core_components.generators.library import DungeonGenerator
from core_components.maps.base import GraphicTileMap, TileCoordinate
        
class Atlas:
    """The Atlas component is a collection of map generators and a history of their generated maps. 
    It allows for the creation and management of multiple maps, and provides a way to switch between them.
    It also provides a way to save and load maps from a file.

    """
    
    __slots__ = ("generator", "library", "active")
    
    generators: OrderedDict[str, BaseMapGenerator]
    library: OrderedDict[str, GraphicTileMap]
    
    def __init__(self, width: int = 0, height: int = 0) -> None:

        self.generator = OrderedDict({'dungeons': DungeonGenerator()})
        self.library = OrderedDict({'initial': self.generator['dungeons'].generate()})
        self.active = self.library['initial']

    