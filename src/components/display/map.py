#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import TYPE_CHECKING
from components.display.base import BaseUIComponent
from tile_types import SHROUD
from tcod.console import Console
import numpy as np

if TYPE_CHECKING:
    from engine import Engine


class MapUI(BaseUIComponent):
    """ The Map UI component is responsible for updating the MapUI state on the Console. 
    The Engine provides the state information for the update. No State/Action logic should be here.
    This is the Execution step of State - Action - Execution pipeline for the Console."""

    x: int
    y: int

    def render(self, console: Console, engine: Engine) -> None:
        tile_map = engine.game_map
        player = engine.player
        entities = engine.entities
        
        # Render Tiles
        map_display_width = min(tile_map.width, console.width - self.x)
        map_display_height = min(tile_map.height, console.height - self.y)

        console.rgb[self.x: self.x + map_display_width, self.y:self.y + map_display_height] = tile_map.tiles["color"][:map_display_width, :map_display_height]
        
        # Render Entities in order of their is_alive status
        for entity in sorted(entities | {player}, key=lambda e: e.is_alive, reverse=False):
            if tile_map.is_visible(entity.location):
                console.print(entity.location.x, entity.location.y, entity.char, fg=entity.color)