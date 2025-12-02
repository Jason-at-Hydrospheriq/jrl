#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Set, Iterable, Any
from tcod.context import Context
from tcod.console import Console
from copy import copy   
from entities import Entity, Character
from game_map import GameMap
from event_handlers import ConsoleEventHandler, PlayerEventHandler, NonPlayerEventHandler
from actions import NoAction

class Engine:
    def __init__(self, player: Character, game_map: GameMap) -> None:
        self.console_entity = Entity(name='Console')
        self.player = player
        self.game_map = game_map
        self.console_event_handler = ConsoleEventHandler()
        self.player_event_handler = PlayerEventHandler()
        self.non_player_event_handler = NonPlayerEventHandler()
        self.active_non_player = None

    @property
    def agents(self) -> Iterable:
        handlers = [self.console_event_handler, self.player_event_handler, self.non_player_event_handler]
        actors = [self.console_entity, self.player, self.active_non_player]
        return zip(handlers, actors)
     
    def handle_events(self, events: Iterable[Any]) -> None:
        events_copy = list(events)
        for handler, actor in self.agents:
            action = handler.handle_events(events_copy)
            if actor:
                action.perform(self, actor)

    def render(self, console: Console, context: Context, view_mobs: bool=False) -> None:
        self.game_map.render(console, view_mobs=view_mobs)
        context.present(console, integer_scaling=True)
        console.clear()    