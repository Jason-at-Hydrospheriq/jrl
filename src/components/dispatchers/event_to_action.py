# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from components.queues.event_lib import GameStart, GameOver

from src.state import GameState
from components.dispatchers.base import *


class GameEventDispatcher(BaseEventDispatcher):
    def __init__(self, state: GameState | None = None) -> None:

        if state:
            self.state = state


class EntityDispatcher(GameEventDispatcher):
    pass
    # def _ev_targetcollision(self) -> Sequence[BaseAction]:
            
    #         if isinstance(obstacle, TargetableEntity):
    #             if isinstance(self.entity, TargetingEntity) and not self.entity.target and obstacle.targetable:
    #                 return EntityAcquireTargetAction(self.engine, self.entity, obstacle).perform() # Acquire target.
                
    #         if isinstance(self.entity, CombatEntity):
    #             return EntityMeleeAction(self.engine, self.entity, obstacle).perform() # Immediate melee attack.


class InputDispatcher(GameEventDispatcher):

    def __init__(self, state: GameState | None = None) -> None:
        super().__init__(state)
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


class InterfaceDispatcher(GameEventDispatcher):
    pass

    # def ev_mapupdate(self) -> Sequence[BaseStateAction]:
    #     return [UIUpdateMapColorsAction(self.state)]


class SystemDispatcher(BaseEventDispatcher):
    def __init__(self, state: GameState | None = None) -> None:
        if state:
            self.state = state
            
    def _ev_gamestart(self, event: GameStart) -> List[BaseStateAction]:
        message = event.message
        # TODO: Message log

        return [self.create_action(GAMESTART)]
    
    def _ev_gameover(self, event: GameOver) -> List[BaseStateAction]:
        message = event.message
        # TODO: Message log

        return [self.create_action(GAMEOVER)]
    
    def _ev_keydown(self, event: tcod.event.KeyDown) -> List[BaseStateAction]:
        actions = [self.create_action(NOACTION)]

        if event.sym == tcod.event.KeySym.ESCAPE:
            actions += [self.create_action(SYSTEMEXIT)]

        return actions