#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from turtle import color
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
from core_components.entities.base import BaseGameSubState, BaseGameEntity


class TargetedSubState(BaseGameSubState):
    _state_bits = ('is_target',)
    _states = ({'name':'targeted', 'on_enter': ['update']}, 
                 {'name':'not_targeted', 'on_enter': ['update']},
                 {'name':'unknown', 'on_enter': ['update']},)
    _transitions = (
            {'trigger':'update', 'source':['not_targeted', 'unknown'], 'dest':'targeted', 'conditions':['is_on_map', 'is_target']},
            {'trigger':'update', 'source':['targeted', 'unknown'], 'dest':'not_targeted', 'conditions':['is_on_map', 'is_not_target']},
            {'trigger':'update', 'source':['targeted', 'not_targeted'], 'dest':'unknown', 'conditions':['is_not_on_map']},
        )
    _initial_state = 'not_targeted'
    
    def set_bits(self) -> None:
        self.store.state_vector['is_target'] = self.store.targeter is not None  # type: ignore

    def is_target(self) -> bool:
        return self.store.state_vector['is_target']  # type: ignore

    def is_not_target(self) -> bool:
        return not self.store.state_vector['is_target']  # type: ignore


class TargetingSubState(BaseGameSubState):
    threat_level_threshold: int = 40

    _state_bits = ('target_in_fov', 'target_is_hostile', 'has_target')
    _states = ({'name':'stopped', 'on_enter':['update']},
                {'name':'idle', 'on_enter':['update']},
                {'name':'searching', 'on_enter':['update']}, 
                {'name':'tracking', 'on_enter':['update']},
                {'name':'targeting', 'on_enter':['update']},
                {'name':'unknown', 'on_enter':['update']},)
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'searching', 'tracking', 'targeting'], 'dest':'idle', 'conditions':['is_on_map', 'has_no_target']},
            {'trigger':'update', 'source':['unknown', 'idle', 'tracking', 'targeting'], 'dest':'searching', 'conditions':['is_on_map', 'has_target', 'has_no_visible_target', 'has_no_hostile_target']},
            {'trigger':'update', 'source':['idle', 'searching', 'targeting'], 'dest':'tracking', 'conditions':['is_on_map', 'has_target', 'has_visible_target', 'has_no_hostile_target',]},
            {'trigger':'update', 'source':['idle', 'searching', 'tracking'], 'dest':'targeting', 'conditions':['is_on_map', 'has_target', 'has_visible_target', 'has_hostile_target']},
            {'trigger':'update', 'source':['idle', 'searching', 'tracking', 'targeting'], 'dest':'unknown', 'conditions':['is_not_on_map']},
            )
    _initial_state = 'idle'

    def set_bits(self) -> None: # Interprets store data to set state bits
        self.store.state_vector['target_in_fov'] = self.store.target_in_fov  # type: ignore
        self.store.state_vector['target_is_hostile'] = self.store.threat_level > self.threat_level_threshold # type: ignore
        self.store.state_vector['has_target'] = self.store.target is not None  # type: ignore
    
    # All substates must have the primary state bit methods
    def has_target(self) -> bool:
        return self.store.state_vector['has_target']  # type: ignore
    
    def has_no_target(self) -> bool:
        return not self.store.state_vector['has_target']  # type: ignore
    
    def has_visible_target(self) -> bool:
        return self.store.state_vector['target_in_fov']  # type: ignore
    
    def has_no_visible_target(self) -> bool:
        return not self.store.state_vector['target_in_fov']  # type: ignore
    
    def has_hostile_target(self) -> bool:
        return self.store.state_vector['target_is_hostile']  # type: ignore
    
    def has_no_hostile_target(self) -> bool:
        return not self.store.state_vector['target_is_hostile']  # type: ignore


