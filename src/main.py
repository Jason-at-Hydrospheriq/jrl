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
    screen_width = 60
    screen_height = 60

    # tileset = tcod.tileset.load_tilesheet(
    #     "oryx_roguelike_160x40.png", columns=8 , rows=2, charmap=tcod.tileset.CHARMAP_CP437
    # )
    
    tileset = tcod.tileset.Tileset(20,20)
    img = Image.open("graphics\\resources\\player.png")
    img = img.convert("RGBA")
    tileset.set_tile(64, np.array(img))
    img = Image.open("graphics\\resources\\monster_20x20.png")
    img = img.convert("RGBA")
    tileset.set_tile(65, np.array(img))

    game = Engine()    
    game.start()

    expected_bits = np.full([screen_width, screen_height], fill_value=True)
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

# def main() -> None:
#     pass
#     # Set up game window context
#     tileset = load_tilesheet("dejavu10x10_gs_tc.png", 32, 8, CHARMAP_TCOD)

# #     # Create player and NPC entities
# #     player = Charactor(name="Player", symbol="@", color=(255, 255, 255),
# #                        physical=PhysicalStats(max_hp=30, constitution=12),
# #                        combat=CombatStats(defense=2, attack_power=5))
#     engine = Engine()
#     ui = engine.state.ui

# #     # Set up game map
#     # map_width = 100
#     # map_height = 100
# #     max_total_mobs = 5
# #     max_mobs_per_room = 1
# #     max_rooms = 3
# #     engine.game_map = random_dungeon(engine, map_width, map_height, player=player, max_rooms=max_rooms, max_total_mobs=max_total_mobs, max_mobs_per_room=max_mobs_per_room)


# #     # Main game loop
#     with new_window(columns=WIDTH, rows=HEIGHT, tileset=tileset, title=TITLE, vsync=True, sdl_window_flags=FLAGS) as game_window:
#         ui.console = game_window.new_console(order="F")

#         while True:
#             if game_window.sdl_window: #Resize window
#                 window_height, window_width = game_window.sdl_window.size
#                 ui.console = game_window.new_console(window_width, window_height, order="F")

#             # Render game console
#             ui.render()

#             # Parse, execute, and manage event driven state changes for entities
#             # engine.event_handler.handle_events()

# if __name__ == "__main__":
#     main()