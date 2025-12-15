# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
    
from core_components.dispatchers.base import *
from core_components.events.library import GameStartEvent, GameOverEvent
from core_components.actions.library import GameStartAction, GameOverAction


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
        # self.mob_actions: List[BaseGameAction] = []

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

    # def ev_mapupdate(self) -> Sequence[BaseGameAction]:
    #     return [UIUpdateMapColorsAction(self.state)]


class SystemDispatcher(BaseEventDispatcher):
    GAMESTART = GameStartAction()
    GAMEOVER = GameOverAction()
    NOACTION = NoAction()
    SYSTEMEXIT = SystemExitAction()

    def _ev_gamestartevent(self, 
                      event: GameStartEvent, 
                      state: GameState) -> BaseGameAction:
        message = event.message
        # TODO: Message log

        return self.create_state_action(self.GAMESTART, state)
    
    def _ev_gameoverevent(self, 
                     event: GameOverEvent, 
                     state: GameState) -> BaseGameAction:
        message = event.message
        # TODO: Message log

        return self.create_state_action(self.GAMEOVER, state) 
    
    def _ev_keydownevent(self, 
                    event: tcod.event.KeyDown, 
                    state: GameState) -> BaseGameAction:
        state_action = self.create_state_action(self.NOACTION, state)

        if event.sym == tcod.event.KeySym.ESCAPE:
            state_action = self.create_state_action(self.SYSTEMEXIT, state)

        return state_action