#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Set, Iterable, Any
from tcod.context import Context
from tcod.console import Console

from event_handlers import PlayerEventHandler, MobEventsHandler
from entities import Charactor

if TYPE_CHECKING:
    from game_map import GameMap
    
class Engine:
    player: Charactor
    player_event_handler: PlayerEventHandler
    mob_event_handler: MobEventsHandler

    def __init__(self, player: Charactor) -> None:
        self.player = player
        self.player_event_handler = PlayerEventHandler(self)
        self.mob_event_handler = MobEventsHandler(self)
   
    @property
    def game_map(self) -> GameMap:
        return self.player.game_map

    @game_map.setter
    def game_map(self, value: GameMap) -> None:
        self.player.game_map = value

    def render(self, console: Console, context: Context, view_mobs: bool=False) -> None:
        self.game_map.render(console, view_mobs=view_mobs)
        hp_text = "HP: N/A"
        if self.player.physical:
            hp_text = f"HP: {self.player.physical.hp}/{self.player.physical.max_hp}"
        
        console.print(
            x=1,
            y=105,
            text=hp_text,
            fg=(255, 0, 0),
        )
    
        context.present(console, integer_scaling=True)
        console.clear()    