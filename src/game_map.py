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


class MapCoords:
    x: int
    y: int

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MapCoords):
            return NotImplemented
        return self.x == other.x and self.y == other.y

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
    def physical_objects(self) -> Set[EntityTypes]:
        return {entity for entity in self.entities if entity.physical}
    
    @property
    def live_actors(self) -> List[ActorTypes]:
        return [entity for entity in self.entities if issubclass(entity.__class__, Charactor) and entity.is_alive]
    
    @property
    def live_ai_actors(self) -> List[AICharactor]:
        return [entity for entity in self.live_actors if isinstance(entity, AICharactor) and entity.is_alive]
    
    @property
    def blocked_tiles(self) -> List[MapCoords]:
        blocked = []
        for obj in self.physical_objects:
            if obj.blocks_movement:
                blocked.append(obj.location)
        return blocked
    
    @staticmethod
    def get_map_coords(x: int, y: int) -> MapCoords:
        return MapCoords(x=x, y=y)
    
    def get_entity_at_location(self, location: MapCoords) -> Optional[EntityTypes]:
        """Return first entity found at location."""
        if self.in_bounds(location) is True:
            for entity in self.entities:
                if entity.location == location:
                    return entity
        return None
        
    def in_bounds(self, location: MapCoords) -> bool:
        """Return True if x and y are inside of the bounds of this map."""
        if not location.x is None and not location.y is None:
            return 0 <= location.x < self.width and 0 <= location.y < self.height
        return False
    
    def walkable(self, location: MapCoords) -> bool:
        """Return True if the tile at location is walkable."""
        if not self.in_bounds(location):
            return False
        
        return bool(self.tiles["walkable"][location.x, location.y].all())
           
    def render(self, console: Console, view_mobs: bool=False) -> None:
        # for location in self.blocked_tiles:
        #     self.tiles['walkable'][location.x, location.y] = False

        if self.player:
            self.visible[:] = self.player.fov
            self.explored |= self.visible

        console.rgb[0:self.width, 0:self.height] = np.select(condlist=[self.visible, self.explored], choicelist=[self.tiles["light"], self.tiles["dark"]],
           default=tile_types.SHROUD)
        
        for entity in self.entities | {self.player}:
            if self.visible[entity.location.x, entity.location.y] or view_mobs:
                console.print(entity.location.x, entity.location.y, entity.char, fg=entity.color)