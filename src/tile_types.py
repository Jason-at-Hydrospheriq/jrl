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

# Tile struct used for statically defined tile data.
tile_dtype = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dtype),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dtype),  # Graphics for when this tile is in FOV.
    ]
)

SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dtype)  # Unknown tile

# Define Tiles Using Helper Function
def new_tile(*,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types """
    return np.array((walkable, transparent, dark, light), dtype=tile_dtype)

floor = new_tile(walkable=True, transparent=True, dark=(ord(" "), (255, 255, 255), (50, 50, 150)), light=(ord(" "), (255, 255, 255), (200, 180, 50)))
wall = new_tile(walkable=False, transparent=False, dark=(ord(" "), (255, 255, 255), (0, 0, 100)), light=(ord(" "), (255, 255, 255), (130, 110, 50)))