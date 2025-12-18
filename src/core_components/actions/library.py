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
from core_components.entities.library import BaseEntity, CombatEntity, MobCharactor, MobileEntity, PlayerCharactor, TargetableEntity, TargetingEntity, MortalEntity
from core_components.events.library import TargetCollision, MeleeCollision, MeleeAttack

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
    
    def __init__(self, state: GameState | None = None) -> None:
        if state:
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

class FOVUpdateAction(EngineBaseAction):
        
        def perform(self) -> None:
            """Recompute the visible area based on the players point of view."""
            tile_blocks_vision = self.state.map.active.get_tile_layout('blocks_vision')
            player = self.state.roster.player

            if player and tile_blocks_vision is not None:
                visible_tiles = compute_fov( tile_blocks_vision, (player.location.x, player.location.y), radius=player.fov_radius, algorithm=libtcodpy.FOV_SHADOW)
                self.state.map.active.set_state_bits('visible', visible_tiles)

                # If a tile is "visible" it should be added to "explored".
                if visible_tiles is not None:
                    prior_seen_tiles = self.state.map.active.get_state_bits('seen')
                    newly_seen_tiles = np.logical_or(prior_seen_tiles, visible_tiles)
                    self.state.map.active.set_state_bits('seen', newly_seen_tiles)

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
    def __init__(self, *,
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
        entity_can_target = issubclass(self.entity.__class__, TargetingEntity) if self.entity else False
        entity_can_melee = issubclass(self.entity.__class__, CombatEntity) if self.entity else False
        target_can_be_targeted = issubclass(self.target.__class__, TargetableEntity) if self.target else False
        target_can_melee = issubclass(self.target.__class__, CombatEntity) if self.target else False

        entity_targets = entity_can_target and target_can_be_targeted
        entity_melees = entity_can_melee and target_can_melee 

        if self.entity is not None and self.target is not None: # Acquire target if none exists.
            
            entity_has_target = self.entity.target is not None if hasattr(self.entity, 'target') else False
            
            if entity_targets and not entity_has_target:
                return EntityAcquireTargetAction(state=self.state, entity=self.entity, target=self.target).perform() # Acquire target.
        
            elif entity_melees and entity_has_target:
                return EntityMeleeAction(state=self.state, entity=self.entity, target=self.target).perform() # Immediate melee attack.


class EntityMoveAction(EntityActionOnDestination):

    def perform(self) -> None:

        if self.entity and self.entity.destination:
            self.entity.move()

        # self.states.game_events.add(MapUpdate("main_map", f"{self.entity.name} moved to {self.entity.location}"))


class EntityMeleeAction(EntityActionOnTarget):
    """ Melee combat is between to combat entities."""
    def perform(self) -> None:
        damage = 0
        defense = 0
        attack_power = 0


        if self.entity is not None and self.target is not None and isinstance(self.entity, CombatEntity) and isinstance(self.target, CombatEntity):
            engaged = self.entity.in_combat and self.target.in_combat
            if not engaged:
                 self.entity.in_combat = True
                 self.target.in_combat = True

            if engaged:     
                attack_power = self.entity.combat.attack_power # type: ignore
                defense = self.target.combat.defense # type: ignore
                
                if isinstance(self.target, MortalEntity): # Attack only mortal entities
                    defense = 1  # Basic defense for non-combat entities
                    damage = max(0, attack_power - defense)
                    self.target.take_damage(damage)
                    print(f"{self.entity.name} attacks {self.target.name} for {damage} damage!")

                if isinstance(self.entity, PlayerCharactor) and isinstance(self.target, MobCharactor): # Launch counterattack if target was a mob
                    counterattack_event = MeleeAttack(entity=self.target, target=self.entity, message=f"{self.target.name} counterattacks {self.entity.name}!")
                    self.state.events.put(counterattack_event)

                if self.target.physical.hp <= 0 and isinstance(self.entity, CombatEntity): #type: ignore
                    self.entity.clear_target()
                    self.entity.in_combat = False
                
                if self.target.physical.hp <= 0 and isinstance(self.target, MortalEntity): #type: ignore
                    return EntityDeathAction(self.state, self.entity, self.target).perform() # type: ignore


class EntityDeathAction(EntityActionOnTarget):

    def __init__(self, state: GameState, entity: CombatEntity, target: MortalEntity) -> None:
        self.state = state
        self.entity = entity
        self.target = target

    def perform(self) -> None:
        
        if self.target == self.state.roster.player:
            death_message = f"You have been slain by {self.entity.name}! Game Over."
            print(death_message)
            self.target.die()

            return GameOverAction(self.state).perform()

        else:
            death_message = f"You have slain {self.target.name}!"
            print(death_message)
            self.target.die()

            
