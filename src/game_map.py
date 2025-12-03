#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np
import tcod
from tcod.console import Console
from tcod.map import compute_fov
from typing import Generator, Iterable, Set, Optional, Tuple, List, TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from engine import Engine

from entities import EntityTypes, ActorTypes, PhysicalObject, Charactor, AICharactor
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

    __slots__ = ("width", "height", "tiles", "player", "entities","visible", "explored", "engine")

    width: int
    height: int
    tiles: np.ndarray
    player: Charactor
    entities: Set
    visible: np.ndarray
    explored: np.ndarray
    engine: Engine

    def __init__(self, engine: Engine,width: int, height: int, player: Charactor, entities: Iterable[EntityTypes]=[]) -> None:
        self.engine = engine
        self.width, self.height = width, height
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
        self.player = player
        self.entities = set(entities)
        self.visible: np.ndarray = np.full((width, height), fill_value=False, order="F")
        self.explored: np.ndarray = np.full((width, height), fill_value=False, order="F")
    
    @property
    def entity_locations(self) -> List[Tuple[EntityTypes, np.ndarray]]:
        return [(entity, self.get_entity_location(entity)) for entity in self.entities]
    
    @property
    def physical_objects(self) -> Set[EntityTypes]:
        return {entity for entity in self.entities if issubclass(entity.__class__, PhysicalObject)}
    
    @property
    def live_actors(self) -> Generator[ActorTypes]:
        yield from (entity for entity in self.entities if issubclass(entity.__class__, Charactor) and entity.is_alive)
    
    @property
    def live_ai_actors(self) -> Generator[AICharactor]:
        yield from (entity for entity in self.live_actors if isinstance(entity, AICharactor) and entity.is_alive)
    
    @property
    def blocked_tiles(self) -> Generator[np.ndarray]:
        for obj in self.physical_objects:
            if obj.blocks_movement:
                yield self.get_entity_location(obj)
    
    @staticmethod
    def get_entity_location(entity: EntityTypes) -> np.ndarray:
        return np.array((entity.x, entity.y), dtype=location_dtype)
    
    @staticmethod
    def get_map_location(x: int, y: int) -> np.ndarray:
        return np.array((x, y), dtype=location_dtype)
    
    def get_entity_at_location(self, location) -> Optional[EntityTypes]:
        for entity, entity_location in self.entity_locations:
            if entity_location == location:
                return entity
        return None
        
    def in_bounds(self, location) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        return 0 <= location['x'].all() < self.width and 0 <= location['y'].all() < self.height
             
    def render(self, console: Console, view_mobs: bool=False) -> None:
        for location in self.blocked_tiles:
            self.tiles['walkable'][location['x'], location['y']] = False

        if self.player:
            self.visible[:] = self.player.fov
            self.explored |= self.visible

        console.rgb[0:self.width, 0:self.height] = np.select(condlist=[self.visible, self.explored], choicelist=[self.tiles["light"], self.tiles["dark"]],
           default=tile_types.SHROUD)
        
        for entity in self.entities:
            if self.visible[entity.x, entity.y] or view_mobs:
                console.print(entity.x, entity.y, entity.char, fg=entity.color)