#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Tuple
import numpy as np

from core_components.maps.base import GraphicTileMap, ascii_graphic, GraphicsManifestDict
from core_components.tiles.base import TileTuple

DEFAULT_MANIFEST = GraphicsManifestDict({'dimensions': {'grid_size': TileTuple(([80], [50]))},
                                         'statespace': { 'bits': ('blocks_movement', 'blocks_vision', 'visible', 'seen'),
                                                    'vector_tuples': ( (0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 0, 1, 1),
                                                                (0, 1, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 1, 1, 1),
                                                                (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0), (1, 0, 1, 1),
                                                                (1, 1, 0, 0), (1, 1, 0, 1), (1, 1, 1, 0), (1, 1, 1, 1) ),
                                                    'dtype_labels': {'names': ('shroud', 'visible', 'explored', 'first_look'),
                                                                    'fixed_bits': { 'shroud':       (None, None, 0, 0),
                                                                                    'visible':      (None, None, 1, 1),
                                                                                    'first_look':   (None, None, 1, 0),
                                                                                    'explored':     (None, None, 0, 1)
                                                                                    }
                                                                    },
                                                    'label_map': (),
                                                                },
                                         'colors': {"fill_bluebell": (ord(" "), (255, 255, 255), (50, 50, 150)),
                                                    "fill_light_yellow": (ord(" "), (255, 255, 255), (200, 180, 50)),
                                                    "fill_black": (ord(" "), (255, 255, 255), (0, 0, 0)),
                                                    "fill_dark_blue": (ord(" "), (255, 255, 255), (0, 0, 100)),
                                                    "fill_golden_yellow": (ord(" "), (255, 255, 255), (130, 110, 50))       
                                                        }, 
                                         'dtypes': {
                                                        "tile_state_vector": None,
                                                        "tile_color": ascii_graphic,
                                                        "tile_graphic": None,
                                                        "tile_grid": None
                                         }, 
                                         'graphics': {  "default": {   "fixed_state_bits": {'blocks_movement': 0, 'blocks_vision': 0, 'visible': 0, 'seen': 0}, # Use for state updating
                                                                        "state_definitions": {'shroud': 'fill_black'}},
                                                        "floor": {  "fixed_state_bits": {'blocks_movement': 1, 'blocks_vision': 0, 'visible': None, 'seen': None},
                                                                    "state_definitions": {'shroud': 'fill_black',
                                                                                    'explored': 'fill_bluebell',
                                                                                    'first_look': 'fill_light_yellow',
                                                                                    'visible': 'fill_light_yellow'}},
                                                        "wall": {   "fixed_state_bits": {'blocks_movement': 0, 'blocks_vision': 1, 'visible': None, 'seen': None},
                                                                    "state_definitions": {'shroud': 'fill_black',
                                                                                    'explored': 'fill_dark_blue',
                                                                                    'first_look': 'fill_golden_yellow',
                                                                                    'visible': 'fill_golden_yellow'}},
                                                        }
                                         })


class DefaultTileMap(GraphicTileMap):

    def __init__(self, graphics_manifest=DEFAULT_MANIFEST) -> None:
        super().__init__(graphics_manifest=graphics_manifest)
    
    @property
    def traversable(self) -> np.ndarray:
        return self.get_state_bits('blocks_movement') == False
    
    @property
    def transparent(self) -> np.ndarray:
        return self.get_state_bits('blocks_vision') == False
    
    @property
    def seen(self) -> np.ndarray:
        return self.get_state_bits('seen')

    @property
    def visible(self) -> np.ndarray:
        return self.get_state_bits('visible')
