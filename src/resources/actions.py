# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from tcod.map import compute_fov
from tcod import libtcodpy

from resources.events import MapUpdate, UIEvent

if TYPE_CHECKING:
    from components.roster import Roster

from resources.entities import BaseEntity, CombatEntity, MobileEntity, MortalEntity, TargetableEntity, TargetingEntity

from engine import Engine
from components.game_map import MapCoords
from resources import tile_types
import numpy as np

from components.display.maps import MainMapDisplay


class BaseAction(Protocol):
    """ A generic action that is dispatched by the AI to an action queue. Actions have a perform method that updates the game state when called."""

    def perform(self) -> None:
        ...


class NoAction(BaseAction):

    def perform(self) -> None:
        pass

        
class SystemExitAction(BaseAction):

    def perform(self) -> None:
        raise SystemExit()


class EngineBaseAction(BaseAction):
    engine: Engine
    
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.roster = engine.roster
    

class GameOverAction(EngineBaseAction):
    def perform(self) -> None:
        self.engine.game_over = True


class EntityActionOnSelf(EngineBaseAction):
    def __init__(self, engine: Engine, entity: BaseEntity) -> None:
        super().__init__(engine)
        self.entity = entity


class EntityActionOnTarget(EngineBaseAction):
    def __init__(self, engine: Engine, entity: TargetingEntity, target: TargetableEntity) -> None:
        super().__init__(engine)
        self.entity = entity
        self.target = target


class EntityActionOnDestination(EngineBaseAction):
    def __init__(self, engine: Engine, entity: MobileEntity, destination: MapCoords) -> None:
        super().__init__(engine)
        self.entity = entity

        if hasattr(entity, 'destination'): 
            self.entity.destination = destination #type: ignore


class EntityAcquireTargetAction(EntityActionOnTarget):
    
    def perform(self) -> None:
        self.entity.acquire_target(self.target)


class EntityMoveAction(EntityActionOnDestination):

    def perform(self) -> None:

        obstacle = self.roster.entity_collision(self.entity)
        if obstacle:
                
            if isinstance(obstacle, TargetableEntity):
                if isinstance(self.entity, TargetingEntity) and not self.entity.target and obstacle.targetable:
                    EntityAcquireTargetAction(self.engine, self.entity, obstacle).perform() # Acquire target.
                
                if isinstance(self.entity, CombatEntity):
                    return EntityMeleeAction(self.engine, self.entity, obstacle).perform() # Immediate melee attack.

            return  # Destination is blocked by an entity, wall, or map boundary.
        
        else:
            self.entity.move()
            self.engine.game_events.add(MapUpdate("main_map", f"{self.entity.name} moved to {self.entity.location}"))


class EntityMeleeAction(EntityActionOnTarget):

    def perform(self) -> None:
        damage = 0
        defense = 0
        attack_power = 0

        if isinstance(self.entity, CombatEntity) and self.entity.combat:
            attack_power = self.entity.combat.attack_power
            if isinstance(self.target, CombatEntity) and self.target.combat:
                defense = self.target.combat.defense
            
        if isinstance(self.target, MortalEntity):
            defense = 1  # Basic defense for non-combat entities
            damage = max(0, attack_power - defense)
            self.target.take_damage(damage)

            if self.target.physical.hp <= 0: #type: ignore
                return DeathAction(self.engine, self.target).perform()


class DeathAction(EntityActionOnSelf):

    def __init__(self, engine: Engine, entity: MortalEntity) -> None:
        super().__init__(engine, entity)
        self.entity = entity

    def perform(self) -> None:
        
        if self.entity == self.roster.player:
            death_message = "You have died! Game Over."

        else:
            death_message = f"{self.entity.name} is dead!"

        self.entity.die()
        print(death_message)


class UIUpdateMapColorsAction(EngineBaseAction):

    def perform(self) -> None:
        tile_map = self.engine.game_map
        player = self.engine.roster.player

        if self.engine and player and tile_map:
                fov = compute_fov(tile_map.tiles["transparent"], (player.location.x, player.location.y), radius=player.fov_radius, algorithm=libtcodpy.FOV_SHADOW)
                tile_map.set_visible(fov)
                tile_map.update_explored(fov)

        colors = np.select(condlist=[~tile_map.explored, tile_map.visible, tile_map.explored], 
                           choicelist=[tile_map.tiles["type"]["shroud"], tile_map.tiles["type"]["light"], tile_map.tiles["type"]["dark"]], 
                           default=tile_types.SHROUD)

        tile_map.update_colors(colors)
        map_displays = self.engine.ui.get_elements_by_type(MainMapDisplay)
        
        for map_display in map_displays:
            map_display.render(self.engine)