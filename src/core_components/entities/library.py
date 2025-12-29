#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Optional, Tuple, Type, TYPE_CHECKING
from transitions import Machine
from type_protocols import *

from core_components.entities.attributes import *

if TYPE_CHECKING:
    from core_components.loops import BaseLoopHandler
    from core_components.store import GameStore

from core_components.entities.types import *
from core_components.loops.handlers import MobHandler
from core_components.maps.tiles import TileCoordinate


class BaseGameEntity:
    """
    A generic object to represent players, enemies, items, etc.

    Duck Types: StatefulObject, StateStoreObject, GameEntity
    """
    store: StatefulObject | None
    machine: Machine
    location: TileCoordinate | None

    name: str
    symbol: str
    color: Tuple[int, int, int] # Do this like the maps. Numpy datatypes mapped to state.

    def __init__(self,
                 store: GameStore,
                 *,                 
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
            
        self.store = store
        parent_map_size = store.map.grid.size

        if isinstance(location, tuple):
            self.location = TileCoordinate.from_tuple(location, parent_map_size=parent_map_size)
        else:
            self.location = location

        self.symbol = symbol
        self.color = color
        self.name = name

        states = ['noticed', 'unnoticed']
        transitions = [
                        {'trigger': 'spot', 'source': 'unnoticed', 'dest': 'noticed'},
                        {'trigger': 'unspot', 'source': 'noticed', 'dest': 'unnoticed'}
                            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='unnoticed')


class MixInBlockingEntity(BaseGameEntity):
    blocks_movement: bool = True


class MixinBaseMobileEntity(BaseGameEntity):
    speed: int | None = 0
    destination: TileCoordinate | None = None

    def move(self) -> None:
        if self.destination is not None:
            self.location = self.destination


class BaseTargetingEntity(BaseGameEntity):
    target: GameEntity | None = None
    target_color: Tuple[int, int, int] | None = None

    def __init__(self,
                 store: GameStore,
                 *,                 
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)
        
        self.machine.add_states(['targeting', 'not_targeting'])
        self.machine.add_transition('acquire_target', 'not_targeting', 'targeting')
        self.machine.add_transition('clear_target', 'targeting', 'not_targeting')

    def acquire_target(self, target: BaseTargetableEntity) -> None:
        if self.is_targeting:
            self.clear_target()
   
        self.target_color = target.color  # Store original color
        target.targeter = self
        target.mark() # type: ignore
        self.target = target
        self.target.color = (255, 0, 0)  # Change color to indicate targeting

    def clear_target(self) -> None:
        if isinstance(self.target, BaseTargetableEntity):
            if self.target and self.target_color is not None:
                self.target.color = self.target_color  # Restore original color
                self.target.targeter = None
                self.target.unmark() # type: ignore 

        self.target = None
        self.is_targeting = False


class BaseTargetableEntity(BaseGameEntity):
    targeter: BaseTargetingEntity | None = None

    def __init__(self,
                 store: GameStore,
                 *,                 
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

        self.machine.add_states(['targeted', 'not_targeted'])
        self.machine.add_transition('mark', 'not_targeted', 'targeted')
        self.machine.add_transition('unmark', 'targeted', 'not_targeted')


class BaseMortalEntity(BaseGameEntity):
    physical: PhysicalStats | None = None
    is_near_death: bool = False # Health is critically low
    is_alive: bool = True # Entity is alive
    near_death_threshold: int = 3  # Health threshold to be considered near death

    def __init__(self,
                 store: GameStore,
                 *,                 
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

        self.machine.add_states(['alive', 'dead', 'near_death', 'healthy'])
        self.machine.add_transition('take_damage', 'alive', 'dead', conditions=['is_dead'])
        self.machine.add_transition('take_damage', 'alive', 'near_death', conditions=['is_near_death'])
        self.machine.add_transition('take_damage', 'alive', 'healthy', unless=['is_near_death', 'is_dead']
        )
    
    def take_damage(self, damage: int) -> None:
        if self.physical:
            self.physical.hp -= damage

            if self.physical.hp <= self.near_death_threshold:
                self.is_near_death = True

            if self.physical.hp <= 0:
                self.is_alive = False

    def die(self) -> None:
        raise NotImplementedError()


class CombatEntity(BaseTargetingEntity):
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
    
    def acquire_target(self, target: BaseTargetableEntity) -> None:
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
    

class AIEntity(BaseGameEntity):
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
    

class SightedEntity(BaseGameEntity):
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
    

class Charactor(SightedEntity, CombatEntity, BaseMortalEntity, BaseTargetableEntity, BaseTargetingEntity, MixinBaseMobileEntity, MixInBlockingEntity):
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