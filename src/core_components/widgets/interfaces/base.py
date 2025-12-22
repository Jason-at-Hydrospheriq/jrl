#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Any, Protocol, Set, Dict, TypedDict, TYPE_CHECKING
from tcod.context import Context
from tcod.console import Console
from transitions import Machine

from core_components.maps.tilemaps import DEFAULT_MANIFEST

if TYPE_CHECKING:
    from core_components.store import GameStore

class UIManifestDict(TypedDict):
    widgets: Dict[str, Dict[str, Any]]


class BaseUI:
    machine: Machine
    context: Context
    console: Console
    state: GameStore
    widgets: Set[BaseUIWidget]
    context_width: int
    context_height: int
    console_width: int
    console_height: int

    """ The UI Manager handles the various UI components and their interactions. """
    
    def __init__(self, context: Context | None = None, state: GameStore | None = None, ui_manifest: UIManifestDict | None = None, *, context_width: int = 80, context_height: int = 50) -> None:

        if context is not None:
            self.context = context

        if state is not None:
            self.state = state

        self.widgets = set()
        self.context_width = context_width
        self.context_height = context_height
        # if self.state.map.active is not None:
        #     self.console_width, self.console_height = self.state.map.active.tiles.shape
        # else:
        #     self.console_width = context_width
        #     self.console_height = context_height
            
        if ui_manifest is not None:
            self.console_width = DEFAULT_MANIFEST['dimensions']['grid_size'][0][0]
            self.console_height = DEFAULT_MANIFEST['dimensions']['grid_size'][1][0]

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
        if self.context.sdl_window is not None:
            # console_width, console_height = self.context.sdl_window.size
            self.console = self.context.new_console(self.console_width, self.console_height, order="F")
            for widget in self.widgets:
                widget.render(self.context, self.console, self.state)
            self.context.present(self.console)
            self.console.clear()  


class BaseUIWidget(Protocol):
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


    def render(self, context: Context, console: Console, state: GameStore) -> None:
        """ Render the UI component """
        raise NotImplementedError()