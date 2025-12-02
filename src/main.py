#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import tcod
from tcod.console import Console
from tcod.context import new as new_window
from tcod.tileset import load_tilesheet, CHARMAP_TCOD

from engine import Engine
from entities import Character
from dungeon_factory import random_dungeon

TITLE = "JRL - Jay's Roguelike"
WIDTH, HEIGHT = 720, 480  # Window pixel resolution (when not maximized.)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

def main() -> None:
    # Set up game window context
    tileset = load_tilesheet("dejavu10x10_gs_tc.png", 32, 8, CHARMAP_TCOD)

    # Create player and NPC entities
    player = Character(name="Player", x=40, y=22, char="@", color=(255, 255, 255))

    # Set up game map
    map_width = 100
    map_height = 100
    max_total_mobs = 100
    max_mobs_per_room = 5
    max_rooms = 15
    game_map = random_dungeon(map_width, map_height, player=player, max_rooms=max_rooms, max_total_mobs=max_total_mobs, max_mobs_per_room=max_mobs_per_room)

    # Initialize the game engine with dungeon and player
    engine = Engine(player=player, game_map=game_map)

    # Main game loop
    with new_window(columns=WIDTH, rows=HEIGHT, tileset=tileset, title=TITLE, vsync=True, sdl_window_flags=FLAGS) as game_window:
        root_game_console = game_window.new_console(order="F")

        while True:
            if game_window.sdl_window: #Resize window
                window_height, window_width = game_window.sdl_window.size
                if window_height>=map_height or window_width>=map_width:
                    root_game_console = game_window.new_console(map_width, map_height, order="F")

            # Render game console
            engine.render(console=root_game_console, context=game_window, view_mobs=True)

            # Parse, execute, and manage event driven state changes for entities
            engine.handle_events(events=tcod.event.wait())

if __name__ == "__main__":
    main()