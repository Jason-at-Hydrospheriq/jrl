#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Optional, Tuple, Type, TYPE_CHECKING

from core_components.entities.attributes import *

if TYPE_CHECKING:
    from core_components.loops import BaseLoopHandler

from core_components.loops.handlers import MobHandler
from core_components.maps.tiles import TileCoordinate


class BaseEntity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    location: TileCoordinate
    symbol: str
    color: Tuple[int, int, int]
    name: str
    is_spotted: bool = False # Is visible in another entity's FOV

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
        elif location:
            self.destination = self.location

    def move(self) -> None:
        if self.destination is not None:
            self.location = self.destination


class TargetingEntity(BaseEntity):
    target: TargetableEntity | None
    is_targeting: bool = False # Is currently targeting an entity

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
            self.target.targeter = None
            self.target.is_targeted = False

        self.target = None
        self.is_targeting = False


class TargetableEntity(BaseEntity):
    targeter: TargetingEntity | None
    is_targeted: bool = False # Is currently being targeted by an entity

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    targetable: bool=True,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.targeter = None
        self.targetable = targetable


class MortalEntity(BaseEntity):
    physical: PhysicalStats | None
    is_near_death: bool = False # Health is critically low
    is_alive: bool = True # Entity is alive
    near_death_threshold: int = 3  # Health threshold to be considered near death

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
    
    def take_damage(self, damage: int) -> None:
        if self.physical:
            self.physical.hp -= damage

            if self.physical.hp <= self.near_death_threshold:
                self.is_near_death = True

            if self.physical.hp <= 0:
                self.is_alive = False

    def die(self) -> None:
        raise NotImplementedError()


class CombatEntity(TargetingEntity):
    combat: CombatStats | None
    is_in_combat: bool = False

    melee_range_threshold: int = 1  # Distance threshold for melee range
    missile_range_threshold: int = 5  # Distance threshold for missile range
    spell_range_threshold: int = 3  # Distance threshold for spell range

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

    @property
    def is_target_in_melee_range(self) -> bool:
        distance = self.distance_to_target()
        if self.target is None:
            return False
        if self.target and distance is not None:
            return distance <= self.melee_range_threshold
        return False
    
    @property
    def is_target_in_missile_range(self) -> bool:
        distance = self.distance_to_target()
        if self.target is None:
            return False
        if self.target and distance is not None:
            return distance <= self.missile_range_threshold
        return False
    
    @property
    def is_target_in_spell_range(self) -> bool:
        distance = self.distance_to_target()
        if self.target is None:
            return False
        if self.target and distance is not None:
            return distance <= self.spell_range_threshold
        return False
    
    def acquire_target(self, target: TargetableEntity) -> None:
        if isinstance(target, CombatEntity):
            combat_status = (self.is_in_combat, target.is_in_combat)
            match combat_status: # Update combat state based on both entity and target status
                case (True, True): # Both are in combat
                    pass
                case (True, False): # Entity is in combat, target is not in combat. Target is surprised.
                    self.is_in_combat = False
                case (False, True): # Entity is not in combat, target is in combat. Entity is surprised.
                    self.is_in_combat = True
                case (False, False): # Neither are in combat
                    pass
        super().acquire_target(target)

    def distance_to_target(self) -> Optional[int]:
        if self.target is None:
            return None
        dx = self.target.location.x - self.location.x
        dy = self.target.location.y - self.location.y
        return max(abs(dx), abs(dy))  # Using Chebyshev distance for grid-based movement
    
    def attack(self) -> int:
        return self.combat.attack_power - self.target.combat.defense  # type: ignore
    

class AIEntity(BaseEntity):
    _ai: BaseHandler | None = None
    is_in_missile_range: bool = False
    is_in_melee_range: bool = False
    is_in_spell_range: bool = False

    def __init__(   self, 
                    *, 
                    location: TileCoordinate | None = None,
                    symbol: str=' ', 
                    color: Tuple[int, int, int]=(0,0,0), 
                    name: str="<Unnamed>", 
                    ai_cls: BaseHandler | None = None,
                 ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)

        if ai_cls:
            self._ai = ai_cls

    @property
    def ai(self) -> BaseHandler | None:
        return self._ai
    

class SightedEntity(BaseEntity):
    fov_radius: int
    is_spotting: bool = False

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
                    combat: CombatStats | None = None
                    ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name)
        self.fov_radius = fov_radius
        self.physical = physical
        self.combat = combat
        self.targetable = True

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
                ) -> None:
    
        super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat)


class AICharactor(Charactor, AIEntity):
    path: List[TileCoordinate] = []
    
    def __init__(   self,
                    *,
                    location: TileCoordinate | None = None,
                    symbol: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4,
                    physical: PhysicalStats | None = None,
                    combat: CombatStats | None = None,
                    ai_cls:BaseHandler | None = None,
                    ) -> None:
        
        Charactor.__init__(self, location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat)
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
                ai_cls: BaseHandler | None = None,
                ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, ai_cls=ai_cls)


class MobCharactor(AICharactor):
    def __init__(   self,
                *,
                location: TileCoordinate | None = None,
                symbol: str = "?",
                color: Tuple[int, int, int],
                name: str = "<Unnamed>",
                fov_radius: int = 4,
                physical: PhysicalStats | None = None,
                combat: CombatStats | None = None
                ) -> None:
        
        super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat)
        self._ai = MobHandler(self)