class CombatSubState(BaseGameSubState):
   
    _state_bits = ('in_melee_range',) # , 'in_missile_range', 'in_spell_range')
    _states = ({'name':'engaged', 'on_enter':['update']},
                         {'name': 'melee_ready', 'on_enter':['update']},
                         {'name':'disengaged', 'on_enter':['update']},
                            {'name':'idle', 'on_enter':['update']},
                         {'name':'unknown', 'on_enter':['update']})
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'idle', 'disengaged', 'melee_ready'], 'dest':'engaged', 'conditions':['is_on_map', 'is_targeting', 'is_out_of_range']},
            {'trigger':'update', 'source':['unknown', 'idle', 'engaged', 'disengaged'], 'dest':'melee_ready', 'conditions':['is_on_map', 'is_targeting', 'is_in_melee_range']},
            {'trigger':'update', 'source':['unknown', 'disengaged', 'engaged', 'melee_ready'], 'dest':'idle', 'conditions':['is_on_map', 'is_not_targeting', 'is_out_of_range']},
            {'trigger':'update', 'source':['unknown', 'idle', 'engaged', 'melee_ready'], 'dest':'disengaged', 'conditions':['is_on_map', 'is_not_targeting', 'is_in_melee_range']},
            {'trigger':'update', 'source':['idle', 'engaged', 'disengaged', 'melee_ready'], 'dest':'unknown', 'conditions':['is_not_on_map']},)
    
    _initial_state = 'disengaged'

    def set_bits(self) -> None: # Interprets distance to target and targeting status into state bits
        self.store.state_vector['in_melee_range'] = self.store.distance_to_target <= 1  # type: ignore
    
    def is_in_melee_range(self) -> bool:
        return self.store.state_vector['in_melee_range']  # type: ignore
    
    def is_out_of_range(self) -> bool:
        return not (self.is_in_melee_range()) # or self.is_in_missile_range() or self.is_in_spell_range())
    
    def is_targeting(self) -> bool:
        return self.store.focus.is_targeting()  # type: ignore 
    
    def is_not_targeting(self) -> bool:
        return not self.store.focus.is_targeting()  # type: ignore
  
    
class TargetableEntity(BaseGameEntity):
    targeter: StatefulObject | None = None
    perception: TargetedSubState
    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("perception", TargetedSubState),
    )
    
    def __init__(self,
                 store: GameStore | None = None,
                 *,
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__(store=store, location=location, name=name, symbol=symbol, color=color)


class TargetingEntity(BaseGameEntity):
    target: BaseGameEntity | None = None
    fov_radius: int = 0
    focus: TargetingSubState
    _visible = False
    _threat_level: int = 0
    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("focus", TargetingSubState),
    )

    def __init__(self,
                 store: GameStore | None = None,
                 *,
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__(store=store, location=location, name=name, symbol=symbol, color=color)

    @property
    def threat_level(self) -> int:
        return self._threat_level
    
    @property
    def target_in_fov(self) -> bool:
        if self.target:
            return self.target._visible # type: ignore
        return False
    
    def assess_target(self, target: BaseGameEntity) -> None:
        pass  # Placeholder for threat assessment logic
       
    def set_target(self, *, target: BaseGameEntity) -> None:
        self.target = target  # type: ignore            

    
class CombatEntity(TargetableEntity, TargetingEntity):
    combat: CombatSubState
    attack_power: int = 10
    defense_power: int = 5

    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("combat", CombatSubState),
        ("perception", TargetedSubState),
        ("focus", TargetingSubState),
    )
    
    @property
    def distance_to_target(self) -> int:

        if self.target and self.location and self.target.location is not None:
            dx = self.target.location.x - self.location.x
            dy = self.target.location.y - self.location.y
            return max(abs(dx), abs(dy))  # Using Chebyshev distance for grid-based movement
        
        return 9999
    
    @property
    def attack(self) -> int:
        damage = 0
        if self.combat.is_melee_ready(): #type: ignore
            damage = self.attack_power - self.target.defense  # type: ignore
            damage = max(0, damage)
    
        return damage
    
    @property
    def defense(self) -> int:
        return self.defense_power


