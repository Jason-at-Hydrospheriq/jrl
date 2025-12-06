# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, TYPE_CHECKING, Sequence
import tcod
import tcod.event

from src.resources.actions import *
from components.dispatch.base import BaseEventDispatcher

# from entities import AICharactor, Charactor
# from components.ai import HostileAI

if TYPE_CHECKING:
    from engine import Engine

MOVEMENT_KEYS = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.W: (0, -1),
    tcod.event.KeySym.S: (0, 1),
    tcod.event.KeySym.A: (-1, 0),
    tcod.event.KeySym.D: (1, 0),
}
    

class InputDispatcher(BaseEventDispatcher):

    def __init__(self, engine: Engine | None = None) -> None:

        if engine:
            self.engine = engine

        self.action_sequence: Sequence[BaseAction] = []
        self.mob_actions: List[BaseAction] = []

    # @property
    # def mobs(self) -> Generator[AICharactor]:
    #     yield from (mob for mob in self.engine.roster.live_ai_actors if isinstance(mob.ai, HostileAI))
    
    def _ev_keydown(self, event: tcod.event.KeyDown) -> Sequence[BaseAction]:
        actions = [NoAction()]

        if event.sym == tcod.event.KeySym.ESCAPE:
            actions += [SystemExitAction()]
        
        if event.sym in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[event.sym]
            destination = self.engine.game_map.get_map_coords(self.engine.roster.player.location.x + dx, self.engine.roster.player.location.y + dy)
            actions += [EntityMoveAction(self.engine, self.engine.roster.player, destination)]
        
        # if self.mob_actions:
        #     while self.mob_actions:
        #         action = self.mob_actions.pop(0)

        #         if issubclass(action.__class__, ActionOnTarget) or issubclass(action.__class__, ActionOnDestination):
        #             actions += [action]
        #         else:
        #             unused_actions += [action]
            
        #     self.mob_actions = unused_actions

        return actions
