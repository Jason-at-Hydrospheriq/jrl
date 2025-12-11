#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
import numpy as np
import random
from typing import Any, NewType, NotRequired, Protocol, Dict, Tuple, TypedDict
from copy import deepcopy
import numpy as np

from core_components.tiles.base import BaseTileGrid, TileTuple

# Tile graphic dtype definition
ascii_graphic = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ], metadata={"__name__": "ascii_graphic"}
)

# Tile Grid dtype generator
def grid_tile_dtype(graphic_dtype: np.dtype, rendered_dtype: np.dtype = ascii_graphic) -> np.dtype:
    """Generates the tile location dtype based on the provided tile_type dtype"""
    return np.dtype(
                    [   ("graphic_type", graphic_dtype), # The type of the tile, e.g., 'floor', 'wall', etc. with associated graphic states.
                        ("traversable", np.bool),  # True if this tile can be occupied by or passed through by an entity.
                        ("transparent", np.bool),  # True if this tile doesn't block FOV.
                        ('visible', np.bool),  # True if this tile is currently visible.
                        ('explored', np.bool),  # True if this tile has been explored.
                        ('graphic_state', ascii_graphic) # The current graphic state representation of the tile.
                    ], metadata={"__name__": "grid_tile_dtype"})

# A typed dictionary for map graphics
class MapGraphics(TypedDict):
    dimensions: Any
    colors: Dict[str, Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]]
    dtypes: Dict[str, np.dtype | None ]
    graphics: Dict[str, Dict[str, str]]
    interaction_states: Dict[str, np.ndarray]
    render_states: Dict[str, np.ndarray]

StateTuple = NewType('StateTuple', Tuple[bool | None, bool | None, bool | None, bool | None])

DEFAULT_MANIFEST = MapGraphics(
    {   'dimensions': {'grid_size': TileTuple(([80], [50]))},
        'colors': {
                "fill_bluebell": (ord(" "), (255, 255, 255), (50, 50, 150)),
                "fill_light_yellow": (ord(" "), (255, 255, 255), (200, 180, 50)),
                "fill_black": (ord(" "), (255, 255, 255), (0, 0, 0)),
                "fill_dark_blue": (ord(" "), (255, 255, 255), (0, 0, 100)),
                "fill_golden_yellow": (ord(" "), (255, 255, 255), (130, 110, 50))
                      },
        'interaction_states': {
                            'opaque_block': np.array((False, False)),
                            'transparent_block': np.array((False, True)),
                            'opaque_pass': np.array((True, False)),
                            'transparent_pass': np.array((True, True))
                            },
        'render_states': { 
                    'shrouded': np.array((False, False)), 
                    'explored': np.array((False, True)),
                    'first_look': np.array((True, False)),
                    'visible': np.array((True, True))
                    },
        "dtypes": {
                "tile_graphic": ascii_graphic,
                "tile_type": None,
                "tile_location": None
                },
        'graphics': {
                'default': {
                        'shrouded': "fill_black",
                        'explored': "fill_black",
                        'first_look': "fill_black",
                        'visible': "fill_black"
                           },
                'floor': {
                    'shrouded': "fill_black",
                    'explored': "fill_bluebell",
                    'first_look': "fill_light_yellow",
                    'visible': "fill_light_yellow"
                        },
                'wall': {
                    'shrouded': "fill_black",
                    'explored': 'fill_dark_blue',
                    'first_look': "fill_golden_yellow",
                    'visible': "fill_golden_yellow"
                        }
                    }
                })