class MobileEntity(BaseGameEntity):
    speed: int | None = 0
    destination: TileCoordinate | None = None

    def move(self) -> None:
        if self.destination is not None:
            self.location = self.destination


class Charactor(MobileEntity, CombatEntity):

    def __init__(   self,
                    *,
                    store: GameStore | None = None,
                    location: TileCoordinate | None = None,
                    symbol: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    fov_radius: int = 4
                    ) -> None:
        
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)
        
        self.blocks_movement = True
        self.fov_radius = fov_radius
        self.targetable = True
        
    def die(self) -> None:
        self.blocks_movement = False
        self.name = f"remains of {self.name}"
        self.symbol = "%"
        self.color = (191, 0, 0)


class PlayerCharactor(Charactor):
    def __init__(   self,
                *,
                store: GameStore | None = None,
                location: TileCoordinate | None = None,
                name: str = "<Unnamed>",
                symbol: str = '@',
                color: Tuple[int, int, int]=(255, 255, 255),

                ) -> None:

        fov_radius = 6

        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius)


class AICharactor(Charactor):
    path: List[TileCoordinate] = []
    _ai: BaseLoopHandler | None = None
    
    def __init__(   self,
                    *,
                store: GameStore | None = None,
                location: TileCoordinate | None = None,
                name: str = "<Unnamed>",
                symbol: str = '?',
                color: Tuple[int, int, int]=(255, 255, 255),
                ai_cls: BaseLoopHandler | None = None,
                 ) -> None:
        
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

        if ai_cls:
            self._ai = ai_cls

    @property
    def ai(self) -> BaseLoopHandler | None:
        return self._ai


    def die(self) -> None:
        super().die()
        self._ai = None


class MobCharactor(AICharactor):
    def __init__(   self,
                    *,
                store: GameStore | None = None,
                location: TileCoordinate | None = None,
                name: str = "<Unnamed>",
                symbol: str = '?',
                color: Tuple[int, int, int]=(255, 255, 255),
                 ) -> None:
        
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)
        self._ai = MobHandler(self)


# class BaseGameEntity:
#     """
#     store: StatefulObject | None
#     machine: Machine
#     location: TileCoordinate | None

#     name: str
#     symbol: str
#     color: Tuple[int, int, int] # Do this like the maps. Numpy datatypes mapped to state.

#     def __init__(self,
#                  store: GameStore,
#                  *,                 
#                  location: Tuple[int, int] | TileCoordinate | None = None,
#                  name: str="<Unnamed>", 
#                  symbol: str=' ', 
#                  color: Tuple[int, int, int]=(0,0,0)) -> None:
            
#         self.store = store
#         parent_map_size = store.map.grid.size

#         if isinstance(location, tuple):
#             self.location = TileCoordinate.from_tuple(location, parent_map_size=parent_map_size)
#         else:
#             self.location = location

#         self.symbol = symbol
#         self.color = color
#         self.name = name

#         states = ['noticed', 'unnoticed']
#         transitions = [
#                         {'trigger': 'spot', 'source': 'unnoticed', 'dest': 'noticed'},
#                         {'trigger': 'unspot', 'source': 'noticed', 'dest': 'unnoticed'}
#                             ]
#         self.machine = Machine(model=self, states=states, transitions=transitions, initial='unnoticed')


# class BaseTargetingEntity(BaseGameEntity):
#     target: GameEntity | None = None
#     target_color: Tuple[int, int, int] | None = None

#     def __init__(self,
#                  store: GameStore,
#                  *,                 
#                  location: Tuple[int, int] | TileCoordinate | None = None,
#                  name: str="<Unnamed>", 
#                  symbol: str=' ', 
#                  color: Tuple[int, int, int]=(0,0,0)) -> None:
        
#         super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)
        
