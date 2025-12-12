#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from typing import Tuple
import numpy as np

from core_components.maps.base import GraphicTileMap, ascii_graphic
from core_components.tiles.base import TileTuple


DEFAULT_MANIFEST = {    'dimensions': {'grid_size': TileTuple(([80], [50]))},
                        'state': {  'bits': (  'blocks_movement', 'blocks_vision', 'visible', 'seen'),
                                    'names': (  '0000', '0001', '0010', '0011',
                                                '0100', '0101', '0110', '0111',
                                                '1000', '1001', '1010', '1011',
                                                '1100', '1101', '1110', '1111'),
                                    'tuples': ( (0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 0, 1, 1),
                                                (0, 1, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 1, 1, 1),
                                                (1, 0, 0, 0), (1, 0, 0, 1), (1, 0, 1, 0), (1, 0, 1, 1),
                                                (1, 1, 0, 0), (1, 1, 0, 1), (1, 1, 1, 0), (1, 1, 1, 1) ),
                                    'dtype_labels': {   'fixed_bits': { 'shroud': {'blocks_movement': None, 'blocks_vision': None, 'visible': 0, 'seen': 0}, # Use for mapping to state
                                                                        'visible': {'blocks_movement': None, 'blocks_vision': None, 'visible': 1, 'seen': 1},
                                                                        'first_look': {'blocks_movement': None, 'blocks_vision': None, 'visible': 1, 'seen': 0},
                                                                        'explored': {'blocks_movement': None, 'blocks_vision': None, 'visible': 0, 'seen': 1}},
                                                        'label_state_map': None} # Use fixed_bits to create at runtime
                                    },
                                            
                        'colors': { "fill_bluebell": (ord(" "), (255, 255, 255), (50, 50, 150)),
                                    "fill_light_yellow": (ord(" "), (255, 255, 255), (200, 180, 50)),
                                    "fill_black": (ord(" "), (255, 255, 255), (0, 0, 0)),
                                    "fill_dark_blue": (ord(" "), (255, 255, 255), (0, 0, 100)),
                                    "fill_golden_yellow": (ord(" "), (255, 255, 255), (130, 110, 50))       
                                        },
                        "dtypes": {
                                    "tile_state": None,
                                    "tile_color": None,
                                    "tile_graphic": None,
                                    "tile_grid": None
                                    },

                        'graphics': {"default": {   "fixed_state_bits": {'blocks_movement': 0, 'blocks_vision': 0, 'visible': 0, 'seen': 0}, # Use for state updating
                                                    "state_label": {'0000': ('shroud', 'fill_black')}},
                                    "floor": {  "fixed_state_bits": {'blocks_movement': 1, 'blocks_vision': 0, 'visible': None, 'seen': None},
                                                "state_dtype_labels": {'1000': ('shroud', 'fill_black'),
                                                                '1001': ('explored', 'fill_bluebell'),
                                                                '1010': ('first_look', 'fill_light_yellow'),
                                                                '1011': ('visible', 'fill_light_yellow')}},
                                    "wall": {   "fixed_state_bits": {'blocks_movement': 0, 'blocks_vision': 1, 'visible': None, 'seen': None},
                                                "state_dtype_labels": {'0100': ('shroud', 'fill_black'),
                                                                '0101': ('explored', 'fill_dark_blue'),
                                                                '0110': ('first_look', 'fill_golden_yellow'),
                                                                '0111': ('visible', 'fill_golden_yellow')}},
                                    }
                    }


class DefaultTileMap(GraphicTileMap):
    pass
 # @property
    # def state_definitions_table(self) -> np.ndarray:
    #     """Return a table of all defined render states."""
    #     state_vectors = [self.tiles[bit] for bit in self.state['bits']]
    #     return np.dstack(state_vectors)
    
    # @property
    # def state_definitions_tensor(self) -> np.ndarray:
    #     """Return an array of the defined render states reshaped to align with the state_tensor."""
    #     grid_dim1, grid_dim2 = self.grid.size[0][0], self.grid.size[1][0]
    #     dim1 = np.concatenate([self.state_definitions_table] * grid_dim1).reshape(grid_dim1, *self.state_definitions_table.shape)
       
    #     return np.concatenate([dim1] * grid_dim2).reshape(grid_dim2, grid_dim1, *self.state_definitions_table.shape)
    
    # @property
    # def state_tensor(self) -> np.ndarray:
    #     """Return a tensor of all current render states for all tiles on the map reshaped to align the state_definitions_tensor."""
    #     pos1 = self.tiles['visible']
    #     pos2 = self.tiles['explored']

    #     current = np.dstack([pos1, pos2])
    #     n_states = len(self.state['bits'])

    #     np.concatenate([current]*n_states).reshape(self.tiles.size, n_states, 4)
    #     return np.stack([pos1, pos2], axis=3)
    
    # @property
    # def state_labels_array(self) -> np.ndarray:
    #     """Return an array of state labels for all tiles on the map based on their current states."""

    #     return np.argwhere(np.all(self.state_definitions_tensor == self.state_definitions_tensor, axis=(3,)))
    
    # def update_graphics(self) -> None:
    #     """Update the graphic render of all tiles on the map based on their current states."""
    #     state_array = self.get_rendered_state_array()
    #     for index, graphic in np.ndenumerate(self.tiles['type']):
    #         state_label = state_array[index]
    #         tile_type_graphic = self.tiles['graphic_type'][index]
    #         graphic_name = tile_type_graphic['name']
    #         graphic_def = self.graphics[graphic_name]
    #         self.tiles['rendered'][index] = graphic_def[state_label]

    # def set_area(self, 
    #              area: TileArea | np.ndarray, 
    #              tile_type: str = "floor",
    #              traversable: bool = True,
    #              transparent: bool = True) -> None:
        
    #     """Set tiles on the map at the specified area."""
        
    #     if isinstance(area, np.ndarray):
    #         area_slice = [area[:,0], area[:,1]]

    #     elif isinstance(area, TileArea):
    #         area_slice = area.to_slices()
            
    #     self.tiles['type'][area_slice[0], area_slice[1]] = self._resources['tiles'][tile_type]
    #     self.tiles['graphic'][area_slice[0], area_slice[1]] = self._resources['tiles'][tile_type]['g_shroud']
    #     self.tiles['traversable'][area_slice[0], area_slice[1]] = traversable
    #     self.tiles['transparent'][area_slice[0], area_slice[1]] = transparent

    #     #TODO Update unit tests for add_area method