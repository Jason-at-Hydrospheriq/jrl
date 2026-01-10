#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from tcod.context import Context
import tcod
from PIL import Image
import os
import numpy as np
import traceback
import time

from display.widgets import MainMapDisplay, HealthBarWidget, MessageLogWidget
from manifests import DEFAULT_TILEMAP_MANIFEST
from baseclasses import BaseUI
from game_types import UIManifestDict
import threading

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
    threads = []
    stop_signal: threading.Event
    
    TITLE = "JRL - Jay's Roguelike"
    WIDTH, HEIGHT = 200, 96  # Window pixel resolution (when not maximized.)
    FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED
    src_path = os.path.dirname(os.path.abspath(__file__))
    TILESET = tcod.tileset.load_truetype_font("C:\\Users\\jason\\workspaces\\repos\\jrl\\src\\display\\graphics\\resources\\GoogleSansCode-SemiBold.ttf", 25, 25)

    def __init__(self, context: Context | None = None, ui_manifest: UIManifestDict | None = DEFAULT_UI_MANIFEST, store: GameStore | None = None) -> None:
        super().__init__(context=context, ui_manifest=ui_manifest)  
        self.store = store
        self.threads = []
        self.stop_signal = threading.Event()

        # Load Tileset Resources
        img = Image.open(os.path.join("display", "graphics", "resources", "player", "test-5.png"))
        img = img.convert("RGBA")
        self.TILESET.set_tile(64, np.array(img))
        img = Image.open(os.path.join("display", "graphics", "resources", "mob", "test-3.png"))
        img = img.convert("RGBA")
        self.TILESET.set_tile(65, np.array(img))
        self.threads.append(threading.Thread(target=self.display_loop, daemon=True))
        
    def _start(self) -> None:
        """Initializes the display for rendering."""
        self.context = tcod.context.new(columns = self.WIDTH, rows = self.HEIGHT, tileset=self.TILESET, title=self.TITLE, vsync=True, sdl_window_flags=self.FLAGS)
        
        for thread in self.threads:
            thread.start()

        print("Display has started.")

    def _stop(self) -> None:
        """Cleans up resources used by the display."""
        if self.context:
            self.context.close()
        print("Display has stopped.")
    
    def display_loop(self) -> None:
        """Main display loop that runs in a separate thread."""
        last_beat = time.time()
        ctr = 0

        try:
            while not self.stop_signal.is_set():
                ctr += 1
    
                if self.state != 'started':  # type: ignore
                    time.sleep(0.1)
                    continue

                if ctr % 50 == 0:
                    current_time = time.time()
                    if ctr % 100 == 0:
                        print(f"Display Loop <8: {(current_time - last_beat)*1000:.2f}ms")
                        ctr = 0
                    else:
                        print(f"Display Loop 8>: {(current_time - last_beat)*1000:.2f}ms")
                    last_beat = current_time
                self.render()

        except Exception as e:
            print(f"Display loop encountered an error: {e}")
            traceback.print_exc()
