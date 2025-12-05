from __future__ import annotations
from typing import TYPE_CHECKING, Set, Iterable, Any
from tcod.context import Context
from tcod.console import Console

from entities import Charactor
from game_map import GameMap


class Engine:
    """The Game Engine has a Player, a collection of Game Entities, a Game Map, an Event Handler, a Renderer, and a UI. The Engine manages the state to state transitions
    of all objects in the game."""

    player: Charactor
    game_map: GameMap