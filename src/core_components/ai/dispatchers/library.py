# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import numpy as np

from core_components.ai.dispatchers.base import *
from core_components.entities.library import BaseEntity, TargetableEntity, MobileEntity, TargetingEntity, CombatEntity, Charactor
from core_components.ai.events.library import FOVUpdateEvent, GameStartEvent, GameOverEvent, MeleeAttackEvent, FOVUpdateEvent, TargetAvailableAIEvent, OnTargetAIEvent, TargetOutOfRangeAIEvent
from core_components.ai.actions.library import EntityAcquireTargetAction, EntityActionOnDestination, EntityActionOnTarget, EntityCollisionAction, EntityMeleeAction, FOVUpdateAction, GameStartAction, GameOverAction, EntityMoveAction, GeneralAction
from core_components.maps.tiles.base import TileTuple, TileCoordinate

A = TypeVar('A', EntityActionOnDestination, EntityActionOnTarget)

class AIDispatcher(BaseEventDispatcher):
    MOVEMENT_ACTION = EntityMoveAction()
    COLLISION_ACTION = EntityCollisionAction()
    TARGET_ACQUISITION_ACTION = EntityAcquireTargetAction()
    MELEE_ATTACK = EntityMeleeAction()

    @classmethod
    def create_action_on_target(cls, action: A, state: GameState, entity: BaseEntity, target: BaseEntity | TileCoordinate) -> A:
        clone = super().create_state_action(action, state)
        if isinstance(entity, MobileEntity) and isinstance(clone, EntityActionOnDestination):
            clone.entity = entity
        elif isinstance(entity, (Charactor)) and isinstance(clone, EntityActionOnTarget):
            clone.entity = entity
        if isinstance(clone, EntityActionOnTarget) and isinstance(target, (Charactor)):
            clone.target = target
        elif isinstance(target, TileCoordinate) and isinstance(clone, EntityActionOnDestination):
            clone.destination = target
        return clone
    
    def get_path_to(self, state: GameState, entity: BaseEntity,destination: TileCoordinate) -> List[TileCoordinate]:
        """Compute and return a path to the target position.

        If there is no valid path then returns an empty list.
        """
        game_map = state.map.active

        # Copy the traversable array.
        cost = np.array(game_map.blocks_movement, dtype=np.int8) + 1

        for location in state.roster.entity_blocked_locations:
            if location and cost[location.x, location.y]:
                cost[location.x, location.y] += 10

        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=0)
        pathfinder = tcod.path.Pathfinder(graph)
        start = entity.location.to_tuple
        end = destination.to_tuple
        pathfinder.add_root(start)  
        path = pathfinder.path_to(end)[1:]
        return [game_map.grid.get_location(index[0], index[1]) for index in path]
    
    def distance_to_target(self, entity: BaseEntity, target: BaseEntity) -> int | None:
        if target:
            dx = target.location.x - entity.location.x
            dy = target.location.y - entity.location.y
            return max(abs(dx), abs(dy))
        
        return None

    def _ev_meleeattack(self,  event: MeleeAttackEvent, state: GameState) -> EntityActionOnTarget:
        entity = event.entity
        target = event.target

        state_action = self.create_action_on_target(self.MELEE_ATTACK, state, entity, target) # type: ignore

        if isinstance(entity, CombatEntity) and isinstance(target, CombatEntity):
            state_action.entity = entity
            state_action.target = target

        return state_action
    
    def _ev_targetavailableaievent(self, 
                          event: TargetAvailableAIEvent, 
                          state: GameState) -> EntityAcquireTargetAction:
        entity = event.entity
        target = event.target

        state_action = self.create_action_on_target(self.TARGET_ACQUISITION_ACTION, state, entity, target) # type: ignore

        if isinstance(entity, TargetingEntity) and isinstance(target, TargetableEntity):
            state_action.entity = entity
            state_action.target = target

        return state_action # type: ignore
    
    # def _ev_ontargetaievent(self,
    #                     event: OnTargetAIEvent,
    #                     state: GameState) -> EntityMeleeAction:
    #         entity = event.entity
    #         target = event.target
    
    #         state_action = self.create_action_on_target(self.MOVEMENT_ACTION, state, entity, target) # type: ignore
    
    #         if isinstance(entity, CombatEntity) and isinstance(target, CombatEntity):
    #             state_action.entity = entity
    #             state_action.destination = target.location
    
    #         return state_action # type: ignore
    
    def _ev_meleeattackevent(self,
                         event: MeleeAttackEvent,
                         state: GameState) -> EntityMeleeAction:
            entity = event.entity
            target = event.target
    
            state_action = self.create_action_on_target(self.MELEE_ATTACK, state, entity, target) # type: ignore
    
            if isinstance(entity, CombatEntity) and isinstance(target, CombatEntity):
                state_action.entity = entity
                state_action.target = target
    
            return state_action # type: ignore
    
    def _ev_targetoutofrangeaievent(self,
                            event: TargetOutOfRangeAIEvent,
                            state: GameState) -> EntityMoveAction:
            entity = event.entity
            target = event.target
            state_action: EntityMoveAction
            path = []
            state_action = self.create_action_on_target(self.MOVEMENT_ACTION, state, entity, target) # type: ignore
    
            if entity and target:
                path = self.get_path_to(state, entity, target.location)
            if path:
                state_action.destination = path[0]  # Move to the next step in the path.

            return state_action 
    
    # type: ignore
    # def _ev_targetcollision(self) -> Sequence[BaseAction]:
            
    #         if isinstance(obstacle, TargetableEntity):
    #             if isinstance(self.entity, TargetingEntity) and not self.entity.target and obstacle.targetable:
    #                 return EntityAcquireTargetAction(self.engine, self.entity, obstacle).perform() # Acquire target.
                
    #         if isinstance(self.entity, CombatEntity):
    #             return EntityMeleeAction(self.engine, self.entity, obstacle).perform() # Immediate melee attack.


