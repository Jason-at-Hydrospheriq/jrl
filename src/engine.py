#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Set, Iterable, Any
from tcod.context import Context
from tcod.console import Console

from event_handlers import EventHandler
from actions import NoAction
from entities import Character

if TYPE_CHECKING:
    from game_map import GameMap
    
class Engine:
    player: Character
    event_handler: EventHandler

    def __init__(self, player: Character) -> None:
        self.player = player
        self.event_handler = EventHandler(self)
   
    @property
    def game_map(self) -> GameMap:
        return self.player.game_map

    @game_map.setter
    def game_map(self, value: GameMap) -> None:
        self.player.game_map = value

    def handle_mob_actions(self) -> None:
        for entity in self.game_map.non_player_entities:
            if isinstance(entity, Character):
                mob_action = NoAction(entity)
                mob_action.perform()

    def render(self, console: Console, context: Context, view_mobs: bool=False) -> None:
        self.game_map.render(console, view_mobs=view_mobs)
        context.present(console, integer_scaling=True)
        console.clear()    