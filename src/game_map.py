#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
import tcod
from tcod.console import Console
from tcod.map import compute_fov
from typing import Iterable, Set, Optional, Tuple, List

from entities import Character, Entity
import tile_types


# Define Structured Data Types for GameMap
# Location structured type.
location_dtype = np.dtype(
    [
        ("x", np.int32),  
        ("y", np.int32)
    ]
)

class GameMap:
    def __init__(self, width: int, height: int, player: Character, mobs: Iterable[Character], ):
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
        self.player = player
        self.mobs = set(mobs)
        self.objects = {}
        self.visible: np.ndarray = np.full((width, height), fill_value=False, order="F")
        self.explored: np.ndarray = np.full((width, height), fill_value=False, order="F")
    
    @property
    def all_entities(self) -> Set:
        return self.mobs.union({self.player}.union(self.objects))
    
    @property
    def all_non_player_entities(self) -> Set:
        return self.mobs.union(self.objects)
    
    @property
    def all_entity_blocked_tiles(self) -> List[np.ndarray]:
        return [self.get_entity_location(entity) for entity in self.all_entities if entity.blocks_movement]

    @property
    def non_player_entity_blocked_tiles(self) -> List[np.ndarray]:
        return [self.get_entity_location(entity) for entity in self.all_non_player_entities if entity.blocks_movement]
    
    @staticmethod
    def get_entity_location(entity: Entity) -> np.ndarray:
        return np.array((entity.x, entity.y), dtype=location_dtype)
    
    @staticmethod
    def get_map_location(x: int, y: int) -> np.ndarray:
        return np.array((x, y), dtype=location_dtype)
    
    def get_entity_by_location(self, location) -> Entity|None:
        entity_locations = [(self.get_entity_location(entity), entity) for entity in self.all_entities]
        for entity_location, entity in entity_locations:
            if entity_location == location:
                return entity
            else:
                return None
            
    def in_bounds(self, target) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= target['x'].all() < self.width and 0 <= target['y'].all() < self.height

    def render(self, console: Console, view_mobs: bool=False) -> None:
        if self.non_player_entity_blocked_tiles:
            for location in self.non_player_entity_blocked_tiles:
                self.tiles['walkable'][location['x'], location['y']] = False

        if self.player:
            self.visible[:] = compute_fov(self.tiles["transparent"], (self.player.x, self.player.y), radius=self.player.fov_radius, algorithm=tcod.FOV_SHADOW)
            self.explored |= self.visible

        console.rgb[0:self.width, 0:self.height] = np.select(condlist=[self.visible, self.explored], choicelist=[self.tiles["light"], self.tiles["dark"]],
           default=tile_types.SHROUD)
        
        for entity in self.all_entities:
            # if self.visible[entity.x, entity.y] or view_mobs:
            console.print(entity.x, entity.y, entity.char, fg=entity.color)