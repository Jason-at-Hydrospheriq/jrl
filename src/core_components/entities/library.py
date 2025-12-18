#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Optional, Tuple, Type

from core_components.entities.attributes import *
from core_components.entities.ai import BaseAI

from core_components.tiles.base import TileCoordinate


class BaseEntity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    location: TileCoordinate
    symbol: str
    color: Tuple[int, int, int]
    name: str

    def __init__(   self, 
                 location: TileCoordinate | None = None,
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0), 
                 name: str="<Unnamed>") -> None:
        
        if location:
            self.location = location
    
        self.symbol = symbol
        self.color = color
        self.name = name


class BlockingEntity(BaseEntity):
    blocks_movement: bool = True

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    blocks_movement: bool=True) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.blocks_movement = blocks_movement


class MobileEntity(BaseEntity):
    destination: TileCoordinate

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    destination: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>") -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        if destination:
            self.destination = destination
    
    def move(self) -> None:
        if self.destination is not None:
            self.location = self.destination


class TargetingEntity(BaseEntity):
    target: TargetableEntity | None

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    target: TargetableEntity | None = None,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.target = target

    def acquire_target(self, target: TargetableEntity) -> None:
        self.clear_target()
        self.target_color = target.color  # Store original color
        self.target = target
        self.target.color = (255, 0, 0)  # Change color to indicate targeting
        
    def clear_target(self) -> None:
        if self.target is not None and hasattr(self, 'target_color'):
            self.target.color = self.target_color  # Restore original color
        self.target = None


class TargetableEntity(BaseEntity):
    targetable: bool = True

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    targetable: bool=True,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.targetable = targetable


class MortalEntity(BaseEntity):
    physical: PhysicalStats | None

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    physical: PhysicalStats | None = None,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.physical = physical

    @property
    def is_alive(self) -> bool:
        if self.physical:
            return not self.physical.is_destroyed()
        return True
    
    def take_damage(self, damage: int) -> None:
        if self.physical:
            self.physical.hp -= damage

    def die(self) -> None:
        raise NotImplementedError()


class CombatEntity(TargetingEntity):
    combat: CombatStats | None
    in_combat: bool = False

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    combat: CombatStats | None = None,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.combat = combat

    def acquire_target(self, target: TargetableEntity) -> None:
        if isinstance(target, CombatEntity):
            combat_status = (self.in_combat, target.in_combat)
            match combat_status:
                case (True, True): # Both are in combat
                    pass
                case (True, False): # Entity is in combat, target is not
                    self.in_combat = False
                case (False, True): # Entity is not in combat, target is
                    self.in_combat = True
                case (False, False): # Neither are in combat, hostile mobs are ALWAYS in combat.
                    pass
                    
        self.target = target

    def attack(self) -> int:
        return self.combat.attack_power - self.target.combat.defense  # type: ignore
    

class AIEntity(BaseEntity):
    _ai: Optional[BaseAI]

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    ai_cls: Optional[Type[BaseAI]] = None,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)

        # if ai_cls:
        #     self._ai = ai_cls()

    @property
    def ai(self) -> Optional[BaseAI]:
        return self._ai
    

class SightedEntity(BaseEntity):
    fov_radius: int

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    fov_radius: int = 4,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.fov_radius = fov_radius
    

class Charactor(SightedEntity, CombatEntity, MortalEntity, TargetableEntity, TargetingEntity, MobileEntity, BlockingEntity):
    def __init__(   self,
                    *,
                    location: TileCoordinate | None = None,
                    symbol: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    targetable: bool = True,
                    ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.fov_radius = fov_radius
        self.physical = physical
        self.combat = combat
        self.targetable = targetable

    def die(self) -> None:
        self.blocks_movement = False
        self.name = f"remains of {self.name}"
        self.symbol = "%"
        self.color = (191, 0, 0)


class PlayerCharactor(Charactor):
    def __init__(   self,
                *,
                location: TileCoordinate | None = None,
                symbol: str = "@",
                color: Tuple[int, int, int],
                name: str = "<Unnamed>",
                fov_radius: int = 4,
                physical: PhysicalStats | None = None,
                combat: CombatStats | None = None,
                targetable: bool = True,
                ) -> None:
    
        super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, targetable=targetable)


class AICharactor(Charactor, AIEntity):
    def __init__(   self,
                    *,
                    location: TileCoordinate | None = None,
                    symbol: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    targetable: bool = True,
                    ai_cls: Optional[Type[BaseAI]] = None,
                    ) -> None:
        
        Charactor.__init__(self, location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, targetable=targetable)
        AIEntity.__init__(self, location=location, symbol=symbol, color=color, name=name, ai_cls=ai_cls) 
    
    def die(self) -> None:
        super().die()
        self._ai = None


class NonPlayerCharactor(AICharactor):
    def __init__(   self,
                *,
                location: TileCoordinate | None = None,
                symbol: str = "?",
                color: Tuple[int, int, int],
                name: str = "<Unnamed>",
                fov_radius: int = 4,
                physical: PhysicalStats | None = None,
                combat: CombatStats | None = None,
                targetable: bool = True,
                ai_cls: Optional[Type[BaseAI]] = None,
                ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, targetable=targetable, ai_cls=ai_cls)


class MobCharactor(AICharactor):
    def __init__(   self,
                *,
                location: TileCoordinate | None = None,
                symbol: str = "?",
                color: Tuple[int, int, int],
                name: str = "<Unnamed>",
                fov_radius: int = 4,
                physical: PhysicalStats | None = None,
                combat: CombatStats | None = None,
                targetable: bool = True,
                ai_cls: Optional[Type[BaseAI]] = None,
                ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, targetable=targetable, ai_cls=ai_cls)
