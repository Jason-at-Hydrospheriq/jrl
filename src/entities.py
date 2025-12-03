#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from tcod.map import compute_fov
import numpy as np
from typing import Optional, Tuple, TypeVar, TYPE_CHECKING, Set
from copy import deepcopy

from actions import MovementAction
if TYPE_CHECKING:
    from game_map import GameMap

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    game_map: GameMap
    x: int
    y: int
    char: str
    color: Tuple[int, int, int]
    name: str
    blocks_movement: bool

    def __init__(self, game_map: GameMap | None = None, x: int=0, y: int=0, char: str=' ', color: Tuple[int, int, int]=(0,0,0), name: str='Entity', blocks_movement: bool=False):
        
        if game_map:
            self.game_map = game_map
            self.game_map.entities.add(self)

        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
    
    def spawn(self: T, game_map: GameMap, location) -> T:
        """Spawn a copy of this entity at the given location."""
        clone = deepcopy(self)
        clone.x = int(location['x'])
        clone.y = int(location['y'])
        clone.game_map = game_map
        game_map.entities.add(clone)
        return clone
    

class Character(Entity):
    def __init__(self, game_map: GameMap | None = None, x: int=0, y: int=0, char: str=' ', color: Tuple[int, int, int]=(0,0,0), name: str='Entity', blocks_movement: bool=False, fov_radius: int=4):
        super().__init__(game_map=game_map, x=x, y=y, char=char, color=color, name=name, blocks_movement=True)
        self.fov_radius = fov_radius

    def move(self, action: MovementAction) -> None:
        # Move the entity by a given amount
        self.x += action.dx
        self.y += action.dy

