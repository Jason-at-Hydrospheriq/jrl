#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from tcod.map import compute_fov
import numpy as np
from typing import Tuple, List, Set, TypeVar, TYPE_CHECKING
from copy import deepcopy

from actions import MovementAction

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x: int=0, y: int=0, char: str=' ', color: Tuple[int, int, int]=(0,0,0), name: str='Entity', blocks_movement: bool=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
    
    def spawn(self: T, mobs: Set[T], location) -> T:
        """Spawn a copy of this entity at the given location."""
        clone = deepcopy(self)
        clone.x = int(location['x'])
        clone.y = int(location['y'])
        mobs.add(clone)
        return clone
    

class Character(Entity):
    def __init__(self, char: str, color: Tuple[int, int, int], x: int = 0, y: int = 0, name: str='Entity', fov_radius: int=4):
        super().__init__(x, y, char, color, name, blocks_movement=True)
        self.fov_radius = fov_radius

    def move(self, action: MovementAction) -> None:
        # Move the entity by a given amount
        self.x += action.dx
        self.y += action.dy

