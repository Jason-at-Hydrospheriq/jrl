# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from core_components.state import GameState

class BaseGameAction(Protocol):
    """ A generic action that is dispatched by the AI to an action queue. Actions have a perform method that updates the game state when called."""
    state: GameState
    
    def perform(self) -> None:
        ...

