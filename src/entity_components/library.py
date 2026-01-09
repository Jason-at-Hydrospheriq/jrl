#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import numpy as np
from tcod import libtcodpy
from tcod.map import compute_fov

from entity_components.attributes import *

if TYPE_CHECKING:
    from engine_components.store import GameStore

from atlas_components.tiles import TileCoordinate
from entity_components.base import BaseGameSubState, BaseGameEntity, action_locked
from display_components.graphics.colors import enemy_die
class CollisionSubState(BaseGameSubState):
    """The CollisionSubState is a class that defines and runs the 'collision' state machine for a Game Entity.
    This state machine tracks whether an Entity is colliding with another object or not. It manages the 
    'entity_collision', 'terrain_collision', 'boundary_collision' state bits in the state_vector."""

    _state_bits = ('in_entity_collision', 'in_terrain_collision', 'in_boundary_collision')
    _states = ( {'name':'colliding_with_entity', 'on_enter': ['update']},
                {'name':'colliding_with_terrain', 'on_enter': ['update']}, 
                {'name':'colliding_with_boundary', 'on_enter': ['update']}, 
                {'name':'not_colliding', 'on_enter': ['update']},
                {'name':'unknown', 'on_enter': ['update']},)
    _transitions = (
            {'trigger':'update', 'source':['not_colliding', 'unknown', 'colliding_with_terrain', 'colliding_with_boundary'], 'dest':'colliding_with_entity', 'conditions':['is_on_map', 'is_colliding_with_entity']},
            {'trigger':'update', 'source':['not_colliding', 'unknown', 'colliding_with_entity'], 'dest':'colliding_with_terrain', 'conditions':['is_on_map', 'is_colliding_with_terrain']},
            {'trigger':'update', 'source':['not_colliding', 'unknown', 'colliding_with_entity'], 'dest':'colliding_with_boundary', 'conditions':['is_on_map', 'is_colliding_with_boundary']},
            {'trigger':'update', 'source':['unknown', 'colliding_with_entity', 'colliding_with_terrain', 'colliding_with_boundary'], 'dest':'not_colliding', 'conditions':['is_on_map', 'is_not_colliding']},
            {'trigger':'update', 'source':['not_colliding', 'colliding_with_entity', 'colliding_with_terrain', 'colliding_with_boundary'], 'dest':'unknown', 'conditions':['is_not_on_map']})
    _initial_state = 'not_colliding'
    
    def set_bits(self) -> None:
        self.store.state_vector['in_entity_collision'] = self.store.destination_is_blocking_entity  # type: ignore
        self.store.state_vector['in_terrain_collision'] = self.store.destination_is_blocking_terrain  # type: ignore
        self.store.state_vector['in_boundary_collision'] = self.store.destination_is_map_boundary  # type: ignore
        
    def is_colliding_with_entity(self) -> bool:
        return self.store.state_vector['in_entity_collision']  # type: ignore

    def is_colliding_with_terrain(self) -> bool:
        return self.store.state_vector['in_terrain_collision']  # type: ignore

    def is_colliding_with_boundary(self) -> bool:
        return self.store.state_vector['in_boundary_collision']  # type: ignore

    def is_not_colliding(self) -> bool:
        return not (self.store.state_vector['in_entity_collision'] or  # type: ignore
                    self.store.state_vector['in_terrain_collision'] or  # type: ignore
                    self.store.state_vector['in_boundary_collision'])  # type: ignore
    
    def is_colliding(self) -> bool:
        return not self.is_not_colliding()


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

    state_changed: bool = False
    _state_bits = ('target_in_fov', 'target_is_hostile', 'has_target')
    _states = ({'name':'stopped', 'on_enter':['update']},
                {'name':'idle', 'on_enter':['update']},
                {'name':'searching', 'on_enter':['update']}, 
                {'name':'tracking', 'on_enter':['state_transition']},
                {'name':'targeting', 'on_enter':['update']},
                {'name':'unknown', 'on_enter':['update']},)
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'searching', 'tracking', 'targeting'], 'dest':'idle', 'conditions':['is_on_map', 'has_no_target']},
            {'trigger':'update', 'source':['unknown', 'idle', 'tracking', 'targeting'], 'dest':'searching', 'conditions':['is_on_map', 'has_target', 'has_no_visible_target', 'has_no_hostile_target']},
            {'trigger':'update', 'source':['unknown', 'idle', 'searching', 'targeting'], 'dest':'tracking', 'conditions':['is_on_map', 'has_target', 'has_visible_target', 'has_no_hostile_target',]},
            {'trigger':'update', 'source':['unknown', 'idle', 'searching', 'tracking'], 'dest':'targeting', 'conditions':['is_on_map', 'has_target', 'has_visible_target', 'has_hostile_target']},
            {'trigger':'update', 'source':['idle', 'searching', 'tracking', 'targeting'], 'dest':'unknown', 'conditions':['is_not_on_map']},
            )
    _initial_state = 'idle'

    def state_transition(self) -> None:
        self.state_changed = True
        self.set_bits()

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
    It manages the 'in_melee_range' state bit in the state_vector. An entity can have more than one CombatSubState
    to represent different combat types (melee, missile, spell)."""

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
  

class CharacterHealthSubState(BaseGameSubState):
    """The CharacterHealthSubState is a class that defines and runs the 'health' state machine for a Game Entity.
    This state machine tracks whether a Character is healthy, injured, critical, or dead. It manages the 
    'is_healthy', 'is_injured', 'is_critical', and 'is_dead' state bits in the state_vector."""

    _state_bits = ('is_healthy', 'is_injured', 'is_critical', 'is_dead')
    _states = ( {'name':'healthy', 'on_enter': ['update']},
                {'name':'injured', 'on_enter': ['update']}, 
                {'name':'critical', 'on_enter': ['update']}, 
                {'name':'unconscious', 'on_enter': ['update']},
                {'name':'dead', 'on_enter': ['update']},
                {'name':'unknown', 'on_enter': ['update']},)
    _transitions = (
            {'trigger':'update', 'source':['unknown', 'injured', 'critical', 'unconscious'], 'dest':'healthy', 'conditions':['is_on_map', 'is_healthy']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'critical', 'unconscious'], 'dest':'injured', 'conditions':['is_on_map', 'is_injured']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'injured', 'unconscious'], 'dest':'critical', 'conditions':['is_on_map', 'is_critical']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'injured', 'critical'], 'dest':'unconscious', 'conditions':['is_on_map', 'is_unconscious']},
            {'trigger':'update', 'source':['unknown', 'healthy', 'injured', 'critical', 'unconscious'], 'dest':'dead', 'conditions':['is_on_map', 'is_dead']},
            {'trigger':'update', 'source':['healthy', 'injured', 'critical', 'unconscious', 'dead'], 'dest':'unknown', 'conditions':['is_not_on_map']},)
    _initial_state = 'healthy'
    
    def set_bits(self) -> None:
        if self.store.hp is not None and self.store.max_hp is not None:  # type: ignore | Character can take damage when alive.
            self.store.state_vector['is_healthy'] = self.store.hp > (0.7 * self.store.max_hp) and self.store.is_alive  # type: ignore
            self.store.state_vector['is_injured'] = (0.3 * self.store.max_hp) < self.store.hp <= (0.7 * self.store.max_hp) and self.store.is_alive  # type: ignore
            self.store.state_vector['is_critical'] = 0 < self.store.hp <= (0.3 * self.store.max_hp) and self.store.is_alive  # type: ignore
            self.store.state_vector['is_unconscious'] = self.store.hp == 0 and self.store.is_alive  # type: ignore
        
        elif self.store.hp is None:  # type: ignore | Character cannot take damage when dead.
            self.store.state_vector['is_dead'] = not self.store.is_alive  # type: ignore

    def is_healthy(self) -> bool:
        return self.store.state_vector['is_healthy']  # type: ignore
    
    def is_injured(self) -> bool:
        return self.store.state_vector['is_injured']  # type: ignore
    
    def is_critical(self) -> bool:
        return self.store.state_vector['is_critical']  # type: ignore
    
    def is_unconscious(self) -> bool:
        return self.store.state_vector['is_unconscious']  # type: ignore
    
    def is_dead(self) -> bool:
        return self.store.state_vector['is_dead']  # type: ignore
    

@action_locked
class MobileEntity(BaseGameEntity):
    """A Mobile Entity is any game object that can move around the map. It has a 'collision' substate that is an
    instance of CollisionSubState that manages its collision states. A Mobile Entity can 'move' and has 'speed' and 'destination' properties
    to control its movement capabilities."""

    speed: int | None = 0
    destination: TileCoordinate | None = None
    collision: CollisionSubState
    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("collision", CollisionSubState),
    )

    @property
    def destination_is_blocking_entity(self) -> bool:
        if self.store and self.store.atlas.active and self.store.portfolio: # type: ignore Assume store is GameStore
            for entity in self.store.portfolio.live_actors: # type: ignore Assume live_actors is List[Character]
                if entity.location == self.destination and entity.blocks_movement:
                    return True
        return False
    
    @property
    def destination_is_blocking_terrain(self) -> bool:
        if self.store and self.store.atlas.active and self.destination: # type: ignore Assume store is GameStore
            return self.store.atlas.active.is_blocked(self.destination)  # type: ignore
        return False
    
    @property
    def destination_is_map_boundary(self) -> bool:
        if self.store and self.store.atlas.active and self.destination: # type: ignore Assume store is GameStore
            map_width = self.store.atlas.active.grid.width  # type: ignore
            map_height = self.store.atlas.active.grid.height  # type: ignore
            if self.destination:
                if self.destination.x < 0 or self.destination.x >= map_width or self.destination.y < 0 or self.destination.y >= map_height:
                    return True
        return False    
    
    def move(self) -> None:
        self.location = self.destination
        self.destination = None
        self.update()


@action_locked
class TargetableEntity(BaseGameEntity):
    """A Targetable Entity is any game object that can become the focus of a TargetingEntity.
    It has a 'perception' substate that is an instance of TargetedSubState that manages its targeted states.
    A Targetable Entity can be damaged."""

    targeter: TargetingEntity | None = None
    perception: TargetedSubState
    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("perception", TargetedSubState))
    
    def __init__(self,
                 store: GameStore | None = None,
                 location: TileCoordinate | None = None,
                 *,
                 name: str="<Unnamed>", 
                 symbol: str=' ', 
                 color: Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__(store=store, location=location, name=name, symbol=symbol, color=color)

    def set_targeter(self, targeter: TargetingEntity) -> None:
        self.targeter = targeter
        self.update()

    def clear_targeter(self) -> None:
        self.targeter = None
        self.update()


@action_locked
class TargetingEntity(BaseGameEntity):
    """A Targeting Entity is any game object that can focus on a TargetableEntity. It has a 'focus' substate 
    that is an instance of TargetingSubState that manages its targeting states. A Targeting Entity can assess 
    threat levels and has a 'threat_level' property to represent its current threat assessment."""

    target: TargetableEntity | None = None
    focus: TargetingSubState
    _fov_radius: int = 6
    _earshot_radius: int = 10
    _visible_tiles: np.ndarray | None = None
    _earshot_tiles: np.ndarray | None = None
    _initial_threat_level: int = 10
    _threat_level: int = 0
    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("focus", TargetingSubState))

    def __init__(self,
                 store: GameStore | None = None,
                 *,
                 location: TileCoordinate | None = None,
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
    def visible_tiles(self) -> np.ndarray | None:
        return self._visible_tiles
    
    @visible_tiles.setter
    def visible_tiles(self, value: np.ndarray | None) -> None:
        self._visible_tiles = value

    @property
    def earshot_radius(self) -> int:
        return self._earshot_radius
    
    @earshot_radius.setter
    def earshot_radius(self, value: int) -> None:
        self._earshot_radius = value

    @property
    def earshot_tiles(self) -> np.ndarray | None:
        return self._earshot_tiles
    
    @earshot_tiles.setter
    def earshot_tiles(self, value: np.ndarray | None) -> None:
        self._earshot_tiles = value

    @property
    def target_in_fov(self) -> bool:
        if self.target and self.target.location is not None and isinstance(self.visible_tiles, np.ndarray):
            return self.is_location_in_fov(self.target.location)

        return False

    @property
    def distance_to_target(self) -> int:

        if self.target and self.location and self.target.location is not None:
            dx = self.target.location.x - self.location.x
            dy = self.target.location.y - self.location.y
            return max(abs(dx), abs(dy))  # Using Chebyshev distance for grid-based movement
        
        return 9999
    
    def is_location_in_fov(self, location: TileCoordinate | None) -> bool:
        if isinstance(self.visible_tiles, np.ndarray):
            self.update_visible_tiles()
            if location and self.visible_tiles[location.x, location.y]:
                return True

        return False
    
    def is_location_in_earshot(self, location: TileCoordinate | None) -> bool:
        if isinstance(self.earshot_tiles, np.ndarray):
            self.update_earshot_tiles()
            if location and self.earshot_tiles[location.x, location.y]:
                return True
        return False
    
    def update_visible_tiles(self) -> None:
        self.visible_tiles = self.tiles_in_range(self.fov_radius)

    def update_earshot_tiles(self) -> None:
        self.earshot_tiles = self.tiles_in_range(self._earshot_radius)

    def tiles_in_range(self, radius: int) -> np.ndarray | None:
        blocking_tiles = None
        tiles_in_range = None

        if self.store and self.store.atlas:  # type: ignore Assume store is GameStore
            blocking_tiles = self.store.atlas.active.blocks_vision  # type: ignore

            if isinstance(blocking_tiles, np.ndarray) and self.location is not None:
                tiles_in_range = compute_fov(~blocking_tiles, (self.location.x, self.location.y), radius=radius, algorithm=libtcodpy.FOV_RESTRICTIVE)
        
        return tiles_in_range

    def set_target(self, target: TargetableEntity) -> None:
        self.threat_level = self._initial_threat_level
        self.target = target
        target.set_targeter(self)
        self.update()

    def clear_target(self) -> None:
        if self.target:
            self.target.clear_targeter()
        self.target = None
        self.threat_level = self._initial_threat_level
        self.update()

    def acquire_target(self) -> bool:
        visible_targets: List[TargetableEntity] = []
        distances: List[Tuple[int, TargetableEntity]] = []
        threats: list[Tuple[int, TargetableEntity]] = []
        selection_list = []

        if self.store and self.store.portfolio:  # type: ignore | A TargetingEntity must have a GameStore
            self.update_visible_tiles()
            visible_targets = [entity for entity in self.store.portfolio.live_actors if entity and self.visible_tiles[entity.location.x, entity.location.y]]  # type: ignore Assume live_actors is List[Character]
    
        if visible_targets:
            for entity in visible_targets:
                if entity is not self and not isinstance(entity, self.__class__):
                    self.set_target(entity)
                    distance = self.distance_to_target
                    distances.append((distance, entity))
                    threat = self.threat_level
                    threats.append((threat, entity))
        
        if distances and threats:
            distances.sort(key=lambda x: x[0])
            threats.sort(key=lambda x: x[0], reverse=True)
        
        for threat, threat_entity in threats:
            for distance, distance_entity in distances:
                if threat_entity is distance_entity:
                    selection_list.append((threat * (self.fov_radius - distance), threat_entity))
        
        if selection_list:
            selection_list.sort(key=lambda x: x[0], reverse=True)
            self.set_target(selection_list[0][1])
            return True
        else:
            self.clear_target()
            return False

    def assess_threat(self) -> None:
        friendly = isinstance(self.target, self.__class__)
        threat_level = self._initial_threat_level

        if self.distance_to_target > 8:
            threat_level = self._initial_threat_level * (not friendly)
        if self.distance_to_target <= 8:
            threat_level += (self._initial_threat_level + 10) * (not friendly)
        if self.distance_to_target <= 5:
            threat_level += (self._initial_threat_level + 20) * (not friendly)
        if self.distance_to_target <= 2:
            threat_level += (self._initial_threat_level + 30) * (not friendly)
        if self.distance_to_target == 1:
            threat_level += (self._initial_threat_level + 40) * (not friendly)
        if self.target and hasattr(self.target, 'target'):
            if self.target.target is self: # type: ignore
                threat_level = threat_level * 2 * (not friendly)

        self.threat_level = threat_level

    def update(self) -> None:
        self.update_visible_tiles()
        self.update_earshot_tiles()
        self.assess_threat()
        super().update()


@action_locked
class CombatEntity(TargetableEntity, TargetingEntity):
    """A Combat Entity is any game object that can both target and be targeted by other entities and deal damage.
    It has both 'focus' and 'perception' substates that are instances of TargetingSubState and TargetedSubState. 
    It has a 'combat' substate that is an instance of CombatSubState to manage its combat states. A Combat Entity has
    'attack' and 'defense' methods to calculate damage dealt and mitigated during combat."""

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

    def attack(self) -> int:
        return self._attack_power #TODO: add state-based modifiers
    
    def defend(self) -> int:
        damage_mitigated = 0
        match self.combat.state:  # type: ignore
            case 'engaged':
                damage_mitigated = self._defense_power // 2
            case 'fighting':
                damage_mitigated = self._defense_power
            case 'disengaged':
                damage_mitigated = self._defense_power // 4
            case 'peaceful':
                damage_mitigated = 0
            case _:
                damage_mitigated = 0

        return damage_mitigated 


@action_locked
class Character(MobileEntity, CombatEntity):
    health: CharacterHealthSubState
    is_alive: bool

    _substates_manifest = (
        ("spawn", BaseGameSubState),
        ("perception", TargetedSubState),
        ("focus", TargetingSubState),
        ("combat", CombatSubState),
        ("health", CharacterHealthSubState),
        ("collision", CollisionSubState)
    )

    def __init__(   self,
                    store: GameStore | None = None,
                    *,
                    location: TileCoordinate | None = None,
                    symbol: str = "?",
                    color: Tuple[int, int, int],
                    name: str = "<Unnamed>",
                    ) -> None:
                
        self.is_alive = True

        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

    def take_damage(self, damage: int) -> None:
        if self.is_alive:
            initial_health_state = self.health.state  # type: ignore

            if self.hp is not None:
                hit = self.hp - damage

                match self.health.state:  # type: ignore
                    case 'healthy':
                        if hit < 0:
                            # Survivability check could go here
                            self.hp = 0
                        else:
                            self.hp = hit
                            
                    case 'injured':
                        if hit < 0:
                            # Survivability check could go here, outcome different from healthy state
                            self.hp = 0
                        else:
                            self.hp = hit

                    case 'critical':
                        if hit < 0:
                            # Survivability check could go here, outcome different from injured state
                            self.hp = 0
                        else:
                            self.hp = hit

                    case 'unconscious':
                        if hit < 0:
                            # Survivability check could go here, outcome different from critical state
                            self.die()

                    case 'dead':
                        pass

                self.update()

            final_health_state = self.health.state  # type: ignore
            if initial_health_state != final_health_state:
                self.store.log.add(f"{self.name} is now {final_health_state}.")  # type: ignore

    def die(self) -> None:
        self.blocks_movement = False
        self.is_invulnerable = True
        self.is_alive = False
        self.store.log.add(f"{self.name} has died.")  # type: ignore
        self.name = f"remains of {self.name}"
        #self.symbol = "%"
        self.color = enemy_die



