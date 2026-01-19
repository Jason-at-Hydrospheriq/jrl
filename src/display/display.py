#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.context import Context
import tcod
from PIL import Image
import os
import numpy as np

from display.widgets import HistoryViewerWidget, InventoryViewerWidget, MainMapDisplay, HealthBarWidget, MessageLogWidget, MouseTooltipWidget
from manifests import DEFAULT_TILEMAP_MANIFEST
from baseclasses import BaseUI, BaseUIWindow, WidgetRenderOrder as order
from entities.behaviors import InputEvent, system_behaviors, viewer_behaviors, selector_behaviors

from game_types import UIManifestDict

if TYPE_CHECKING:
    from store import GameStore
    from loop.components import SubLoopHandler

MAIN_CONSOLE_MANIFEST: UIManifestDict = {
    'widgets': {                
                        'main_map': {
                            'cls': MainMapDisplay,
                            'x': 1,
                            'y': 1,
                            'width': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][0][0],
                            'height': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][1][0],
                            'render_order': order.BACKGROUND
                        },
                        'player_health_bar': {
                            'cls': HealthBarWidget,
                            'x': 5,
                            'y': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][1][0] + 2,
                            'width': 20,
                            'height': 1,
                            'render_order': order.FOREGROUND
                                    },
                        'message_log': {
                            'cls': MessageLogWidget,
                            'x': 30,
                            'y': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][1][0] - 5,
                            'width': 20,
                            'height': 5,
                            'render_order': order.FOREGROUND
                        },
                        'mouse_tooltip': {
                            'cls': MouseTooltipWidget,
                            'mouse_x': 0,
                            'mouse_y': 0,
                            'render_order': order.FOREGROUND
                        },

    }}
HISTORY_CONSOLE_MANIFEST: UIManifestDict = {
    'widgets': {                
                        'history_viewer': {
                            'cls': HistoryViewerWidget,
                            'x': 5,
                            'y': 5,
                            'width': 75,
                            'height': 15,
                            'render_order': order.FOREGROUND
                        },

    }}
INVENTORY_CONSOLE_MANIFEST: UIManifestDict = {
    'widgets': {                
                        'inventory_viewer': {
                            'cls': InventoryViewerWidget,
                            'x': 5,
                            'y': 5,
                            'width': 30,
                            'height': 15,
                            'render_order': order.FOREGROUND
                        },

    }}

class GameDisplay(BaseUI):

    TITLE = "JRL - Jay's Roguelike"
    WIDTH, HEIGHT = 200, 96  # Window pixel resolution (when not maximized.)
    FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED
    src_path = os.path.dirname(os.path.abspath(__file__))
    TILESET = tcod.tileset.load_truetype_font("C:\\Users\\jason\\workspaces\\repos\\jrl\\src\\display\\graphics\\resources\\GoogleSansCode-SemiBold.ttf", 25, 25)

    def __init__(self, context: Context | None = None, ui_manifest: UIManifestDict | None = MAIN_CONSOLE_MANIFEST, store: GameStore | None = None) -> None:
        super().__init__(context=context, ui_manifest=ui_manifest)  
        self.store = store

        # Load Tileset Resources
        img = Image.open(os.path.join("display", "graphics", "resources", "player", "test-5.png"))
        img = img.convert("RGBA")
        self.TILESET.set_tile(64, np.array(img))
        img = Image.open(os.path.join("display", "graphics", "resources", "mob", "test-3.png"))
        img = img.convert("RGBA")
        self.TILESET.set_tile(65, np.array(img))
        
        self.add_window(BaseUIWindow(name="main_window", store=store, context=context, width=80, height=50, 
                                       widget_manifest=ui_manifest, is_rendered=True))
        self.machine.add_state('main')
        self.machine.add_transition('open_main', 'started', 'main')
        self.machine.add_transition('close_main', 'main', 'started')

        self.add_window(BaseUIWindow(name="history_window", store=store, context=context, width=75, height=15, 
                                       overlay_x=1, overlay_y=34, widget_manifest=HISTORY_CONSOLE_MANIFEST, is_rendered=False, 
                                       is_overlay=True))
        self.machine.add_state('history', on_enter='_open_history', on_exit='_close_history')
        self.machine.add_transition('open_history', 'main', 'history')
        self.machine.add_transition('close_history', 'history', 'main')
        self.machine.add_transition('open_history', 'inventory', 'history')

        self.add_window(BaseUIWindow(name="inventory_window", store=store, context=context, width=30, height=15, 
                                       overlay_x=1, overlay_y=34, widget_manifest=INVENTORY_CONSOLE_MANIFEST, is_rendered=False, 
                                       is_overlay=True))
        self.machine.add_state('inventory', on_enter='_open_inventory', on_exit='_close_inventory')
        self.machine.add_transition('open_inventory', 'main', 'inventory')
        self.machine.add_transition('close_inventory', 'inventory', 'main')
        self.machine.add_transition('open_inventory', 'history', 'inventory')

    def _start(self) -> None:
        """Initializes the display for rendering."""
        self.context = tcod.context.new(columns = self.WIDTH, rows = self.HEIGHT, tileset=self.TILESET, title=self.TITLE, vsync=True, sdl_window_flags=self.FLAGS)
        for window in self.windows:
            window.context = self.context
            window.console = self.context.new_console(window.width, window.height, order="F")

        print("Display has started.")

    def _stop(self) -> None:
        """Cleans up resources used by the display."""
        if self.context:
            self.context.close()
        print("Display has stopped.")
    
    def _open_inventory(self) -> None:                                        
        inventory_console = self.get_window_by_name('inventory_window')
        main_console = self.get_window_by_name('main_window')
        inventory_console.is_rendered=True

        for window in self.windows:
            if window is not inventory_console and window is not main_console:
                window.is_rendered=False

        self.ai.behaviors = selector_behaviors

        print("Inventory opened.")

    def _close_inventory(self) -> None:

        for window in self.windows:
            if window.name == 'inventory_window':
                window.is_rendered=False
        self.ai.behaviors = system_behaviors

        print("Inventory closed.")

    def _open_history(self) -> None:
        history_console = self.get_window_by_name('history_window')
        main_console = self.get_window_by_name('main_window')
        history_console.is_rendered=True

        for window in self.windows:
            if window is not history_console and window is not main_console:
                window.is_rendered=False
        self.ai.behaviors = viewer_behaviors

        print("History viewer opened.")

    def _close_history(self) -> None:
        for window in self.windows:
            if window.name == 'history_window':
                window.is_rendered=False
        self.ai.behaviors = system_behaviors

        print("History viewer closed.")

    def process_event(self, input_event: tcod.event.Event) -> None:
        if not self.is_stopped():  # type: ignore | Assume store is GameStore
            game_event = InputEvent(store=self.store, handler=self.ai, input_event=input_event)
            if self.ai:
                self.ai.handle(game_event)
