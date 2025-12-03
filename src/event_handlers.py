#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Generator, Iterable, Any, Protocol, TYPE_CHECKING
import tcod
import tcod.event

from actions import Action, ActionOnTarget, EscapeAction, MoveAction, NoAction, SystemExitAction
from entities import Charactor

if TYPE_CHECKING:
    from engine import Engine

MOVEMENT_KEYS = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
}

class EventHandler(Protocol):
    engine: Engine

    def handle_events(self) -> None:
        ...
    
    def _dispatch_events(self) -> Action:
        ...


class PlayerEventHandler:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @property
    def player(self) -> Charactor:
        return self.engine.player

    def handle_events(self) -> None:
        player_action = self._dispatch_events()
        player_action.perform()
        
    def _event_quit(self, event: tcod.event.Quit) -> Action:
        action: Action = SystemExitAction(self.player)

        return action
    
    def _event_keydown(self, event: tcod.event.KeyDown) -> Action:
        action: Action = NoAction(self.player)
        
        if event.sym in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[event.sym]
            action = MoveAction(self.player, dx, dy)
        
        elif event.sym == tcod.event.KeySym.ESCAPE:
            action = SystemExitAction(self.player)

        return action

    def _dispatch_events(self) -> Action:
        
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                return self._event_quit(event)
            elif isinstance(event, tcod.event.KeyDown):
                return self._event_keydown(event)
            
        return NoAction(self.player)
    

class MobEventsHandler:

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def mobs(self) -> Generator[Charactor]:
        return self.engine.game_map.live_ai_actors

    def handle_events(self) -> None:
        for mob in self.mobs():
            if mob.event_handler:
                mob_action = mob.event_handler._dispatch_events()
                mob_action.perform()


class GameOverEventHandler(EventHandler):

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def handle_events(self) -> None:
        game_over_action = self._dispatch_events()
        game_over_action.perform()

    def _event_quit(self, event: tcod.event.Quit) -> Action:
        action: Action = SystemExitAction(self.engine.player)

        return action

    def _event_keydown(self, event: tcod.event.KeyDown) -> Action:
        action: Action = NoAction(self.engine.player)

        if event.sym == tcod.event.KeySym.ESCAPE:
            action = SystemExitAction(self.engine.player)

        return action

    def _dispatch_events(self) -> Action:

        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                return self._event_quit(event)
            elif isinstance(event, tcod.event.KeyDown):
                return self._event_keydown(event)

        return NoAction(self.engine.player)