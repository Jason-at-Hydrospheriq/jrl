#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from turtle import color
from typing import List, Optional, Tuple, Type, TYPE_CHECKING
from transitions import Machine
from type_protocols import *
import tcod as libtcodpy
from tcod.map import compute_fov

from core_components.entities.attributes import *

if TYPE_CHECKING:
    from core_components.loops import BaseLoopHandler
    from core_components.store import GameStore

from core_components.entities.types import *
from core_components.loops.handlers import MobHandler
from core_components.maps.tiles import TileCoordinate
from core_components.entities.base import BaseGameSubState, BaseGameEntity


class TargetedSubState(BaseGameSubState):
    """The TargetedSubState is a class that defines and runs the 'perception' state machine for a Game Entity.
    This state machine tracks whether an Entity is targeted by another entity. It manages the 'is_target' state
    bit in the state_vector."""

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
    """The TargetingSubState is a class that defines and runs the 'focus' state machine for a Game Entity.
    This state machine tracks whether an Entity has a target and the status of that target. It manages the 
    'target_in_fov', 'target_is_hostile', and 'has_target' state bits in the state_vector."""
    
    threat_level_threshold: int = 60

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
    """The CombatSubState is a class that defines and runs the 'combat' state machine for a Game Entity.
    This state machine tracks whether an Entity is engaged in combat, attacking, disengaged, or peaceful.
    It manages the 'in_melee_range' state bit in the state_vector."""

    range_threshold: int = 1  # Distance threshold for combat range
    combat_type: str = "melee"  # Type of combat: 'melee', 'missile', 'spell'

    _state_bits = (f'in_{combat_type}_range',) 
    _states = ( {'name': 'engaged', 'on_enter':['update']},
                {'name': 'fighting', 'on_enter':['update']},
                {'name': 'disengaged', 'on_enter':['update']},
                {'name': 'peaceful', 'on_enter':['update']},
                {'name': 'unknown', 'on_enter':['update']})
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'peaceful', 'disengaged', 'fighting'], 'dest':'engaged', 'conditions':['is_on_map', 'is_targeting', 'is_out_of_range']},
            {'trigger':'update', 'source':['unknown', 'peaceful', 'engaged', 'disengaged'], 'dest':'fighting', 'conditions':['is_on_map', 'is_targeting', 'is_in_range']},
            {'trigger':'update', 'source':['unknown', 'disengaged', 'engaged', 'fighting'], 'dest':'peaceful', 'conditions':['is_on_map', 'is_not_targeting', 'is_out_of_range']},
            {'trigger':'update', 'source':['unknown', 'peaceful', 'engaged', 'fighting'], 'dest':'disengaged', 'conditions':['is_on_map', 'is_not_targeting', 'is_in_range']},
            {'trigger':'update', 'source':['peaceful', 'engaged', 'disengaged', 'fighting'], 'dest':'unknown', 'conditions':['is_not_on_map']},)
    _initial_state = 'disengaged'

    def set_bits(self) -> None: # Interprets distance to target and targeting status into state bits
        self.store.state_vector[f'in_{self.combat_type}_range'] = self.store.distance_to_target <= self.range_threshold  # type: ignore
    
    def is_in_range(self) -> bool:
        return self.store.state_vector[f'in_{self.combat_type}_range']  # type: ignore
    
    def is_out_of_range(self) -> bool:
        return not (self.is_in_range()) # or self.is_in_missile_range() or self.is_in_spell_range())
    
    def is_targeting(self) -> bool:
        return self.store.focus.is_targeting()  # type: ignore 
    
    def is_not_targeting(self) -> bool:
        return not self.store.focus.is_targeting()  # type: ignore
  
    