#         self.machine.add_states(['targeting', 'not_targeting'])
#         self.machine.add_transition('acquire_target', 'not_targeting', 'targeting')
#         self.machine.add_transition('clear_target', 'targeting', 'not_targeting')

#     def acquire_target(self, target: BaseTargetableEntity) -> None:
#         if self.is_targeting:
#             self.clear_target()
   
#         self.target_color = target.color  # Store original color
#         target.targeter = self
#         target.mark() # type: ignore
#         self.target = target
#         self.target.color = (255, 0, 0)  # Change color to indicate targeting

#     def clear_target(self) -> None:
#         if isinstance(self.target, BaseTargetableEntity):
#             if self.target and self.target_color is not None:
#                 self.target.color = self.target_color  # Restore original color
#                 self.target.targeter = None
#                 self.target.unmark() # type: ignore 

#         self.target = None
#         self.is_targeting = False


# class BaseTargetableEntity(BaseGameEntity):
#     targeter: BaseTargetingEntity | None = None

#     def __init__(self,
#                  store: GameStore,
#                  *,                 
#                  location: Tuple[int, int] | TileCoordinate | None = None,
#                  name: str="<Unnamed>", 
#                  symbol: str=' ', 
#                  color: Tuple[int, int, int]=(0,0,0)) -> None:
        
#         super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

#         self.machine.add_states(['targeted', 'not_targeted'])
#         self.machine.add_transition('mark', 'not_targeted', 'targeted')
#         self.machine.add_transition('unmark', 'targeted', 'not_targeted')


# class BaseMortalEntity(BaseGameEntity):
#     physical: PhysicalStats | None = None
#     is_near_death: bool = False # Health is critically low
#     is_alive: bool = True # Entity is alive
#     near_death_threshold: int = 3  # Health threshold to be considered near death

#     def __init__(self,
#                  store: GameStore,
#                  *,                 
#                  location: Tuple[int, int] | TileCoordinate | None = None,
#                  name: str="<Unnamed>", 
#                  symbol: str=' ', 
#                  color: Tuple[int, int, int]=(0,0,0)) -> None:
        
#         super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

#         self.machine.add_states(['alive', 'dead', 'near_death', 'healthy'])
#         self.machine.add_transition('take_damage', 'alive', 'dead', conditions=['is_dead'])
#         self.machine.add_transition('take_damage', 'alive', 'near_death', conditions=['is_near_death'])
#         self.machine.add_transition('take_damage', 'alive', 'healthy', unless=['is_near_death', 'is_dead']
#         )
    
#     def take_damage(self, damage: int) -> None:
#         if self.physical:
#             self.physical.hp -= damage

#             if self.physical.hp <= self.near_death_threshold:
#                 self.is_near_death = True

#             if self.physical.hp <= 0:
#                 self.is_alive = False

#     def die(self) -> None:
#         raise NotImplementedError()


# class CombatEntity(BaseTargetingEntity):
#     combat: CombatStats | None
#     is_in_combat: bool = False

#     melee_range_threshold: int = 1  # Distance threshold for melee range
#     missile_range_threshold: int = 5  # Distance threshold for missile range
#     spell_range_threshold: int = 3  # Distance threshold for spell range

#     def __init__(   self, 
#                     *, 
#                     location: TileCoordinate | None = None,
#                     symbol: str=' ', 
#                     color: Tuple[int, int, int]=(0,0,0), 
#                     name: str="<Unnamed>", 
#                     combat: CombatStats | None = None,
#                  ) -> None:
        
#         super().__init__(location=location, symbol=symbol, color=color, name=name)
#         self.combat = combat

#     @property
#     def is_target_in_melee_range(self) -> bool:
#         distance = self.distance_to_target()
#         if self.target is None:
#             return False
#         if self.target and distance is not None:
#             return distance <= self.melee_range_threshold
#         return False
    
#     @property
#     def is_target_in_missile_range(self) -> bool:
#         distance = self.distance_to_target()
#         if self.target is None:
#             return False
#         if self.target and distance is not None:
#             return distance <= self.missile_range_threshold
#         return False
    
