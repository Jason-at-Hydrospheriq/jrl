# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.events.library import GameStart, GameOver
    from state import GameState
    
from components.actions.base import *


class EntityDispatcher(BaseEventDispatcher):
    pass
    # def _ev_targetcollision(self) -> Sequence[BaseAction]:
            
    #         if isinstance(obstacle, TargetableEntity):
    #             if isinstance(self.entity, TargetingEntity) and not self.entity.target and obstacle.targetable:
    #                 return EntityAcquireTargetAction(self.engine, self.entity, obstacle).perform() # Acquire target.
                
    #         if isinstance(self.entity, CombatEntity):
    #             return EntityMeleeAction(self.engine, self.entity, obstacle).perform() # Immediate melee attack.


class InputDispatcher(BaseEventDispatcher):
    pass
    # def __init__(self, state: GameState | None = None) -> None:
    #     super().__init__(state)
        # self.mob_actions: List[BaseStateAction] = []

    # @property
    # def mobs(self) -> Generator[AICharactor]:
    #     yield from (mob for mob in self.engine.roster.live_ai_actors if isinstance(mob.ai, HostileAI))
    
    # def _ev_keydown(self, event: tcod.event.KeyDown) -> Sequence[BaseAction]:
    #     actions = [NoAction()]

    #     if event.sym == tcod.event.KeySym.ESCAPE:
    #         actions += [SystemExitAction()]
        
    #     if event.sym in MOVEMENT_KEYS:
    #         dx, dy = MOVEMENT_KEYS[event.sym]
    #         destination = self.engine.game_map.get_map_coords(self.engine.roster.player.location.x + dx, self.engine.roster.player.location.y + dy)
    #         actions += [EntityMoveAction(self.engine, self.engine.roster.player, destination)]
        
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

    # def ev_mapupdate(self) -> Sequence[BaseStateAction]:
    #     return [UIUpdateMapColorsAction(self.state)]


class SystemDispatcher(BaseEventDispatcher):
            
    def _ev_gamestart(self, 
                      event: GameStart, 
                      state: GameState) -> List[BaseStateAction]:
        message = event.message
        # TODO: Message log

        return [self.create_state_action(GAMESTART, state)]
    
    def _ev_gameover(self, 
                     event: GameOver, 
                     state: GameState) -> List[BaseStateAction]:
        message = event.message
        # TODO: Message log

        return [self.create_state_action(GAMEOVER, state)]
    
    def _ev_keydown(self, 
                    event: tcod.event.KeyDown, 
                    state: GameState) -> List[BaseStateAction]:
        state_actions = [self.create_state_action(NOACTION, state)]

        if event.sym == tcod.event.KeySym.ESCAPE:
            state_actions += [self.create_state_action(SYSTEMEXIT, state)]

        return state_actions