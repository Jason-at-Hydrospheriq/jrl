#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from tcod.map import compute_fov
from tcod import libtcodpy
import numpy as np
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING
from copy import deepcopy

from components.attributes.stats import PhysicalStats, MentalStats, CombatStats
from components.action_handlers.ai import BaseAI

from components.game_map import MapCoords



class BaseEntity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    location: MapCoords
    char: str
    color: Tuple[int, int, int]
    name: str

    def __init__(   self, 
                 location: MapCoords | None = None,
                 char: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0), 
                 name: str="<Unnamed>") -> None:
        
        if location:
            self.location = location
    
        self.char = char
        self.color = color
        self.name = name


class PhysicalObject(BaseEntity):
    destination: MapCoords
    target: PhysicalObject | Charactor | AICharactor
    blocks_movement: bool = True
    targetable: bool = True
    physical: PhysicalStats | None
    combat: CombatStats | None

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    destination: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    blocks_movement: bool=True, 
                    targetable: bool=True,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                 ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        self.blocks_movement = blocks_movement
        self.targetable = targetable
        self.physical = physical
        self.combat = combat

        if destination:
            self.destination = destination
    
    def move(self) -> None:
        if self.destination is not None:
            self.location = self.destination
    
    def die(self) -> None:
        raise NotImplementedError()


class Charactor(PhysicalObject):
    fov_radius: int
    mental: MentalStats | None

    def __init__(   self,
                    *,
                    location: MapCoords | None = None,
                    char: str,
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    mental: MentalStats | None = None,
                    targetable: bool = True,
                    ) -> None:

        super().__init__(location=location, char=char, color=color, name=name, physical=physical, combat=combat, targetable=targetable)
        self.fov_radius = fov_radius
        self.mental = mental

    # @property
    # def event_handler(self):
    #     if not hasattr(self, '_ai'):
    #         return self.game_map.engine.event_handler if self.game_map else None
    #     else:
    #         return self.__getattribute__('_ai')

    # @property Make into state variable and an ACTION
    # def fov(self) -> np.ndarray:
    #     """Return the actor's field of view as a boolean array."""
    #     if self.game_map and self.location is not None:
    #         return compute_fov(self.game_map.tiles["transparent"], (self.location.x, self.location.y), radius=self.fov_radius, algorithm=libtcodpy.FOV_SHADOW)
    #     else:
    #         return np.array([])

    @property
    def is_alive(self) -> bool:
        alive = True
        if self.physical:
            alive = not self.physical.is_destroyed()
        if self.mental:
            alive = alive and self.mental.is_conscious()        
        return alive

    def attack(self) -> int:
        return self.combat.attack_power - self.target.combat.defense  # type: ignore

    def die(self) -> None:
       self.blocks_movement = False
       self.name = f"remains of {self.name}"
       self.char = "%"
       self.color = (191, 0, 0)


class AICharactor(Charactor):
    _ai: Optional[BaseAI]
    
    def __init__(   self,
                    *,
                    location: MapCoords | None = None,
                    char: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    ai_cls,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    mental: MentalStats | None = None,
                    targetable: bool = True,
                    ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, mental=mental, targetable=targetable)
        self._ai = ai_cls

    @property
    def ai(self) -> Optional[BaseAI]:
        return self._ai
    
    @property
    def is_alive(self) -> bool:
        alive = super().is_alive
        if not alive and self._ai:
            # self._ai.on_death()
            self._ai = None
        return alive
    
    def die(self) -> None:
        super().die()
        self._ai = None
       
EntityTypes = TypeVar("EntityTypes", BaseEntity, PhysicalObject, Charactor, AICharactor)
ActorTypes = TypeVar("ActorTypes", Charactor, AICharactor)