#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.console import Console
from tcod.context import Context
import numpy as np

from baseclasses import BaseUIWidget

if TYPE_CHECKING:
    from store import GameStore

import colors
from game_types import SHROUD
from baseclasses import WidgetRenderOrder


class HealthBarWidget(BaseUIWidget):
    """ A simple health bar widget to display an entity's health. """
    def __init__(self, name: str, *, upper_Left_x: int = 0, upper_Left_y: int=0, width: int=50, height: int=5, render_order: WidgetRenderOrder) -> None:
        self.name = name
        self.upper_Left_x = upper_Left_x
        self.upper_Left_y = upper_Left_y
        self.lower_Right_x = upper_Left_x + width
        self.lower_Right_y = upper_Left_y + height
        self.width = width
        self.height = height
        self.render_order = render_order

    def render(self, context: Context, console: Console, store: GameStore) -> None:
        bar_width = 0
        current_value = 0
        maximum_value = 1

        if store.portfolio and store.portfolio.player is not None:
            current_value = store.portfolio.player.hp 
            maximum_value = store.portfolio.player.max_hp

        if current_value and maximum_value:
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
    def __init__(self, name: str, *, upper_Left_x: int = 0, upper_Left_y: int=0, width: int=50, height: int=5, render_order: WidgetRenderOrder) -> None:
        self.name = name
        self.upper_Left_x = upper_Left_x
        self.upper_Left_y = upper_Left_y
        self.lower_Right_x = upper_Left_x + width
        self.lower_Right_y = upper_Left_y + height
        self.width = width
        self.height = height
        self.render_order = render_order

    def render(self, context: Context, console: Console, store: GameStore) -> None:
        """
        Renders the map.

        If a tile is in the "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        player = None
        game_map = None

        if store.atlas and store.portfolio is not None:
            player = store.portfolio.player
            game_map = store.atlas.active  # type: ignore | Assume store is GameStore  

        if game_map:
            tile_map = np.select(
                condlist=[game_map.visible, game_map.seen],
                choicelist=[game_map.tiles['graphic_type']['visible'], game_map.tiles['graphic_type']['explored']],
                default=SHROUD,
            ) 
            console.rgb[0 : self.width, 0 : self.height] = tile_map

        if store.portfolio and store.atlas:
            visible = store.atlas.active.visible
            color = colors.white

            for actor in store.portfolio.all_ai_actors:
                if actor.location and visible[*actor.location.to_list]:
                    if not actor.perception.is_targeted():  # type: ignore | State machine method is dynamically added
                        color = actor.color
                    elif actor.perception.is_targeted():  # type: ignore | State machine method is dynamically added
                        color = colors.enemy_atk
                    console.print(actor.location.x, actor.location.y, actor.symbol, fg=color)

            if player and player.location:
                console.print(player.location.x, player.location.y, player.symbol, fg=player.color)


class MessageLogWidget(BaseUIWidget):
    """ A simple message log widget to display game messages. """
    def __init__(self, name: str, *, upper_Left_x: int = 0, upper_Left_y: int=0, width: int=50, height: int=5, render_order: WidgetRenderOrder) -> None:
        self.name = name
        self.upper_Left_x = upper_Left_x
        self.upper_Left_y = upper_Left_y
        self.lower_Right_x = upper_Left_x + width
        self.lower_Right_y = upper_Left_y + height
        self.width = width
        self.height = height
        self.render_order = render_order

    def render(self, context: Context, console: Console, store: GameStore) -> None:
        y = self.upper_Left_y + self.height - 1
        for message in reversed(store.log.messages[-self.height :]):
            console.print(
                x=self.upper_Left_x,
                y=y,
                text=message.full_text,
                fg=message.fg,
            )
            y -= 1

            if y < self.upper_Left_y:
                return


