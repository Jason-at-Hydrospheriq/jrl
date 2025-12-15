# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from tcod.console import Console
from tcod.context import new as new_window
from tcod.tileset import load_tilesheet, CHARMAP_TCOD

from engine import Engine
# from dungeon_factory import random_dungeon
# from entities import Charactor
# from components.stats import CombatStats, PhysicalStats

TITLE = "JRL - Jay's Roguelike"
WIDTH, HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

def main() -> None:
    screen_width = 80
    screen_height = 50

    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )
    
    game = Engine()
    game.start()
    context = tcod.context.new_terminal( screen_width, screen_height, tileset=tileset,
                                         title="Yet Another Roguelike Tutorial", vsync=True)
    
    while True:
        # Update Console
        console = context.new_console(screen_width, screen_height, order="F")
        console.print(x=1, y=1, string="@")
        context.present(console)

        # Update Game State
        for game_event in tcod.event.wait():
            if isinstance(game_event, tcod.event.KeyDown):
                game.state.events.put(game_event)

        if game.state.game_over.is_set():
            context.close()   
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