#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.console import Console
from tcod.context import Context
import numpy as np

from core_components.ui.interfaces import BaseUIWidget
from core_components.ui.graphics import colors

if TYPE_CHECKING:
    from state import GameState

from core_components.ui.graphics.tile_types import SHROUD


class HealthBarWidget(BaseUIWidget):
    """ A simple health bar widget to display an entity's health. """
    def __init__(self, name: str, *, upper_Left_x: int = 0, upper_Left_y: int=0, width: int=50, height: int=5) -> None:
        self.name = name
        self.upper_Left_x = upper_Left_x
        self.upper_Left_y = upper_Left_y
        self.lower_Right_x = upper_Left_x + width
        self.lower_Right_y = upper_Left_y + height
        self.width = width
        self.height = height

    def render(self, context: Context, console: Console, state: GameState) -> None:
        bar_width = 0
        current_value = 0
        maximum_value = 1

        if state.roster.player is not None:
            current_value = state.roster.player.physical.hp # type: ignore
            maximum_value = state.roster.player.physical.max_hp # type: ignore
        
        bar_width = int(float(current_value) / maximum_value * self.width)

        console.draw_rect(x=self.upper_Left_x, y=self.upper_Left_y, width=self.width, height=self.height, ch=1, bg=colors.bar_empty)

        if bar_width > 0:
            console.draw_rect(
                x=self.upper_Left_x, y=self.upper_Left_y, width=bar_width, height=self.height, ch=1, bg=colors.bar_filled
            )

        console.print(
            x=self.upper_Left_x, y=self.upper_Left_y, text=f"Player HP: {current_value}/{maximum_value}", fg=colors.bar_text
        )


class MainMapDisplay(BaseUIWidget):
    """ The main map display widget. """
    def __init__(self, name: str, *, upper_Left_x: int = 0, upper_Left_y: int=0, width: int=50, height: int=5) -> None:
        self.name = name
        self.upper_Left_x = upper_Left_x
        self.upper_Left_y = upper_Left_y
        self.lower_Right_x = upper_Left_x + width
        self.lower_Right_y = upper_Left_y + height
        self.width = width
        self.height = height

    def render(self, context: Context, console: Console, state: GameState) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        player = state.roster.player
        game_map = state.map.active
        actors = state.roster.live_actors
        # console_width = self.width
        # console_height = self.height

        # if context.sdl_window is not None:
        #     window_width = context.sdl_window.size[0] // 20
        #     window_height = context.sdl_window.size[1] // 20
        #     console_width = window_width - 5
        #     console_height = window_height - 5

        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[game_map.visible, game_map.seen],
            choicelist=[game_map.tiles['graphic_type']['visible'], game_map.tiles['graphic_type']['explored']],
            default=SHROUD,
        ) 

        if len(actors) > 0:
            for actor in state.roster.live_actors:
                if actor.is_spotted:
                    console.print(actor.location.x, actor.location.y, actor.symbol, fg=actor.color)
        if player:
            console.print(player.location.x, player.location.y, player.symbol, fg=player.color)
    
    # def print_entities(self, entities, key, tile_map: GraphicTileMap) -> None:
    #     for entity in sorted(entities, key=key, reverse=False):
    #         if tile_map.is_visible(entity.location):
    #             self.console.print(entity.location.x, entity.location.y, entity.char, fg=entity.color)

    # def render(self, state) -> None:
    #     x_slice = slice(self.upper_Left_x, self.lower_Right_x)
    #     y_slice = slice(self.upper_Left_y, self.lower_Right_y)
        
    #     # Render Tiles
    #     self.console.rgb[x_slice, y_slice] = state[:self.width, :self.height]
    
        # # Render Actors in order of their is_alive status
        # self.print_entities(engine.roster.all_actors, key=lambda e: hasattr(e, 'is_alive'), tile_map=tile_map)

        # # Render Non-Actors in order of their blocks_movement status
        # self.print_entities(engine.roster.all_non_actors, key=lambda e: hasattr(e, 'blocks_movement'), tile_map=tile_map)


class MessageLogWidget(BaseUIWidget):
    """ A simple message log widget to display game messages. """
    def __init__(self, name: str, *, upper_Left_x: int = 0, upper_Left_y: int=0, width: int=50, height: int=5) -> None:
        self.name = name
        self.upper_Left_x = upper_Left_x
        self.upper_Left_y = upper_Left_y
        self.lower_Right_x = upper_Left_x + width
        self.lower_Right_y = upper_Left_y + height
        self.width = width
        self.height = height

    def render(self, context: Context, console: Console, state: GameState) -> None:
        y = self.upper_Left_y + self.height - 1
        for message in reversed(state.log.messages[-self.height :]):
            console.print(
                x=self.upper_Left_x,
                y=y,
                text=message.plain_text,
                fg=message.fg,
            )
            y -= 1