#     @property
#     def is_target_in_spell_range(self) -> bool:
#         distance = self.distance_to_target()
#         if self.target is None:
#             return False
#         if self.target and distance is not None:
#             return distance <= self.spell_range_threshold
#         return False
    
#     def acquire_target(self, target: BaseTargetableEntity) -> None:
#         if isinstance(target, CombatEntity):
#             combat_status = (self.is_in_combat, target.is_in_combat)
#             match combat_status: # Update combat state based on both entity and target status
#                 case (True, True): # Both are in combat
#                     pass
#                 case (True, False): # Entity is in combat, target is not in combat. Target is surprised.
#                     self.is_in_combat = False
#                 case (False, True): # Entity is not in combat, target is in combat. Entity is surprised.
#                     self.is_in_combat = True
#                 case (False, False): # Neither are in combat
#                     pass
#         super().acquire_target(target)

#     def distance_to_target(self) -> Optional[int]:
#         if self.target is None:
#             return None
#         dx = self.target.location.x - self.location.x
#         dy = self.target.location.y - self.location.y
#         return max(abs(dx), abs(dy))  # Using Chebyshev distance for grid-based movement
    
#     def attack(self) -> int:
#         return self.combat.attack_power - self.target.combat.defense  # type: ignore
    

# class AIEntity(BaseGameEntity):
#     _ai: BaseHandler | None = None
#     is_in_missile_range: bool = False
#     is_in_melee_range: bool = False
#     is_in_spell_range: bool = False

#     def __init__(   self, 
#                     *, 
#                     location: TileCoordinate | None = None,
#                     symbol: str=' ', 
#                     color: Tuple[int, int, int]=(0,0,0), 
#                     name: str="<Unnamed>", 
#                     ai_cls: BaseHandler | None = None,
#                  ) -> None:
        
#         super().__init__(location=location, symbol=symbol, color=color, name=name)

#         if ai_cls:
#             self._ai = ai_cls

#     @property
#     def ai(self) -> BaseHandler | None:
#         return self._ai
    




# class AICharactor(Charactor, AIEntity):
#     path: List[TileCoordinate] = []
    
#     def __init__(   self,
#                     *,
#                     location: TileCoordinate | None = None,
#                     symbol: str = "?",
#                     color: Tuple[int, int, int],
#                     name: str = "<Unnamed>",
#                     fov_radius: int = 4,
#                     physical: PhysicalStats | None = None,
#                     combat: CombatStats | None = None,
#                     ai_cls:BaseHandler | None = None,
#                     ) -> None:
        
#         Charactor.__init__(self, location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat)
#         AIEntity.__init__(self, location=location, symbol=symbol, color=color, name=name, ai_cls=ai_cls) 


#     def die(self) -> None:
#         super().die()
#         self._ai = None


# class NonPlayerCharactor(AICharactor):
#     def __init__(   self,
#                 *,
#                 location: TileCoordinate | None = None,
#                 symbol: str = "?",
#                 color: Tuple[int, int, int],
#                 name: str = "<Unnamed>",
#                 fov_radius: int = 4,
#                 physical: PhysicalStats | None = None,
#                 combat: CombatStats | None = None,
#                 ai_cls: BaseHandler | None = None,
#                 ) -> None:
        
#         super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat, ai_cls=ai_cls)


# class MobCharactor(AICharactor):
#     def __init__(   self,
#                 *,
#                 location: TileCoordinate | None = None,
#                 symbol: str = "?",
#                 color: Tuple[int, int, int],
#                 name: str = "<Unnamed>",
#                 fov_radius: int = 4,
#                 physical: PhysicalStats | None = None,
#                 combat: CombatStats | None = None
#                 ) -> None:
        
#         super().__init__(location=location, symbol=symbol, color=color, name=name, fov_radius=fov_radius, physical=physical, combat=combat)
#         self._ai = MobHandler(self)