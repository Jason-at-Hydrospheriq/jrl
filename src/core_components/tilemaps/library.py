#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Tuple
from core_components.maps.base import BaseTileMap, ascii_graphic


class GenericTileMap(BaseTileMap):
    def __init__(self, size: Tuple[int, int] = (1, 1)) -> None:
        self._resources = {
            'graphics': {"fill_bluebell": (ord(" "), (255, 255, 255), (50, 50, 150)),
                          "fill_light_yellow": (ord(" "), (255, 255, 255), (200, 180, 50)),
                          "fill_black": (ord(" "), (255, 255, 255), (0, 0, 0)),
                          "fill_dark_blue": (ord(" "), (255, 255, 255), (0, 0, 100)),
                          "fill_golden_yellow": (ord(" "), (255, 255, 255), (130, 110, 50))
                          },
            'tile_type_graphic_fields': ['g_shroud', 'g_explored', 'g_visible'],
            "dtypes": {
                "tile_graphic": ascii_graphic,
                "tile_type": None,
                "tile_location": None},
            'tiles': {
                'default': {
                        'g_shroud': "fill_black",
                        'g_explored': "fill_black",
                        'g_visible': "fill_black"
                           },

                'floor': {
                    'g_shroud': "fill_black",
                    'g_explored': "fill_bluebell",
                    'g_visible': "fill_light_yellow"
                        },
                'wall': {
                   'g_shroud': "fill_black",
                   'g_explored': 'fill_dark_blue',
                   'g_visible': "fill_golden_yellow"
                        }
                    }
                }
        self._width, self._height = size
        self.initialize_resources()
        self.initialize_map()