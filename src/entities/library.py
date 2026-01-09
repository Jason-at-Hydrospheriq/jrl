
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import numpy as np    
from tcod import libtcodpy
from tcod.map import compute_fov

if TYPE_CHECKING:
    from entities.library import TargetingEntity
    from store import GameStore
    from loop_resources.components import SubLoopHandler

from tcod.path import Pathfinder, SimpleGraph
from game_types import TileCoordinate
from display_components.graphics.colors import enemy_die
from entities.base import BaseGameEntity, BaseGameSubState, action_locked
from entities.components import CollisionSubState, CombatSubState, TargetedSubState, TargetingSubState, CharacterHealthSubState


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

    targeter: "TargetingEntity | None" = None
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

    def set_targeter(self, targeter: "TargetingEntity") -> None:
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


# ENTITIES
@action_locked
class AICharacter(Character):
    path: List[TileCoordinate] = []
    _ai: SubLoopHandler | None = None

    def __init__(   self,
                    store: GameStore | None = None,
                        *,
                    location: TileCoordinate | None = None,
                    name: str = "<Unnamed>",
                    symbol: str = '?',
                    color: Tuple[int, int, int]=(255, 255, 255),
                    ai: SubLoopHandler | None = None,
                    ) -> None:

        if ai:
            self._ai = ai

        super().__init__(store=store, location=location, symbol=symbol, color=color, name=name)

    @property
    def ai(self) -> SubLoopHandler | None:
        return self._ai

    @ai.setter
    def ai(self, value: SubLoopHandler | None) -> None:
        self._ai = value

    def set_path_to_target(self) -> None:
        if self.target and self.location and self.store and self.store.atlas and self.target.location is not None:  # type: ignore | Assume store is GameStore
            map_size = self.store.atlas.active.grid.size  # type: ignore | Assume store is GameStore
            blocked_tiles = np.array(self.store.atlas.active.blocks_movement, dtype=np.int8) # type: ignore | Assume store is GameStore
            blocked_tiles += 10
            cost = SimpleGraph(cost=blocked_tiles, cardinal=2, diagonal=5)
            finder = Pathfinder(cost)  # type: ignore | Assume store is GameStore
            finder.add_root(self.location.to_tuple)
            path = finder.path_to(self.target.location.to_tuple)
            self.path = [TileCoordinate.from_tuple((step[0], step[1]), parent_map_size=map_size) for step in path]
        else:
            self.path = []
        self.update()

    def set_destination_from_path(self) -> None:
        if self.path:
            self.path.pop(0)  # Remove current location from path
            self.destination = self.path.pop(0) if self.path else None
        else:
            self.set_path_to_target()
            self.set_destination_from_path()

        self.update()

    def die(self) -> None:
        super().die()
        self._ai = None

    def update(self) -> None:
        super().update()



