#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.context import Context
import tcod
from PIL import Image
from transitions import Machine
import os
import numpy as np

from core_components.widgets.interfaces import *
from core_components.widgets.interfaces import HealthBarWidget, MainMapDisplay, MessageLogWidget
from core_components.maps.tilemaps import DEFAULT_MANIFEST

if TYPE_CHECKING:
    from core_components.store import GameStore


DEFAULT_UI_MANIFEST: UIManifestDict = {
    'widgets': {                
                        'main_map': {
                            'cls': MainMapDisplay,
                            'x': 1,
                            'y': 1,
                            'width': DEFAULT_MANIFEST['dimensions']['grid_size'][0][0],
                            'height': DEFAULT_MANIFEST['dimensions']['grid_size'][1][0]},
                        'player_health_bar': {
                            'cls': HealthBarWidget,
                            'x': 5,
                            'y': DEFAULT_MANIFEST['dimensions']['grid_size'][1][0] + 2,
                            'width': 20,
                            'height': 1
                                    },
                        'message_log': {
                            'cls': MessageLogWidget,
                            'x': 30,
                            'y': DEFAULT_MANIFEST['dimensions']['grid_size'][1][0] - 5,
                            'width': 20,
                            'height': 5
                        }

    }}


class Display(BaseUI):
    machine: Machine
    context: tcod.context.Context

    TITLE = "JRL - Jay's Roguelike"
    WIDTH, HEIGHT = 200, 96  # Window pixel resolution (when not maximized.)
    FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED
    TILESET = tcod.tileset.load_truetype_font(os.path.join("src","core_components", "ui", "graphics", "resources", "GoogleSansCode-SemiBold.ttf"), 25, 25)

    def __init__(self, context: Context | None = None, ui_manifest: UIManifestDict | None = DEFAULT_UI_MANIFEST) -> None:
        super().__init__(context=context, ui_manifest=ui_manifest)  
        
        def __init__(self) -> None:
            states = ['idle', 
                        {'name': 'started', 'on_enter': '_start'}, 
                        {'name': 'stopped', 'on_enter': '_stop'}]
            transitions =[
                {'trigger': 'start', 'source': 'stopped', 'dest': 'started'},
                {'trigger': 'stop', 'source': 'started', 'dest': 'stopped'}
                ]
            self.machine = Machine(model=self, states=states, transitions=transitions, initial='stopped')

            img = Image.open(os.path.join("src","core_components", "ui", "graphics", "resources", "player", "test-5.png"))
            img = img.convert("RGBA")
            self.TILESET.set_tile(64, np.array(img))
            img = Image.open(os.path.join("src","core_components", "ui", "graphics", "resources", "mob", "test-3.png"))
            img = img.convert("RGBA")
            self.TILESET.set_tile(65, np.array(img))

    def _start(self) -> None:
        """Initializes the display for rendering."""
        self.context = tcod.context.new(columns = self.WIDTH, rows = self.HEIGHT, tileset=self.TILESET, title=self.TITLE, vsync=True, sdl_window_flags=self.FLAGS)

        print("Display has started.")

    def _stop(self) -> None:
        """Cleans up resources used by the display."""
        self.context.close()
        print("Display has stopped.")