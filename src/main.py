# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-

from __future__ import annotations
# import tcod
# from tcod.console import Console
# from tcod.context import new as new_window
# from tcod.tileset import load_tilesheet, CHARMAP_TCOD

# from engine import Engine
# from dungeon_factory import random_dungeon
# from entities import Charactor
# from components.stats import CombatStats, PhysicalStats

TITLE = "JRL - Jay's Roguelike"
WIDTH, HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
# FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

def main() -> None:
    pass
#     # Set up game window context
#     tileset = load_tilesheet("dejavu10x10_gs_tc.png", 32, 8, CHARMAP_TCOD)

#     # Create player and NPC entities
#     player = Charactor(name="Player", char="@", color=(255, 255, 255),
#                        physical=PhysicalStats(max_hp=30, constitution=12),
#                        combat=CombatStats(defense=2, attack_power=5))
#     engine = Engine(player=player)

#     # Set up game map
#     map_width = 100
#     map_height = 100
#     max_total_mobs = 5
#     max_mobs_per_room = 1
#     max_rooms = 3
#     engine.game_map = random_dungeon(engine, map_width, map_height, player=player, max_rooms=max_rooms, max_total_mobs=max_total_mobs, max_mobs_per_room=max_mobs_per_room)


#     # Main game loop
#     with new_window(columns=WIDTH, rows=HEIGHT, tileset=tileset, title=TITLE, vsync=True, sdl_window_flags=FLAGS) as game_window:
#         root_game_console = game_window.new_console(order="F")

#         while True:
#             if game_window.sdl_window: #Resize window
#                 window_height, window_width = game_window.sdl_window.size
#                 if window_height>=map_height or window_width>=map_width:
#                     root_game_console = game_window.new_console(map_width, map_height, order="F")

#             # Render game console
#             engine.render(console=root_game_console, context=game_window, view_mobs=False)

#             # Parse, execute, and manage event driven state changes for entities
#             engine.event_handler.handle_events()

# if __name__ == "__main__":
#     main()