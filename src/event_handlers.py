#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Generator, Iterable, Any, List, Optional, Protocol, TYPE_CHECKING, Sequence
import tcod
import tcod.event

from actions import Action, ActionOnDestination, ActionOnTarget, EscapeAction, MoveAction, NoAction, SystemExitAction
from entities import AICharactor, Charactor
from components.ai import HostileAI

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

class EventHandler(Protocol):
    engine: Engine

    @property
    def player(self) -> Charactor:
        return self.engine.player
    
    def handle_events(self) -> None:
        ...
    
    def dispatch(self, event: tcod.event.Event) -> Sequence[Action]:
        method_name = "_ev_" + event.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method:
            return method(event)
        return []
    
    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
       raise SystemExit()
    

class MainEventHandler(EventHandler):

    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.action_sequence: Sequence[Action] = []
        self.mob_actions: List[Action] = []

    @property
    def mobs(self) -> Generator[AICharactor]:
        yield from (mob for mob in self.engine.game_map.live_ai_actors if isinstance(mob.ai, HostileAI))

    def handle_events(self) -> None:

        # Clear previous actions
        self.mob_actions = []
        self.action_sequence = []

        for mob in self.mobs: # Collect mob actions
            if mob.ai and mob.in_player_fov:
                self.mob_actions += [mob.ai.event().to_action()]

        # Create action sequence
        for event in tcod.event.wait():
            self.action_sequence += self.dispatch(event)
        
        # Perform actions
        for action in self.action_sequence:
            action.perform()

        if self.mob_actions:
            for action in self.mob_actions:
                action.perform()

    def _ev_quit(self, event: tcod.event.Quit) -> Sequence[Action]:
        return [SystemExitAction(self.player)]
    
    def _ev_keydown(self, event: tcod.event.KeyDown) -> Sequence[Action]:
        actions = [NoAction(self.player)]
        unused_actions = []

        if event.sym == tcod.event.KeySym.ESCAPE:
            return [SystemExitAction(self.player)]
        
        if event.sym in MOVEMENT_KEYS:
            dx, dy = MOVEMENT_KEYS[event.sym]
            destination = self.player.game_map.get_map_coords(self.player.location.x + dx, self.player.location.y + dy)
            actions += [MoveAction(self.player, destination)]
        
        if self.mob_actions:
            while self.mob_actions:
                action = self.mob_actions.pop(0)

                if issubclass(action.__class__, ActionOnTarget) or issubclass(action.__class__, ActionOnDestination):
                    actions += [action]
                else:
                    unused_actions += [action]
            
            self.mob_actions = unused_actions

        return actions
    

class GameOverEventHandler(EventHandler):
    def __init__(self, engine: Engine | None = None) -> None:

        if engine:
            self.engine = engine

    def handle_events(self) -> None:
        for event in tcod.event.wait():
            actions = self.dispatch(event)

            if actions is None:
                continue
                
            for action in actions:
                action.perform()

    def _ev_keydown(self, event: tcod.event.KeyDown) -> Sequence[Action]:

        if event.sym == tcod.event.KeySym.ESCAPE:
            action = EscapeAction(self.player)

            # No valid key was pressed
            return [action]
        
        return []