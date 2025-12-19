# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from PIL import Image
import numpy as np

#from core_components.events.library import FOVUpdateEvent
from engine import Engine

TITLE = "JRL - Jay's Roguelike"
WIDTH, HEIGHT = 200, 96  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

def main() -> None:

    tileset = tcod.tileset.load_truetype_font("core_components\\graphics\\resources\\GoogleSansCode-SemiBold.ttf", 25, 25)
    img = Image.open("core_components\\graphics\\resources\\player\\test-5.png")
    img = img.convert("RGBA")
    tileset.set_tile(64, np.array(img))
    img = Image.open("core_components\\graphics\\resources\\mob\\test-3.png")
    img = img.convert("RGBA")
    tileset.set_tile(65, np.array(img))

    game = Engine()    
    game.start()
    
    game.ui.context = tcod.context.new(columns = WIDTH, rows = HEIGHT, tileset=tileset, title="Jay's Roguelike", vsync=True, sdl_window_flags=FLAGS)
    game.state.log.add("Welcome to Jay's Roguelike!")
    game.ui.render()

    while True:
        # Update Internal State
        game.map.update_state()

        # Update Console
        game.ui.render()

        # Update State Inputs
        for game_event in tcod.event.wait():
            if isinstance(game_event, tcod.event.KeyDown):
                game.state.events.put(game_event)

        if game.state.game_over.is_set():
            game.ui.context.close()   
            break

if __name__ == "__main__":
    main()