# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import List, TYPE_CHECKING, Sequence

from resources.actions import *
from components.dispatch.base import BaseEventDispatcher


if TYPE_CHECKING:
    from engine import Engine
    

class InterfaceDispatcher(BaseEventDispatcher):
    
    def __init__(self, engine: Engine | None = None) -> None:

        if engine:
            self.engine = engine

        self.action_sequence: Sequence[BaseAction] = []

    def ev_mapupdate(self, event: MapUpdate) -> Sequence[BaseAction]:
        return []