#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Iterable, Any
import tcod
from tcod.event import KeyDown, Quit

from actions import Action, ActionOnTarget, EscapeAction, MovementAction, NoAction, CollisionAction

MOVEMENT_KEYS = {
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
}

class EventHandler():
    def handle_events(self, events: Iterable[Any]) -> Action|ActionOnTarget:
        """Handle a list of events. This method should be overridden by subclasses.

        Args:
            events: A list of events to handle.

        Returns:
            Action: The action to be performed in response to the events.
        """
        raise NotImplementedError()


class ConsoleEventHandler(EventHandler):
    def handle_events(self, events: Iterable[Any]) -> Action:
        action = NoAction()

        for event in events:
            match event:
                
                case Quit():
                    raise SystemExit()
                
                case KeyDown(sym=sym):
                    if sym == tcod.event.KeySym.ESCAPE:
                        action = EscapeAction()
                
                case tcod.event.WindowResized(width=width, height=height):  # Size in pixels
                        pass  # The next call to context.new_console may return a different size.
        return action


class PlayerEventHandler(EventHandler):
    def handle_events(self, events: Iterable[Any]) -> Action | ActionOnTarget:
        action = NoAction()

        for event in events:
            match event:
                case KeyDown(sym=sym):
                    if sym in MOVEMENT_KEYS:
                        dx, dy = MOVEMENT_KEYS[sym]
                        action = CollisionAction(dx, dy)
                
        return action
    

class NonPlayerEventHandler(EventHandler):
    def handle_events(self, events: Iterable[Any]) -> Action | ActionOnTarget:
        action = NoAction()

        # for event in events:
        #     match event:

        #         case KeyDown(sym=sym):
        #             if sym in MOVEMENT_KEYS:
        #                 dx, dy = MOVEMENT_KEYS[sym]
        #                 action = CollisionAction(dx, dy)

        return action
        