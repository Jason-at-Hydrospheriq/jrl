#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Tuple
import numpy as np

from game_types import GraphicTileMap
from manifests import DEFAULT_TILEMAP_MANIFEST

class DefaultTileMap(GraphicTileMap):

    def __init__(self, graphics_manifest=DEFAULT_TILEMAP_MANIFEST) -> None:
        super().__init__(graphics_manifest=graphics_manifest)
    
    @property
    def blocks_movement(self) -> np.ndarray:
        return self.get_state_bits('blocks_movement')
    
    @property
    def blocks_vision(self) -> np.ndarray:
        return self.get_state_bits('blocks_vision')
    
    @property
    def seen(self) -> np.ndarray:
        return self.get_state_bits('seen')

    @property
    def visible(self) -> np.ndarray:
        return self.get_state_bits('visible')
