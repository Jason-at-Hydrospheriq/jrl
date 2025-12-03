#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Iterable, Any, Protocol, TYPE_CHECKING
import tcod
import tcod.event

from actions import Action, ActionOnTarget, EscapeAction, MovementAction, NoAction, CollisionAction, SystemExitAction
from entities import Character

if TYPE_CHECKING:
    from engine import Engine

MOVEMENT_KEYS = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
}

class EventHandlerTemplate(Protocol):

    engine: Engine

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
    
    def event_quit(self, event: tcod.event.Quit) -> Action:
        ...

    def event_keydown(self, event: tcod.event.KeyDown) -> Action | ActionOnTarget:
        ...
    
    def handle_events(self) -> None:
        ...

    def _dispatch_events(self) -> Action | ActionOnTarget:
        ...
    

class EventHandler(EventHandlerTemplate):
    
    @property
    def player(self) -> Character:
        return self.engine.player
    
    def event_quit(self, event: tcod.event.Quit) -> Action:
        action: Action = SystemExitAction(self.player)

        return action
    
    def event_keydown(self, event: tcod.event.KeyDown) -> Action | ActionOnTarget:
        action: Action | ActionOnTarget = NoAction(self.player)
        
        if event.sym in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[event.sym]
            action = CollisionAction(self.player, dx, dy)
        
        elif event.sym == tcod.event.KeySym.ESCAPE:
            action = SystemExitAction(self.player)

        return action

    def handle_events(self) -> None:
        action = self._dispatch_events()
        
        action.perform()

        self.engine.handle_mob_actions()
        self.player.game_map.update_fov()

    def _dispatch_events(self) -> Action | ActionOnTarget:
        
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                return self.event_quit(event)
            elif isinstance(event, tcod.event.KeyDown):
                return self.event_keydown(event)
            
        return NoAction(self.player)