#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, Tuple, Set, TypedDict
from tcod.console import Console
from tcod.context import Context
import numpy as np
from transitions import Machine

if TYPE_CHECKING:
    from store import GameStore

from display_components.graphics import colors
from display_components.graphics.tile_types import SHROUD
from atlas.components.tilemaps import DEFAULT_TILEMAP_MANIFEST

class BaseUI:
    store: GameStore | None
    machine: Machine
    context: Context | None
    console: Console | None
    widgets: Set[BaseUIWidget]
    context_width: int
    context_height: int
    console_width: int
    console_height: int

    """ The UI Manager handles the various UI components and their interactions. """
    
    def __init__(self, context: Context | None = None, store: GameStore | None = None, ui_manifest: UIManifestDict | None = None, *, context_width: int = 80, context_height: int = 50) -> None:

        if context is not None:
            self.context = context

        if store is not None:
            self.store = store

        self.widgets = set()
        self.context_width = context_width
        self.context_height = context_height
        # if self.state.map.active is not None:
        #     self.console_width, self.console_height = self.state.map.active.tiles.shape
        # else:
        #     self.console_width = context_width
        #     self.console_height = context_height
            
        if ui_manifest is not None:
            self.console_width = DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][0][0]
            self.console_height = DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][1][0]

            for widget_name, widget_info in ui_manifest['widgets'].items():
                widget_cls = widget_info['cls']
                x = widget_info.get('x', 0)
                y = widget_info.get('y', 0)
                width = widget_info.get('width', 10)
                height = widget_info.get('height', 5)
                widget = widget_cls(widget_name, upper_Left_x=x, upper_Left_y=y, width=width, height=height)
                self.add_widget(widget=widget, x=x, y=y)


        states = ['idle', 
                    {'name': 'started', 'on_enter': '_start'}, 
                    {'name': 'stopped', 'on_enter': '_stop'}]
        transitions =[
            {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
            {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
            ]
        self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')

    def _start(self) -> None:
        ...

    def _stop(self) -> None:
        ...
        
    def add_widget(self, *, widget: BaseUIWidget, x: int = -1, y: int = -1) -> None:
        """Spawn a copy of this entity at the given location."""
        widget.upper_Left_x = x
        widget.upper_Left_y = y
        widget.lower_Right_x = x + widget.width
        widget.lower_Right_y = y + widget.height
        self.widgets.add(widget)
    
    def get_widget_by_name(self, name: str) -> BaseUIWidget | None:
        """Retrieve a UI element by its name."""
        for widget in self.widgets:
            if widget.name == name:
                return widget
        return None
    
    def get_widgets_by_type(self, widget_type: type) -> Set[BaseUIWidget]:
        """Retrieve all UI elements of a specific type."""
        return {widget for widget in self.widgets if isinstance(widget, widget_type)}

    def render(self) -> None:
        if self.context and self.store:
            if self.context.sdl_window is not None:
                # console_width, console_height = self.context.sdl_window.size
                self.console = self.context.new_console(self.console_width, self.console_height, order="F")
                for widget in self.widgets:
                    widget.render(self.context, self.console, self.store)
                self.context.present(self.console)
                self.console.clear()  


class BaseUIWidget:
    name: str
    upper_Left_x: int
    upper_Left_y: int
    lower_Right_x: int
    lower_Right_y: int
    width: int
    height: int

    def __init__(self, name: str, x: int, y: int, width: int, height: int):
        self.name = name
        self.upper_Left_x = x
        self.upper_Left_y = y
        self.lower_Right_x = x + width
        self.lower_Right_y = y + height
        self.width = width
        self.height = height


    def render(self, context: Context, console: Console, store: GameStore) -> None:
        """ Render the UI component """
        raise NotImplementedError()
    

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
    def __init__(self, name: str, *, upper_Left_x: int = 0, upper_Left_y: int=0, width: int=50, height: int=5) -> None:
        self.name = name
        self.upper_Left_x = upper_Left_x
        self.upper_Left_y = upper_Left_y
        self.lower_Right_x = upper_Left_x + width
        self.lower_Right_y = upper_Left_y + height
        self.width = width
        self.height = height

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

            for actor in store.portfolio.live_actors:
                if actor.location and visible[*actor.location.to_list]:
                    if not actor.perception.is_targeted():  # type: ignore | State machine method is dynamically added
                        color = actor.color
                    elif actor.perception.is_targeted():  # type: ignore | State machine method is dynamically added
                        color = colors.enemy_atk
                    console.print(actor.location.x, actor.location.y, actor.symbol, fg=color)

            if player and player.location:
                console.print(player.location.x, player.location.y, player.symbol, fg=player.color)


class Message:
    """ A single message for the message log. """
    def __init__(self, text: str, fg: Tuple[int, int, int] = colors.white) -> None:
        self.plain_text = text
        self.fg= fg
        self.count = 1
        if self.count > 1:
            self.text = f"{self.plain_text} (x{self.count})"


class MessageLog:
    """ A simple message log widget to display game messages. """
    def __init__(self) -> None:
        self.messages: list[Message] = []
        
    def add(self, text: str, fg: Tuple[int, int, int] = colors.white, stack: bool = True) -> None:
        """Add a message to this log.
        `text` is the message text, `fg` is the text color.
        If `stack` is True then the message can stack with a previous message
        of the same text.
        """
        if stack and self.messages and text == self.messages[-1].plain_text:
            self.messages[-1].count += 1
        else:
            self.messages.append(Message(text, fg))   


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

    def render(self, context: Context, console: Console, store: GameStore) -> None:
        y = self.upper_Left_y + self.height - 1
        for message in reversed(store.log.messages[-self.height :]):
            console.print(
                x=self.upper_Left_x,
                y=y,
                text=message.plain_text,
                fg=message.fg,
            )
            y -= 1


class UIManifestDict(TypedDict):
    widgets: Dict[str, Dict[str, Any]]