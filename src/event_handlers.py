#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Generator, Iterable, Any, Protocol, TYPE_CHECKING
import tcod
import tcod.event

from actions import Action, ActionOnTarget, EscapeAction, MoveAction, NoAction, SystemExitAction
from entities import AICharactor, Charactor
from components.ai import HostileAI

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
            destination = self.player.game_map.get_map_coords(self.player.location.x + dx, self.player.location.y + dy)
            action = MoveAction(self.player, destination)
        
        elif event.sym == tcod.event.KeySym.ESCAPE:
            action = SystemExitAction(self.player)

        self.engine.mob_event_handler.handle_events()

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
        self.actions = []

    @property
    def mobs(self) -> Generator[AICharactor]:
        yield from (mob for mob in self.engine.game_map.live_ai_actors if isinstance(mob.ai, HostileAI))

    def handle_events(self) -> None:
        self._dispatch_events()
        
        for action in self.actions:
            action.perform()

    def _dispatch_events(self) -> None:
        self.actions = []
        for mob in self.mobs:
            if mob.ai and mob.in_player_fov:
                self.actions += [mob.ai.event().to_action()]

        return None


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