class GraphicTileMap:
    """The GraphicTileMap defines the interface for graphic tile maps. A GraphicTileMap
    holds the graphics, dtypes, and tile states for the map. It has a TileGrid that
    manages the tile data and provides methods for initializing and manipulating the TileCoordinateSystem. 
    It also has a graphics dictionary that holds the graphic definitions for the tiles. The graphics
    dictionary can be stored as JSON and is loaded at runtime to set the GraphicTileMap attributes.
    """
    _graphics_manifest: MapGraphics
    _graphics_resources: MapGraphics
    _grid: BaseTileGrid
    dimensions: Dict[str, TileTuple]
    colors: Dict[str, np.ndarray]
    dtypes: Dict[str, np.dtype | None ]
    graphics: Dict[str, np.ndarray | None]
    tiles: np.ndarray
    states: Dict = {}

    def __init__(self, graphics: MapGraphics = DEFAULT_MANIFEST) -> None:

        if graphics:
            self._graphics_manifest = deepcopy(graphics)
            self._graphics_resources = MapGraphics(
                                        {"dimensions": {},
                                        "dtypes": {}, 
                                        "colors": {},
                                        "graphics": {},
                                        "interaction_states": {},
                                        "render_states": {}
                                        })
            
            # Link attributes to graphics resources
            for key in self._graphics_manifest.keys():
                if not key.endswith("_states"):
                    setattr(self, key, self._graphics_resources[key])
                elif key.endswith("_states"):
                    self.states[key] = deepcopy(self._graphics_manifest[key])

            self.dimensions = deepcopy(self._graphics_manifest['dimensions'])
            
            self._initialize_dtypes()
            self._initialize_colors()
            self._initialize_graphics()

            if "grid_tile_dtype" in self.dtypes:
                dtype = self.dtypes["grid_tile_dtype"]
                if dtype is not None:
                    self._grid = BaseTileGrid(dtype)
            
                    if "grid_size" in self.dimensions:
                        self.grid.size = self.dimensions["grid_size"]
                        self.grid._initialize_grid()
                        self.tiles = self.grid.tiles
                        self.tiles['graphic_type'][:] = self.graphics['default']
                        self.states['render_states']
                        self.states['matrix'] =  
                        self.reset_exploration()
                        self.reset_visibility()

    @property
    def grid(self) -> BaseTileGrid:
        return self._grid

    def _initialize_dtypes(self) -> None:

        """Generates the tile and tile location dtypes based on the graphic definitions"""

        state_color_dtypes = [(state, ascii_graphic) for state in self.states['render_states'].keys()]
        graphic_dtype =  np.dtype([("name", "U16")] + state_color_dtypes, metadata={"__name__": "tile_graphics"})
        self.dtypes["tile_graphics"] = graphic_dtype
        self.dtypes["grid_tile_dtype"] = grid_tile_dtype(graphic_dtype)
    
    def _initialize_colors(self) -> None:
        """Generates the tile graphic definitions for the map"""
        color_dtype = ascii_graphic
        for color_name, color_def in self._graphics_manifest['colors'].items():
            self.colors[color_name] = np.array(color_def, dtype=color_dtype)
    
    def _initialize_graphics(self) -> None:
        graphic_dtype = self.dtypes['tile_graphics']
        for graphic_name, state_color_definition in self._graphics_manifest['graphics'].items():
            name_value = (graphic_name,)
            graphics_value = []

            for state in self.states['render_states'].keys():
                graphics_value.append(
                    self.colors[state_color_definition[state]]
                )
            
            
            values =  name_value + tuple(graphics_value)
            
            graphic = np.array(values, dtype=graphic_dtype)
            self.graphics[graphic_name] = graphic

    # def get_render_state(self, state: StateTuple) -> str:
    #     """Return the render state label based on the state tuple."""
        

    # def get_graphic_at(self, location: TileCoordinates) -> np.ndarray:
    #     """Return the tile color at the given location."""
    #     if not location.is_inbounds:
    #         return np.empty((3,))
        
    #     return self.tiles["colors"][location.x, location.y]

    @property
    def state_definitions_table(self) -> np.ndarray:
        """Return a table of all defined render states."""
        state_vectors = []
        for val in self.states['render_states'].values():
            state_vectors.append(val)
        return np.dstack(state_vectors)
    
    @property
    def state_definitions_tensor(self) -> np.ndarray:
        """Return an array of the defined render states reshaped to align with the state_tensor."""
        grid_dim1, grid_dim2 = self.grid.size[0][0], self.grid.size[1][0]
        dim1 = np.concatenate([self.state_definitions_table] * grid_dim1).reshape(grid_dim1, *self.state_definitions_table.shape)
       
        return np.concatenate([dim1] * grid_dim2).reshape(grid_dim2, grid_dim1, *self.state_definitions_table.shape)
    
    @property
    def state_tensor(self) -> np.ndarray:
        """Return a tensor of all current render states for all tiles on the map reshaped to align the state_definitions_tensor."""
        pos1 = self.tiles['visible']
        pos2 = self.tiles['explored']

        current = np.dstack([pos1, pos2])
        n_states = len(list(self.states['render_states'].keys()))

        np.concatenate([current]*n_states).reshape(self.tiles.size, n_states, 4)
        return np.stack([pos1, pos2], axis=3)
    
    @property
    def state_labels_array(self) -> np.ndarray:
        """Return an array of state labels for all tiles on the map based on their current states."""

        return np.argwhere(np.all(self.state_definitions_tensor == self.state_definitions_tensor, axis=(3,)))
    
    def update_graphics(self) -> None:
        """Update the graphic render of all tiles on the map based on their current states."""
        state_array = self.get_rendered_state_array()
        for index, graphic in np.ndenumerate(self.tiles['type']):
            state_label = state_array[index]
            tile_type_graphic = self.tiles['graphic_type'][index]
            graphic_name = tile_type_graphic['name']
            graphic_def = self.graphics[graphic_name]
            self.tiles['rendered'][index] = graphic_def[state_label]

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

    def update_traversable(self, area_mask: np.ndarray, state: StateTuple) -> None:
        """Set the traversable state of the tiles based on the area mask."""
        if state[0] is not None:
            self.tiles["traversable"][area_mask] = state[0]

    def update_transparency(self, area_mask: np.ndarray, state: StateTuple) -> None:
        """Set the transparency of the tiles based on the area mask."""
        if state[1] is not None:
            self.tiles["transparent"][area_mask] = state[1]

    def update_visible(self, fov: np.ndarray) -> None:
        """Set the visible state of the tiles based on the field of view."""
        self.tiles["visible"][:] = fov
    
    def update_explored(self, fov: np.ndarray) -> None:
        """Update the explored state of the tiles based on the field of view."""
        self.tiles["explored"][:] |= fov
    
    def update_rendered_state(self) -> None:
        """Set the graphic state of the tiles."""
        pass

    def reset_traversable(self) -> None:
        """Reset the traversable state of all tiles on the map to not traversable."""
        self.tiles["traversable"][:, :] = False

    def reset_transparency(self) -> None:
        """Reset the transparency of all tiles on the map to not transparent."""
        self.tiles["transparent"][:, :] = False

    def reset_visibility(self) -> None:
        """Reset the visibility of all tiles on the map to not visible."""
        self.tiles["visible"][:, :] = False

    def reset_exploration(self) -> None:

        """Reset the exploration state of all tiles on the map to not explored."""
        self.tiles["explored"][:, :] = False 


        