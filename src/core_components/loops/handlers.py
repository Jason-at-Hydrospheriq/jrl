#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set, Tuple
import tcod

from core_components.loops.base import StateTransformer, StateTransitionObject, GameEvent, GameAction
from core_components.loops.actions import NoAction
from core_components.loops.events import NonEvent


class Handler(StateTransformer):
    """The Handler is responsible for tranforming Game Inputs and AI Actions into Game Events
    and sending them to the State Action Queue."""

    templates: Set[Tuple[str, StateTransitionObject]]
    
    def __init__(self):
        super().__init__()
        self.templates = {
                        ('noaction', NonEvent()),
                        ('nonevent', NoAction()),
                        }
    
    def dispatch(self, event: GameEvent) -> bool:
        return super()._enqueue(event)   
        
    def handle(self, event: GameAction | tcod.event.Event | None = None) -> bool:
        if event is not None:
            if isinstance(event, tcod.event.Event):
                # Handle tcod event conversion to GameEvent here if needed
                pass

            parsed_event: GameAction | GameEvent = event  # type: ignore

            return super()._enqueue(parsed_event)
        
        return False
