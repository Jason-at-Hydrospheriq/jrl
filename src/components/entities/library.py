#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Optional, Tuple, Type

from components.entities.attributes import *
from components.entities.ai import BaseAI

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


class BlockingEntity(BaseEntity):
    blocks_movement: bool = True

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    blocks_movement: bool=True) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        self.blocks_movement = blocks_movement


class MobileEntity(BaseEntity):
    destination: MapCoords

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    destination: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>") -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        if destination:
            self.destination = destination
    
    def move(self) -> None:
        if self.destination is not None:
            self.location = self.destination


class TargetingEntity(BaseEntity):
    target: TargetableEntity | None

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    target: TargetableEntity | None = None,
                 ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        self.target = target

    def acquire_target(self, target: TargetableEntity) -> None:
        self.target = target
    
    def clear_target(self) -> None:
        self.target = None


class TargetableEntity(BaseEntity):
    targetable: bool = True

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    targetable: bool=True,
                 ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        self.targetable = targetable


class MortalEntity(BaseEntity):
    physical: PhysicalStats | None

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    physical: PhysicalStats | None = None,
                 ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        self.physical = physical

    @property
    def is_alive(self) -> bool:
        if self.physical:
            return not self.physical.is_destroyed()
        return True
    
    def take_damage(self, damage: int) -> None:
        if self.physical:
            self.physical.hp -= damage
            if self.physical.hp <= 0:
                self.die()

    def die(self) -> None:
        raise NotImplementedError()


class CombatEntity(TargetingEntity):
    combat: CombatStats | None

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    combat: CombatStats | None = None,
                 ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        self.combat = combat

    def attack(self) -> int:
        return self.combat.attack_power - self.target.combat.defense  # type: ignore
    

class AIEntity(BaseEntity):
    _ai: Optional[BaseAI]

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    ai_cls: Optional[Type[BaseAI]] = None,
                 ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)

        # if ai_cls:
        #     self._ai = ai_cls()

    @property
    def ai(self) -> Optional[BaseAI]:
        return self._ai
    

class SightedEntity(BaseEntity):
    fov_radius: int

    def __init__(   self, 
                    *, 
                    location: MapCoords | None = None,
                    char: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    fov_radius: int = 4,
                 ) -> None:
        
        super().__init__(location=location, char=char, color=color, name=name)
        self.fov_radius = fov_radius
        

class Charactor(MobileEntity, TargetableEntity, MortalEntity, CombatEntity, SightedEntity):
    def __init__(   self,
                    *,
                    location: MapCoords | None = None,
                    char: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    targetable: bool = True,
                    ) -> None:
        
        MobileEntity.__init__(self, location=location, char=char, color=color, name=name)
        TargetableEntity.__init__(self, location=location, char=char, color=color, name=name, targetable=targetable)
        MortalEntity.__init__(self, location=location, char=char, color=color, name=name, physical=physical)
        CombatEntity.__init__(self, location=location, char=char, color=color, name=name, combat=combat)
        SightedEntity.__init__(self, location=location, char=char, color=color, name=name, fov_radius=fov_radius)


    def die(self) -> None:
       self.blocks_movement = False
       self.name = f"remains of {self.name}"
       self.char = "%"
       self.color = (191, 0, 0)


class AICharactor(Charactor, AIEntity):
    def __init__(   self,
                    *,
                    location: MapCoords | None = None,
                    char: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    targetable: bool = True,
                    ai_cls: Optional[Type[BaseAI]] = None,
                    ) -> None:
        
        Charactor.__init__(self, location=location, char=char, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, targetable=targetable)
        AIEntity.__init__(self, location=location, char=char, color=color, name=name, ai_cls=ai_cls) 
    
    def die(self) -> None:
        super().die()
        self._ai = None
        