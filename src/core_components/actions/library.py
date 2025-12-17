# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from tcod.map import compute_fov
from tcod import libtcodpy
import numpy as np

from core_components.tiles.base import TileCoordinate

if TYPE_CHECKING:
    from state import GameState

from core_components.actions.base import BaseGameAction
from core_components.entities.library import BaseEntity, CombatEntity, MobileEntity, TargetableEntity, TargetingEntity, MortalEntity
from core_components.events.library import TargetCollision, MeleeCollision

class GeneralAction(BaseGameAction):

    def __init__(self, state: GameState | None = None) -> None:
        
        if state:
            self.state = state

    def perform(self) -> None:
        raise NotImplementedError()


class NoAction(GeneralAction):

    def perform(self) -> None:
        pass

        
class SystemExitAction(GeneralAction):

    def perform(self) -> None:
        self.state.game_over.set()


class EngineBaseAction(GeneralAction):
    state: GameState
    
    def __init__(self, state: GameState) -> None:
        self.state = state
        self.roster = state.roster
    

class GameStartAction(GeneralAction):

    def perform(self) -> None:
        print("Game On")
        self.state.game_over.clear()


class GameOverAction(GeneralAction):

    def perform(self) -> None:
        print("Game Over")
        self.state.game_over.set()


# class UIUpdateMapColorsAction(EngineBaseAction):

#     def perform(self) -> None:
#         tile_map = self.state.map
#         player = self.state.roster.player

#         if self.state and player and tile_map:
#                 fov = compute_fov(tile_map.tiles["transparent"], (player.location.x, player.location.y), radius=player.fov_radius, algorithm=libtcodpy.FOV_SHADOW)
#                 tile_map.set_visible(fov)
#                 tile_map.update_explored(fov)

#         colors = np.select(condlist=[~tile_map.explored, tile_map.visible, tile_map.explored], 
#                            choicelist=[tile_map.tiles["type"]["shroud"], tile_map.tiles["type"]["light"], tile_map.tiles["type"]["dark"]], 
#                            default=tile_types.SHROUD)

#         tile_map.update_colors(colors)
#         map_displays = self.state.ui.get_elements_by_type(MainMapDisplay)
        
#         for map_display in map_displays:
#             map_display.render(self.state)


# class EntityActionOnSelf(EngineBaseAction):
#     def __init__(self, states: GameState, entity: BaseEntity) -> None:
#         super().__init__(states)
#         self.entity = entity


class EntityActionOnTarget(EngineBaseAction):
    def __init__(self, state: GameState | None = None, 
                 entity: TargetingEntity | CombatEntity | None = None, 
                 target: TargetableEntity | CombatEntity | None = None) -> None:
        if state:
            super().__init__(state)
        self.entity = entity
        self.target = target


class EntityActionOnDestination(EngineBaseAction):
    def __init__(self, 
                 state: GameState | None = None,  
                 entity: MobileEntity | None = None, 
                 destination: TileCoordinate | None = None) -> None:
    
        if state:
            super().__init__(state)
        if entity:
            self.entity = entity
        if destination:
            self.destination = destination
            
        if hasattr(entity, 'destination'): 
            self.entity.destination = destination #type: ignore


class EntityAcquireTargetAction(EntityActionOnTarget):
    
    def perform(self) -> None:
        if self.entity is not None:
            if isinstance(self.target, TargetableEntity):
                self.entity.acquire_target(self.target)


class EntityCollisionAction(EntityActionOnTarget):
    def perform(self) -> None:
        
        if self.entity is not None:
            if isinstance(self.entity.target, TargetableEntity):
                return EntityAcquireTargetAction(self.state, self.entity, self.entity.target).perform() # Acquire target.
                
            if issubclass(self.entity.__class__, CombatEntity):
                if isinstance(self.entity, CombatEntity) and self.entity.in_combat and self.entity.target is not None:
                    return EntityMeleeAction(self.state, self.entity, self.entity.target).perform() # Immediate melee attack.   


class EntityMoveAction(EntityActionOnDestination):

    def perform(self) -> None:

        if self.entity and self.entity.destination:
            self.entity.move()

        # self.states.game_events.add(MapUpdate("main_map", f"{self.entity.name} moved to {self.entity.location}"))


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

            if self.target.physical.hp <= 0 and isinstance(self.entity, CombatEntity): #type: ignore
                return EntityDeathAction(self.state, self.entity, self.target).perform()


class EntityDeathAction(EntityActionOnTarget):

    def __init__(self, state: GameState, entity: CombatEntity, target: MortalEntity) -> None:
        self.state = state
        self.entity = entity
        self.target = target

    def perform(self) -> None:
        
        if self.target == self.state.roster.player:
            death_message = f"You have been slain by {self.entity.name}! Game Over."

        else:
            death_message = f"You have slain {self.target.name}!"

        self.target.die()
        print(death_message)

        return GameOverAction(self.state).perform()
