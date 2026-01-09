# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Protocol, runtime_checkable

@runtime_checkable
class BaseGameAction(Protocol):
    """ A generic action that is dispatched by the AI to an action queue. Actions have a perform method that updates the game state when called."""
    
    def perform(self) -> None:
        ...