class TargetableEntity(BaseGameEntity):
    """A Targetable Entity is any game object that can become the focus of a TargetingEntity.
    It has a 'perception' substate that is an instance of TargetedSubState that manages its targeted states.
    A Targetable Entity can be damaged. It has a 'take_damage' method to reduce its hit points when damaged."""

    targeter: StatefulObject | None = None
    perception: TargetedSubState
    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("perception", TargetedSubState))
    
    def __init__(self,
                 store: GameStore | None = None,
                 *,
                 location: Tuple[int, int] | TileCoordinate | None = None,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__(store=store, location=location, name=name, symbol=symbol, color=color)

    def take_damage(self, damage: int) -> None:
        if self.hp:
            self.hp -= damage
            self.hp = max(self.hp, 0)


class TargetingEntity(BaseGameEntity):
    """A Targeting Entity is any game object that can focus on a TargetableEntity. It has a 'focus' substate 
    that is an instance of TargetingSubState that manages its targeting states. A Targeting Entity can assess 
    threat levels and has a 'threat_level' property to represent its current threat assessment."""

    target: BaseGameEntity | None = None
    focus: TargetingSubState
    _fov_radius: int = 6
    _visible_tiles: np.ndarray | None = None
    _threat_level: int = 10
    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("focus", TargetingSubState))

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
    
    @threat_level.setter
    def threat_level(self, value: int) -> None:
        self._threat_level = value

    @property
    def fov_radius(self) -> int:
        return self._fov_radius
    
    @fov_radius.setter
    def fov_radius(self, value: int) -> None:
        self._fov_radius = value

    @property
    def target_in_fov(self) -> bool:
            if self.store:
                blocking_tiles = self.store.map.active.blocks_vision if self.store.map and self.store.map.active else None # type: ignore
               
                # UPDATE ENTITY FOV
                if blocking_tiles and self.location is not None:
                    self._visible_tiles = compute_fov( ~blocking_tiles, (self.location.x, self.location.y), radius=self.fov_radius, algorithm=libtcodpy.FOV_RESTRICTIVE)

                    if self.target and self.target.location is not None:
                        tx, ty = self.target.location.x, self.target.location.y
                        if self._visible_tiles[tx, ty]:
                            return True

                    else:
                        visible_targets = [entity for entity in self.store.live_entities if self._visible_tiles[entity.location.x, entity.location.y]]  # type: ignore
                        distances = []

                        if visible_targets:
                            for entity in visible_targets:
                                self.target = entity
                                distance = self.distance_to_target
                                distances.append((distance, entity))
                        
                        if distances:
                            distances.sort(key=lambda x: x[0])
                            self.target = distances[0][1]
                            return True
                        else:
                            self.target = None
                            return False
            return False

    @property
    def distance_to_target(self) -> int:

        if self.target and self.location and self.target.location is not None:
            dx = self.target.location.x - self.location.x
            dy = self.target.location.y - self.location.y
            return max(abs(dx), abs(dy))  # Using Chebyshev distance for grid-based movement
        
        return 9999
      
    def assess_threat(self) -> None:
        if self.distance_to_target <= 8:
            self.threat_level += 10
        if self.distance_to_target <= 5:
            self.threat_level += 10
        if self.distance_to_target <= 2:
            self.threat_level += 10
        if self.distance_to_target == 1:
            self.threat_level += 10
        if self.target:
            if self.target.target is self: # type: ignore
                self.threat_level = self.threat_level * 2
    
    def update(self) -> None:
        self.assess_threat()
        super().update()


class CombatEntity(TargetableEntity, TargetingEntity):
    """A Combat Entity is any game object that can both target and be targeted by other entities and deal damage.
    It has both 'focus' and 'perception' substates that are instances of TargetingSubState and TargetedSubState. 
    It has a 'combat' substate that is an instance of CombatSubState to manage its combat states. A Combat Entity has
    'attack' and 'defense' properties to calculate damage dealt and mitigated during combat."""

    combat: CombatSubState
    _attack_power: int = 10
    _defense_power: int = 5

    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("perception", TargetedSubState),
        ("focus", TargetingSubState),
        ("combat", CombatSubState),
    )
    
    @property
    def attack_power(self) -> int:
        return self._attack_power
    
    @attack_power.setter
    def attack_power(self, value: int) -> None:
        self._attack_power = value
   
    @property
    def defense_power(self) -> int:
        return self._defense_power

    @defense_power.setter
    def defense_power(self, value: int) -> None:
        self._defense_power = value

    @property
    def attack(self) -> int:
        damage_delivered = 0
        if self.combat.is_attacking(): #type: ignore
            damage_delivered = self._attack_power
    
        return damage_delivered
    
    @property
    def defend(self) -> int:
        damage_mitigated = 0
        if self.combat.is_melee_ready(): #type: ignore
            damage_mitigated = self._defense_power
        if self.combat.is_not_melee_ready(): #type: ignore
            damage_mitigated = self._defense_power // 2

        return damage_mitigated


class MobileEntity(BaseGameEntity):
    speed: int | None = 0
    destination: TileCoordinate | None = None

    def move(self) -> None:
        if self.destination is not None:
            self.location = self.destination


class Character(MobileEntity, CombatEntity):

    def __init__(   self,
                    *,
                    store: GameStore | None = None,
                    location: TileCoordinate | None = None,
                    symbol: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    ) -> None:
        
        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)
        
        self.blocks_movement = True
        self.takes_damage = True
        
    def die(self) -> None:
        self.blocks_movement = False
        self.takes_damage = False
        self.name = f"remains of {self.name}"
        self.symbol = "%"
        self.color = (191, 0, 0)


class PlayerCharacter(Character):
    def __init__(   self,
                *,
                store: GameStore | None = None,
                location: TileCoordinate | None = None,
                name: str = "<Unnamed>",
                symbol: str = '@',
                color: Tuple[int, int, int]=(255, 255, 255),

                ) -> None:

        self.fov_radius = 6

        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)


class AICharacter(Character):
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


class MobCharacter(AICharacter):
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

