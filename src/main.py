# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from tcod.console import Console
from tcod.context import new as new_window
from tcod.tileset import load_tilesheet, CHARMAP_TCOD
from PIL import Image
import numpy as np

from engine import Engine
# from dungeon_factory import random_dungeon
from core_components.entities.library import PlayerCharactor
# from components.stats import CombatStats, PhysicalStats
from core_components.tiles.library import TileCoordinate, TileTuple

TITLE = "JRL - Jay's Roguelike"
WIDTH, HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

def main() -> None:
    screen_width = 100
    screen_height = 100

    # tileset = tcod.tileset.load_tilesheet(
    #     "oryx_roguelike_160x40.png", columns=8 , rows=2, charmap=tcod.tileset.CHARMAP_CP437
    # )
    

    
    # tileset = tcod.tileset.load_tilesheet(
    #     "graphics\\resources\\dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    # )

    tileset = tcod.tileset.load_truetype_font("graphics\\resources\\Iceland-Regular.ttf", 25, 25)
    tileset = tcod.tileset.Tileset(20,20)
    img = Image.open("graphics\\resources\\player\\test-5.png")
    img = img.convert("RGBA")
    tileset.set_tile(64, np.array(img))
    img = Image.open("graphics\\resources\\mob\\test-3.png")
    img = img.convert("RGBA")
    tileset.set_tile(65, np.array(img))

    game = Engine()    
    game.start()

    expected_bits = np.full([50, 50], fill_value=True)
    # game.state.map.active.set_state_bits('visible', expected_bits)
    game.map.set_state_bits('seen', expected_bits)
    
    game.ui.context = tcod.context.new(columns = screen_width, rows = screen_height, tileset=tileset, title="Jay's Roguelike", vsync=True, sdl_window_flags=FLAGS)
    
    while True:
        # Update Console
        game.map.update_state()

        game.ui.render()

        # Update Game State
        for game_event in tcod.event.wait():
            if isinstance(game_event, tcod.event.KeyDown):
                game.state.events.put(game_event)

        if game.state.game_over.is_set():
            game.ui.context.close()   
            break

if __name__ == "__main__":
    main()