#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from src.components.display.base import BaseUIComponent

if TYPE_CHECKING:
    from engine import Engine
    from components.game_map import GameMap

class MainMapDisplay(BaseUIComponent):
    """ The Map UI component is responsible for updating the MapUI state on the Console. 
    The Engine provides the state information for the update. No State/Action logic should be here.
    This is the Execution step of State - Action - Execution pipeline for the Console."""

    def print_entities(self, entities, key, tile_map: GameMap) -> None:
        for entity in sorted(entities, key=key, reverse=False):
            if tile_map.is_visible(entity.location):
                self.console.print(entity.location.x, entity.location.y, entity.char, fg=entity.color)

    def render(self, engine: Engine) -> None:
        x_slice = slice(self.upper_Left_x, self.lower_Right_x)
        y_slice = slice(self.upper_Left_y, self.lower_Right_y)
        tile_map = engine.map
        
        # Render Tiles
        self.console.rgb[x_slice, y_slice] = tile_map.tiles["color"][:self.width, :self.height]
        
        # Render Actors in order of their is_alive status
        self.print_entities(engine.roster.all_actors, key=lambda e: hasattr(e, 'is_alive'), tile_map=tile_map)

        # Render Non-Actors in order of their blocks_movement status
        self.print_entities(engine.roster.all_non_actors, key=lambda e: hasattr(e, 'blocks_movement'), tile_map=tile_map)