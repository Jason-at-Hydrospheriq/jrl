# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

# from __future__ import annotations
# from typing import TYPE_CHECKING, Set, Iterable, Any
# from tcod.context import Context
# from tcod.console import Console

# from event_handlers import EventHandler, MainEventHandler, GameOverEventHandler
# from entities import Charactor

# if TYPE_CHECKING:
#     from game_map import GameMap
    
# class Engine:
#     player: Charactor
    
#     def __init__(self, player: Charactor) -> None:
#         self.player = player
#         self._main_event_handler = MainEventHandler(self)
#         self._gameover_event_handler = GameOverEventHandler(self)
    
#     @property
#     def event_handler(self) -> EventHandler:
#         if self.gameover:
#             return self._gameover_event_handler
#         return self._main_event_handler
    
#     @property
#     def game_map(self) -> GameMap:
#         return self.player.game_map

#     @game_map.setter
#     def game_map(self, value: GameMap) -> None:
#         self.player.game_map = value

#     @property
#     def gameover(self) -> bool:
#         return not self.player.is_alive
    
#     def render(self, console: Console, context: Context, view_mobs: bool=False) -> None:
#         self.game_map.render(console, view_mobs=view_mobs)
#         hp_text = "HP: N/A"
#         if self.player.physical:
#             hp_text = f"HP: {self.player.physical.hp}/{self.player.physical.max_hp}"
        
#         console.print(
#             x=1,
#             y=105,
#             text=hp_text,
#             fg=(255, 0, 0),
#         )
    
#         context.present(console, integer_scaling=True)
#         console.clear()    