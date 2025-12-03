#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from tcod.map import compute_fov
import numpy as np
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING
from copy import deepcopy

from components.stats import PhysicalStats, MentalStats, CombatStats
from components.ai import BaseAI

if TYPE_CHECKING:
    from game_map import GameMap
    from engine import Engine

#Type variable used for type hinting 'self' returns
T = TypeVar("T", bound="BaseEntity")


class BaseEntity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    game_map: GameMap
    x: int
    y: int
    char: str
    color: Tuple[int, int, int]
    name: str

    def __init__(   self, 
                 game_map: GameMap | None = None, 
                 x: int=0, 
                 y: int=0, 
                 char: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0), 
                 name: str='<Unnamed>') -> None:
        
        if game_map:
            self.game_map = game_map
            self.game_map.entities.add(self)

        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name

    @property
    def location(self) -> np.ndarray | None:
        return self.game_map.get_entity_location(self) if self.game_map else None
        
    @property
    def engine(self) -> Optional[Engine]:
        return self.game_map.engine if self.game_map else None
    
    def spawn(self: T, game_map: GameMap, location) -> T:
        """Spawn a copy of this entity at the given location."""
        clone = deepcopy(self)
        clone.x = int(location['x'])
        clone.y = int(location['y'])
        clone.game_map = game_map
        game_map.entities.add(clone)
        return clone


class PhysicalObject(BaseEntity):
    dx: int = 0
    dy: int = 0
    target_dx: int = 0
    target_dy: int = 0
    blocks_movement: bool
    targetable: bool = True
    physical: PhysicalStats | None
    combat: CombatStats | None

    def __init__(   self, 
                    *, 
                    x: int=0, 
                    y: int=0, 
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    blocks_movement: bool=False, 
                    targetable: bool=True,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                 ) -> None:
        
        super().__init__(x=x, y=y, char=char, color=color, name=name)
        self.blocks_movement = blocks_movement
        self.targetable = targetable
        self.physical = physical
        self.combat = combat

    @property
    def destination(self) -> np.ndarray:
        destination = self.game_map.get_entity_location(self).copy()
        destination['x'] += self.dx
        destination['y'] += self.dy
        return destination

    @property
    def target_location(self) -> np.ndarray:
        target_location = self.game_map.get_entity_location(self).copy()
        target_location['x'] += self.target_dx
        target_location['y'] += self.target_dy
        return target_location
    
    @property
    def collision(self) -> bool:
        out_of_bounds = not self.game_map.in_bounds(self.destination)
        blocked = self.game_map.get_entity_at_location(self.destination) is not None
        walkable = self.game_map.tiles["walkable"][self.destination['x'], self.destination['y']]
        return blocked or not walkable or out_of_bounds
    
    def move(self) -> None:
        self.x += self.dx
        self.dx = 0
        self.y += self.dy
        self.dy = 0
    

class Charactor(PhysicalObject):
    fov_radius: int
    mental: MentalStats | None

    def __init__(   self,
                    *,
                    x: int = 0,
                    y: int = 0,
                    char: str,
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    mental: MentalStats | None = None,
                    targetable: bool = True,
                    ) -> None:

        super().__init__(x=x, y=y, char=char, color=color, name=name, physical=physical, combat=combat, targetable=targetable)
        self.fov_radius = fov_radius
        self.mental = mental

    @property
    def event_handler(self):
        if not hasattr(self, '_ai'):
            return self.game_map.engine.player_event_handler if self.game_map else None
        else:
            return self.__getattribute__('_ai')

    @property
    def fov(self) -> np.ndarray:
        """Return the actor's field of view as a boolean array."""
        if self.game_map:
            return compute_fov(self.game_map.tiles["transparent"], (self.x, self.y), radius=self.fov_radius, algorithm=tcod.FOV_SHADOW)
        else:
            return np.array([])

    @property
    def is_alive(self) -> bool:
        alive = True
        if self.physical:
            alive = not self.physical.is_destroyed()
        if self.mental:
            alive = alive and self.mental.is_conscious()        
        return alive


class AICharactor(Charactor):
    _ai: Optional[BaseAI]
    
    def __init__(   self,
                    *,
                    x: int = 0,
                    y: int = 0,
                    char: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    ai_cls: Type[BaseAI],
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    mental: MentalStats | None = None,
                    targetable: bool = True,
                    ) -> None:
        
        super().__init__(x=x, y=y, char=char, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, mental=mental, targetable=targetable)
        self._ai = ai_cls(self)

    @property
    def in_player_fov(self) -> bool:
        if self.game_map:
            return self.game_map.visible[self.x, self.y]
        return False
    
    @property
    def is_alive(self) -> bool:
        alive = super().is_alive
        if not alive and self._ai:
            # self._ai.on_death()
            self._ai = None
        return alive
    
    
EntityTypes = TypeVar("EntityTypes", BaseEntity, PhysicalObject, Charactor, AICharactor)
ActorTypes = TypeVar("ActorTypes", Charactor, AICharactor)