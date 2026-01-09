#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.context import Context
import tcod
from PIL import Image
import os
import numpy as np

from display.widgets import MainMapDisplay, HealthBarWidget, MessageLogWidget
from manifests import DEFAULT_TILEMAP_MANIFEST
from game_baseclasses import BaseUI
from game_types import UIManifestDict

if TYPE_CHECKING:
    from store import GameStore


DEFAULT_UI_MANIFEST: UIManifestDict = {
    'widgets': {                
                        'main_map': {
                            'cls': MainMapDisplay,
                            'x': 1,
                            'y': 1,
                            'width': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][0][0],
                            'height': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][1][0]},
                        'player_health_bar': {
                            'cls': HealthBarWidget,
                            'x': 5,
                            'y': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][1][0] + 2,
                            'width': 20,
                            'height': 1
                                    },
                        'message_log': {
                            'cls': MessageLogWidget,
                            'x': 30,
                            'y': DEFAULT_TILEMAP_MANIFEST['dimensions']['grid_size'][1][0] - 5,
                            'width': 20,
                            'height': 5
                        }

    }}


class GameDisplay(BaseUI):

    TITLE = "JRL - Jay's Roguelike"
    WIDTH, HEIGHT = 200, 96  # Window pixel resolution (when not maximized.)
    FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED
    src_path = os.path.dirname(os.path.abspath(__file__))
    TILESET = tcod.tileset.load_truetype_font("C:\\Users\\jason\\workspaces\\repos\\jrl\\src\\display\\graphics\\resources\\GoogleSansCode-SemiBold.ttf", 25, 25)

    def __init__(self, context: Context | None = None, ui_manifest: UIManifestDict | None = DEFAULT_UI_MANIFEST, store: GameStore | None = None) -> None:
        super().__init__(context=context, ui_manifest=ui_manifest)  
        self.store = store

        # Load Tileset Resources
        img = Image.open(os.path.join("display", "graphics", "resources", "player", "test-5.png"))
        img = img.convert("RGBA")
        self.TILESET.set_tile(64, np.array(img))
        img = Image.open(os.path.join("display", "graphics", "resources", "mob", "test-3.png"))
        img = img.convert("RGBA")
        self.TILESET.set_tile(65, np.array(img))

    def _start(self) -> None:
        """Initializes the display for rendering."""
        self.context = tcod.context.new(columns = self.WIDTH, rows = self.HEIGHT, tileset=self.TILESET, title=self.TITLE, vsync=True, sdl_window_flags=self.FLAGS)

        print("Display has started.")

    def _stop(self) -> None:
        """Cleans up resources used by the display."""
        if self.context:
            self.context.close()
        print("Display has stopped.")