class InputDispatcher(BaseEventDispatcher):

    MOVEMENT_KEYS = {
        tcod.event.KeySym.LEFT: (-1, 0),
        tcod.event.KeySym.A: (-1, 0),
        tcod.event.KeySym.RIGHT: (1, 0),
        tcod.event.KeySym.D: (1, 0),
        tcod.event.KeySym.UP: (0, -1),
        tcod.event.KeySym.W: (0, -1),
        tcod.event.KeySym.DOWN: (0, 1),
        tcod.event.KeySym.S: (0, 1),
        }
    
    MOVEMENT_ACTION = EntityMoveAction()
    COLLISION_ACTION = EntityCollisionAction()
    TARGET_ACQUISITION_ACTION = EntityAcquireTargetAction()

    # def __init__(self, state: GameState | None = None) -> None:
    #     self.mob_actions: List[BaseGameAction] = []

    # @property
    # def mobs(self) -> Generator[AICharactor]:
    #     yield from (mob for mob in self.engine.roster.live_ai_actors if isinstance(mob.ai, HostileAI))

    @classmethod
    def create_action_on_target(cls, action: A, state: GameState, entity: BaseEntity, target: BaseEntity | TileCoordinate) -> A:
        clone = super().create_state_action(action, state)
        if isinstance(entity, MobileEntity) and isinstance(clone, EntityActionOnDestination):
            clone.entity = entity
        elif isinstance(entity, (Charactor)) and isinstance(clone, EntityActionOnTarget):
            clone.entity = entity
        if isinstance(clone, EntityActionOnTarget) and isinstance(target, (Charactor)):
            clone.target = target
        elif isinstance(target, TileCoordinate) and isinstance(clone, EntityActionOnDestination):
            clone.destination = target
        return clone

    def _ev_keydown(self, event: tcod.event.KeyDown, state: GameState) -> SystemExitAction | EntityMoveAction | EntityCollisionAction | NoAction:
        state_action: SystemExitAction | EntityMoveAction | EntityCollisionAction | NoAction

        player = state.roster.player
        state_action = self.create_state_action(self.NOACTION, state)
        state.events.put(FOVUpdateEvent(""))

        match event.sym:
            case tcod.event.KeySym.ESCAPE:
                print("Exiting game.")
                state_action = self.create_state_action(self.SYSTEMEXIT, state)
        
            case tcod.event.KeySym.LEFT | tcod.event.KeySym.RIGHT | tcod.event.KeySym.UP | tcod.event.KeySym.DOWN | tcod.event.KeySym.W | tcod.event.KeySym.A | tcod.event.KeySym.S | tcod.event.KeySym.D:
                if player is not None:

                    state_action = self.create_state_action(self.NOACTION, state)
                    destination = self.get_destination(event, player)
                    player.destination = destination
                    blocking_entity = state.roster.entity_collision(player)
                    blocking_tile = state.map.active.object_collision(player.destination)

                    if blocking_entity is not None and isinstance(blocking_entity, TargetableEntity):
                        target_action = self.create_action_on_target(self.COLLISION_ACTION, state, player, blocking_entity)
                        state.actions.put(target_action)
                    
                    #TODO: Update fov??
                              
                    elif blocking_tile:
                        # Collision with map object
                        pass
                    
                    elif not blocking_entity and not blocking_tile:
                        state_action = self.create_action_on_target(self.MOVEMENT_ACTION, state, player, player.destination) #type: ignore
                    
                    #TODO: Trigger mob actions on KeyUp??
        

        return state_action

    def get_destination(self, event, entity) -> TileCoordinate:
        dx, dy = self.MOVEMENT_KEYS[event.sym]
        x = entity.location.x + dx
        y = entity.location.y + dy
        destination_tuple = TileTuple(([x], [y]))

        return TileCoordinate(destination_tuple, entity.location.parent_map_size)
    
        # if self.mob_actions:
        #     while self.mob_actions:
        #         action = self.mob_actions.pop(0)

        #         if issubclass(action.__class__, ActionOnTarget) or issubclass(action.__class__, ActionOnDestination):
        #             actions += [action]
        #         else:
        #             unused_actions += [action]
            
        #     self.mob_actions = unused_actions

        # return actions

    
class InterfaceDispatcher(BaseEventDispatcher):
    pass

    # def ev_mapupdate(self) -> Sequence[BaseGameAction]:
    #     return [UIUpdateMapColorsAction(self.state)]


class SystemDispatcher(BaseEventDispatcher):
    GAMESTART = GameStartAction()
    GAMEOVER = GameOverAction()
    FOVUPDATE = FOVUpdateAction()

    def _ev_gamestartevent(self, 
                      event: GameStartEvent, 
                      state: GameState) -> BaseGameAction:
        message = event.message
        # TODO: Message log
        state_action = self.create_state_action(self.GAMESTART, state)

        return state_action

    def _ev_gameoverevent(self, 
                     event: GameOverEvent, 
                     state: GameState) -> BaseGameAction:
        message = event.message
        # TODO: Message log
        state_action = self.create_state_action(self.GAMEOVER, state)

        return state_action
    
    def _ev_fovupdateevent(self,
                         event: FOVUpdateEvent,
                         state: GameState) -> BaseGameAction:
        message = event.message

        state_action = self.create_state_action(self.FOVUPDATE, state)

        return state_action


