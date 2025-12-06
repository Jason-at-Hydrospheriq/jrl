# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
import tcod
import tcod.event

from src.resources.actions import BaseAction, NoAction, SystemExitAction
from components.dispatch.base import BaseEventDispatcher
from resources.events import GameOver

if TYPE_CHECKING:
    from engine import Engine
    

class GameOverDispatcher(BaseEventDispatcher):
    def __init__(self, engine: Engine | None = None) -> None:

        if engine:
            self.engine = engine

        self.action_sequence: Sequence[BaseAction] = []

    def _ev_gameover(self, event: GameOver) -> Sequence[BaseAction]:
        return [NoAction()]
    
    def _ev_keydown(self, event: tcod.event.KeyDown) -> Sequence[BaseAction]:
        actions = [NoAction()]

        if event.sym == tcod.event.KeySym.ESCAPE:
            actions += [SystemExitAction()]

        return actions
