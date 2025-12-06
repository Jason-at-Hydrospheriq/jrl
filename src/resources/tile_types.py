#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Tuple
import numpy as np

# Define Structured Data Types for Tiles

# Tile graphics structured type compatible with tcod Console.tiles_rgb.
graphic_dtype = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ]
)

tile_dtype = np.dtype([("name", np.str_, 16), ("shroud", graphic_dtype), ("dark", graphic_dtype), ("light", graphic_dtype)])

def new_tile_type(name: str,
                  dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]], 
                  light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
                  ) -> np.ndarray:
    """Helper function for defining tile types"""

    return np.array((name, SHROUD, dark, light), dtype=tile_dtype)


SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dtype)  # Unknown tile

floor = new_tile_type(name="floor",
                      dark=(ord(" "), (255, 255, 255), (50, 50, 150)), 
                      light=(ord(" "), (255, 255, 255), (200, 180, 50)))

wall = new_tile_type(name="wall",
                     dark=(ord(" "), (255, 255, 255), (0, 0, 100)), 
                     light=(ord(" "), (255, 255, 255), (130, 110, 50)))