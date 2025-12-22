# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from tcod.map import compute_fov
from tcod import libtcodpy
import numpy as np

from core_components.maps.tiles import TileCoordinate

if TYPE_CHECKING:
    from core_components.store import GameStore

from core_components.entities.library import Charactor, CombatEntity, MobCharactor, MobileEntity, PlayerCharactor, TargetableEntity, TargetingEntity, MortalEntity
from core_components.loops.events import FOVUpdateEvent, MeleeAttackEvent, TargetAvailableAIEvent


class GeneralAction:

    def __init__(self) -> None:
        pass

    def perform(self) -> None:
        raise NotImplementedError()


class NoAction(GeneralAction):
    
    def perform(self) -> None:
        pass


class EngineBaseAction(GeneralAction):
    state: GameStore
    
    def __init__(self, state: GameStore | None = None) -> None:
        if state:
            self.state = state
            self.roster = state.roster


class SystemExitAction(EngineBaseAction):

    def perform(self) -> None:
        self.state.game_over.set()

    
class GameStartAction(EngineBaseAction):

    def perform(self) -> None:
        print("Game On")
        self.state.game_over.clear()


class GameOverAction(EngineBaseAction):

    def perform(self) -> None:
        print("Game Over")
        self.state.game_over.set()


class FOVUpdateAction(EngineBaseAction):
        
        def perform(self) -> None:
            """Recompute the visible area based on the players point of view."""
            tile_blocks_vision = self.state.map.active.blocks_vision if self.state.map and self.state.map.active else None
            player = self.state.roster.player
            mobs = self.state.roster.live_ai_actors
            player_visible_tiles = np.full((self.state.map.active.grid.width, self.state.map.active.grid.height), False, order="F")            

            # UPDATE PLAYER FOV
            if player and tile_blocks_vision is not None:
                player_visible_tiles = compute_fov( ~tile_blocks_vision, (player.location.x, player.location.y), radius=player.fov_radius, algorithm=libtcodpy.FOV_RESTRICTIVE)
                self.state.map.active.set_state_bits('visible', player_visible_tiles)

                # If a tile is "visible" it should be added to "explored".
                if player_visible_tiles is not None:
                    prior_seen_tiles = self.state.map.active.get_state_bits('seen')
                    newly_seen_tiles = np.logical_or(prior_seen_tiles, player_visible_tiles)
                    self.state.map.active.set_state_bits('seen', newly_seen_tiles)
            
            # UPDATE MOB FOV AND SPOTTING
            if len(mobs) > 0 and player and tile_blocks_vision is not None:
                for mob in mobs:
                    mob_visible_tiles = compute_fov( ~tile_blocks_vision, (mob.location.x, mob.location.y), radius=mob.fov_radius, algorithm=libtcodpy.FOV_SHADOW)
                    
                    if player_visible_tiles[mob.location.x, mob.location.y]:
                        mob.is_spotted = True
                    
                    elif not player_visible_tiles[mob.location.x, mob.location.y]:
                        mob.is_spotted = False

                    if mob_visible_tiles[player.location.x, player.location.y]:
                        mob.is_spotting = True
                        self.state.log.add(text=f"You have been spotted!")
                        player.is_spotted = True

                    elif not mob_visible_tiles[player.location.x, player.location.y]:
                        mob.is_spotting = False
                    
                for mob in mobs:
                    if mob.is_spotted:
                        player.is_spotting = True


class EntityActionOnTarget(EngineBaseAction):
    entity: Charactor | None = None
    target: Charactor | None = None

    def __init__(self, state: GameStore | None = None, 
                 entity: Charactor | None = None, 
                 target: Charactor | None = None) -> None:
        
        if state:
            super().__init__(state)
        self.entity = entity
        self.target = target


class EntityActionOnDestination(EngineBaseAction):
    entity: MobileEntity | None = None
    destination: TileCoordinate | None = None

    def __init__(self, *,
                 state: GameStore | None = None,  
                 entity: MobileEntity | None = None, 
                 destination: TileCoordinate | None = None) -> None:
    
        if state:
            super().__init__(state)
        if entity:
            self.entity = entity
        if destination:
            self.destination = destination


class EntityAcquireTargetAction(EntityActionOnTarget):

    def __init__(self, state: GameStore | None = None, 
                 entity: Charactor | None = None, 
                 target: Charactor | None = None) -> None:
        
        if state and entity and target is not None:
            super().__init__(state=state, entity=entity, target=target)

    def perform(self) -> None:
        if self.entity is not None:
            if isinstance(self.target, Charactor):
                self.entity.acquire_target(self.target)
                self.entity.is_targeting = True
                self.target.is_targeted = True
                self.target.targeter = self.entity
                self.state.log.add(text=f"{self.entity.name} has engaged the {self.target.name}.")
 

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
    entity: MobileEntity | None = None
    destination: TileCoordinate | None = None

    def perform(self) -> None:

        if self.entity and self.destination:
            self.entity.destination = self.destination
            self.entity.move()

            self.state.events.put(FOVUpdateEvent(""))

            for entity in self.state.roster.live_ai_actors:
                if entity:  
                    entity.ai.update_state(self.state) # type: ignore


class EntityMeleeAction(EntityActionOnTarget):
    def __init__(self, state: GameStore | None = None, 
                 entity: Charactor | None = None, 
                 target: Charactor | None = None) -> None:
        if state and entity and target is not None:
            super().__init__(state=state, entity=entity, target=target)

    def perform(self) -> None:
        damage = 0
        defense = 0
        attack_power = 0
    
        if self.entity is not None and self.target is not None and isinstance(self.entity, CombatEntity) and isinstance(self.target, CombatEntity):
            engaged = self.entity.is_in_combat and self.target.is_in_combat
            if not engaged:
                 self.entity.is_in_combat = True
                 self.target.is_in_combat = True

            if engaged:     
                attack_power = self.entity.combat.attack_power # type: ignore
                defense = self.target.combat.defense # type: ignore
                
                if isinstance(self.target, Charactor): # Attack only mortal entities
                    defense = 1  # Basic defense for non-combat entities
                    damage = max(0, attack_power - defense)
                    self.target.take_damage(damage)
                    self.state.log.add(text=f"{self.entity.name} attacks the {self.target.name} for {damage} damage!")

                if isinstance(self.entity, PlayerCharactor) and isinstance(self.target, MobCharactor): # Launch counterattack if target was a mob
                    counterattack_event = MeleeAttackEvent(entity=self.target, target=self.entity)
                    self.state.events.put(counterattack_event)

                if self.target.physical.hp <= 0 and isinstance(self.entity, Charactor): #type: ignore
                    self.entity.clear_target()
                    self.entity.is_in_combat = False
                
                if self.target.physical.hp <= 0 and isinstance(self.target, MortalEntity): #type: ignore
                    return EntityDeathAction(self.state, self.entity, self.target).perform() # type: ignore


class EntityDeathAction(EntityActionOnTarget):
        
    def __init__(self, state: GameStore, entity: Charactor, target: Charactor) -> None:
        self.state = state
        self.entity = entity
        self.target = target

    def perform(self) -> None:
        
        if self.entity and self.target is not None:
            if self.target == self.state.roster.player:
                death_message = f"You have been slain by the {self.entity.name}! Game Over."
                self.state.log.add(text=death_message)
                self.target.clear_target()
                self.target.die()

                return GameOverAction(self.state).perform()

            else:
                death_message = f"You have slain the {self.target.name}!"
                self.state.log.add(text=death_message)
                self.target.clear_target()
                self.target.die()

            
