# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, Sequence, TYPE_CHECKING
import tcod
import tcod.event

from resources.events import BaseGameEvent

if TYPE_CHECKING:
    from engine import Engine

from resources.actions import BaseAction, SystemExitAction


class BaseEventDispatcher(Protocol):
    engine: Engine
    action_sequence: Sequence[BaseAction]
    
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def dispatch(self, event: tcod.event.Event | BaseGameEvent) -> Sequence[BaseAction]:
        method_name = "_ev_" + event.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method:
            return method(event)
        return []
    
    def _ev_quit(self, event: tcod.event.Quit) -> Sequence[BaseAction]:
        return [SystemExitAction()]

    
