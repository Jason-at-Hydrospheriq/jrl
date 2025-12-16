# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
    
from core_components.dispatchers.base import *
from core_components.events.library import GameStartEvent, GameOverEvent, InputEvent, SystemEvent
from core_components.actions.library import EngineBaseAction, GameStartAction, GameOverAction, EntityMoveAction
from core_components.tiles.base import TileTuple, TileCoordinate


class EntityDispatcher(BaseEventDispatcher):
    pass
    # def _ev_targetcollision(self) -> Sequence[BaseAction]:
            
    #         if isinstance(obstacle, TargetableEntity):
    #             if isinstance(self.entity, TargetingEntity) and not self.entity.target and obstacle.targetable:
    #                 return EntityAcquireTargetAction(self.engine, self.entity, obstacle).perform() # Acquire target.
                
    #         if isinstance(self.entity, CombatEntity):
    #             return EntityMeleeAction(self.engine, self.entity, obstacle).perform() # Immediate melee attack.


class InputDispatcher(BaseEventDispatcher):

    MOVEMENT_KEYS = {
        tcod.event.KeySym.LEFT: (-1, 0),
        tcod.event.KeySym.RIGHT: (1, 0),
        tcod.event.KeySym.UP: (0, -1),
        tcod.event.KeySym.DOWN: (0, 1),
        }
    
    MOVEMENT_ACTION = EntityMoveAction()

    # def __init__(self, state: GameState | None = None) -> None:
    #     self.mob_actions: List[BaseGameAction] = []

    # @property
    # def mobs(self) -> Generator[AICharactor]:
    #     yield from (mob for mob in self.engine.roster.live_ai_actors if isinstance(mob.ai, HostileAI))

    @classmethod
    def create_movement_action(cls, state: GameState, entity, destination) -> EntityMoveAction:
        clone = super().create_state_action(cls.MOVEMENT_ACTION, state)
        clone.entity = entity
        clone.destination = destination
        return clone

    def _ev_keydown(self, event: tcod.event.KeyDown, state: GameState) -> BaseGameAction:

        state_action = self.create_state_action(self.NOACTION, state)

        match event.sym:
            case tcod.event.KeySym.ESCAPE:
                print("Exiting game.")
                state_action = self.create_state_action(self.SYSTEMEXIT, state)
        
            case tcod.event.KeySym.LEFT | tcod.event.KeySym.RIGHT | tcod.event.KeySym.UP | tcod.event.KeySym.DOWN:
                if state.roster.player is not None:
                    dx, dy = self.MOVEMENT_KEYS[event.sym]
                    x = state.roster.player.location.x + dx
                    y = state.roster.player.location.y + dy
                    destination_tuple = TileTuple(([x], [y]))
                    state.roster.player.destination = TileCoordinate(destination_tuple)
                    #TODO: Check for collisions and obstacles.
                    #TODO: Update fov
                    #TODO: Trigger mob actions
                    state_action = self.create_movement_action(state, state.roster.player, state.roster.player.destination)
        
        return state_action
    
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
    
