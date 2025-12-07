#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Tuple
import numpy as np

# Define Structured Data Types for Tile Maps

graphic_dtype = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

tile_dtype = np.dtype([("name", np.str_, 16), ("shroud", graphic_dtype), ("dark", graphic_dtype), ("light", graphic_dtype)])


map_dtype = np.dtype(
    [   ("type", tile_dtype), # The type of the tile, e.g., 'floor', 'wall', etc. 
        ("traversable", np.bool),  # True if this tile can be occupied by or passed through by an entity.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ('visible', np.bool),  # True if this tile is currently visible.
        ('explored', np.bool),  # True if this tile has been explored.
        ('color', graphic_dtype)
    ])

SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dtype)  # Unknown tile

def new_tile_type(name: str,
                  dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]], 
                  light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
                  ) -> np.ndarray:
    """Helper function for defining tile types"""

    return np.array((name, SHROUD, dark, light), dtype=tile_dtype)



