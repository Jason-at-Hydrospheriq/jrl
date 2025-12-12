#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
import numpy as np
import itertools
from typing import Any, List, Protocol, Dict, Tuple, TypedDict
from copy import deepcopy
import numpy as np

from core_components.tiles.base import BaseTileGrid, TileTuple, TileArea, TileCoordinate

# Tile graphic dtype definition
ascii_graphic = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ], metadata={"__name__": "ascii_graphic"}
)

# A typed dictionary for map graphics
class GraphicsManifestDict(TypedDict):
    dimensions: Dict[str,TileTuple]
    state: Dict[str, Tuple[str, ...] | Dict[str, Dict[str, int | None]]]
    colors: Dict[str, Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]]
    dtypes: Dict[str, np.dtype | None ]
    graphics: Dict[str, Any]

# Helper functions to create GraphicManifestDict
def create_states(n: int) -> List[str]:
    """
    Generates a list of all possible binary strings for a given bit length n.

    Args:
        n: The desired number of bits (length of the binary strings).

    Returns:
        A list of strings, where each string is a unique n-bit binary representation.
    """
    if n < 0:
        raise ValueError("Bit length must be a non-negative integer.")
        
    # itertools.product('01', repeat=n) generates all combinations of '0' and '1' 
    # of length n as tuples, which are then joined into strings.
    return [''.join(i) for i in itertools.product('01', repeat=n)]

def graphics_state_assignment(manifest):
    statebits = manifest['state_definition']['bits']
    n = len(statebits)
    manifest['state_definition']['names'] = create_states(n)

    graphics = manifest['graphics']
    states = manifest['state_definition']['names']
    labels = manifest['state_definition']['dtype_labels']

    # Assign allowable states to graphics based on their fixed state bits
    for graphic in graphics.values():

        # Screen through each state and assign it to a graphic if it matches the fixed state bits
        for state in states:
            add_state = False

            for idx, bit in enumerate(state):
                fixed_bit = graphic['fixed_state_bits'][statebits[idx]]
                if fixed_bit is None:
                    pass

                elif fixed_bit == int(bit):
                    add_state = True

                else:
                    add_state = False
                    break

            if add_state:
                # Screen through each label and assign a color state label to the state
                for label_name, label_bits in labels.items():
                    use_label = False
                    for idx, bit in enumerate(state):
                        if label_bits[statebits[idx]] is None:
                            use_label = True
                        
                        elif label_bits[statebits[idx]] == int(bit):
                            use_label = True

                        else:
                             # Placeholder for actual color name
                             use_label = False
                             break
                        
                    if use_label:
                        graphic['state_labels'][state] = (label_name, "color name")

    return manifest


class GraphicTileMap(Protocol):
    """The GraphicTileMap defines the interface for graphic tile maps. A GraphicTileMap
    holds the graphics, dtypes, and tile states for the map. It has a TileGrid that
    manages the tile data and provides methods for initializing and manipulating the TileCoordinateSystem. 
    It also has a graphics dictionary that holds the graphic definitions for the tiles. The graphics
    dictionary can be stored as JSON and is loaded at runtime to set the GraphicTileMap attributes. The 
    GraphicTileMap methods allow for reading, updating, and resetting the tile states and graphics on the map.

    Implementations of this protocol are responsible for managing the state and graphics of the tiles on the map
    bases on the specific definitions in the graphics manifest. Each new map should have its own associated graphics 
    manifest standard.
    
    For a full implementation, see the `core_components.maps.library` module.
    """
    _graphics_manifest: GraphicsManifestDict
    _graphics_resources: Dict[str, Any | None]
    _grid: BaseTileGrid
    state: Dict[str, Any] # Dict[str, Tuple[str, ...] | Dict[str, Dict[str, int | None]]]
    colors: Dict[str, np.ndarray | None]
    dtypes: Dict[str, np.dtype | None ]
    graphics: Dict[str, np.ndarray | None]
    tiles: np.ndarray

    def __init__(self, graphics_manifest: GraphicsManifestDict | None) -> None:

        if graphics_manifest:

            # Initialize the internal copy of the graphics manifest and resources
            self._graphics_manifest = deepcopy(graphics_manifest) # May be possible to not persist this at all if we just use the manifest to initialize the grid and graphics
            self._graphics_resources = dict.fromkeys(graphics_manifest) 
            
            # Link attributes to graphics resources
            for key in self._graphics_resources.keys():
                    setattr(self, key, self._graphics_resources[key])
            
            # Copy information from the graphics manifest into the resources dictionary
            self.state = deepcopy(self._graphics_manifest['state'])
            self.colors = {}

            # Initialize the datatypes, colors, and graphics
            self._initialize_dtypes()
            self._initialize_colors()
            self._initialize_graphics()
            
            # Initialize the grid
            if "grid_tile_dtype" in self.dtypes:
                dtype = self.dtypes["grid_tile_dtype"]
                if dtype is not None:
                    self._grid = BaseTileGrid(dtype)

                    self.grid.size = graphics_manifest['dimensions']["grid_size"]
                    self.grid._initialize_grid()
                    self.tiles = self.grid.tiles
                    self.tiles['graphic_type'][:] = self.graphics['default']

                    self.reset_state()
    
    def _initialize_dtypes(self) -> None:

        """Generates the tile and tile location dtypes based on the graphic definitions"""
        
        # Generate the tile graphic dtype based on the provided color palette
        color_dtypes = [(label, ascii_graphic) for label in self.colors]
        graphic_dtype =  np.dtype([("name", "U16")] + color_dtypes, metadata={"__name__": "tile_graphics"})
        self.dtypes["tile_graphics"] = graphic_dtype

        # Generate the tile grid dtype based on the provided tile graphic and state dtypes
        graphic_dtypes = [('graphic_type', graphic_dtype), ('graphic', ascii_graphic)] 
        state_dtypes = [(name, np.bool) for name in self.state['bits']]
        self.dtypes["tile_grid"] = np.dtype( graphic_dtypes + state_dtypes, metadata={"__name__": "grid_tile_dtype"})

    def _initialize_colors(self) -> None:
        """Generates the tile graphic definitions for the map"""
        color_dtype = ascii_graphic
        for color_name, color_def in self._graphics_manifest['colors'].items():
            self.colors[color_name] = np.array(color_def, dtype=color_dtype)

    def _intialize_state_map(self) -> None:
        state_label_map = []
        statebits = self.state['bits']
        dtype_label_bits = self.state['dtype_labels']['fixed_bits']

        for dtype_label, state_def in dtype_label_bits.items():        
            for idx, state in enumerate(self.state['tuples']):
                    # Screen through each state and assign it to a graphic if it matches the fixed state bits
                    label = None

                    for idx, bit in enumerate(state):
                        fixed_bit = state_def[statebits[idx]]
                        if fixed_bit is None:
                            pass

                        elif fixed_bit == int(bit):
                            label = dtype_label

                        else:
                            add_state = False
                            break

                    state_label_map.append(label)

        self.state['state_label_map'] = tuple(state_label_map)
    
    def _initialize_graphics(self) -> None:
        graphic_dtype = self.dtypes['tile_graphics']
        for graphic_name, definition in self._graphics_manifest['graphics'].items():
            name_value = (graphic_name,)
            graphics_value = []

            for label in definition['state_label'].values():
                graphics_value.append(self.colors[label[1]])
            
            values =  name_value + tuple(graphics_value)
            
            graphic = np.array(values, dtype=graphic_dtype)
            self.graphics[graphic_name] = graphic

    @property
    def grid(self) -> BaseTileGrid:
        return self._grid

    @property
    def state_space_array(self) -> np.ndarray:
        return np.array(self.state['tuples']) # 1D State Vector + 1D State Bits = 2D State Space Array

    @property
    def state_space_tensor(self) -> np.ndarray:
        """Returns a tensor of all possible state labels for all tiles on the map.
        NDIMS: 4 
        SHAPE: (m: number of state bits, 
                n: number of possible state vectors,
                x: grid x shape, 
                y: grid y shape)
        """

        n_states = len(self.state['tuples'])
        n_state_bits = len(self.state['bits'])
        ss_array = self.state_space_array # 1D State Vector + 1D State Bits = 2D State Space Array
        ss_3d_tensor = np.concatenate([ss_array] * self.tiles.shape[0]).reshape(self.tiles.shape[0], n_states, n_state_bits) # +1D Grid
        return np.stack([ss_3d_tensor] * self.tiles.shape[1], axis = 1) # +1D Grid = 4D State Space Tensor
    
    @property
    def state_tensor(self) -> np.ndarray:
        """Returns a tensor of state bits for all tiles on the map based on their current states.
        NDIMS: 4 
        SHAPE: (m: number of state bits, 
                n: 1 state vector (current state),
                x: grid x shape, 
                y: grid y shape)
        """
        n_state_bits = len(self.state['bits'])
        state_tensor_dimensions = [self.tiles[bit] for bit in self.state['bits']]
        
        return np.stack(state_tensor_dimensions, axis = 0).transpose(1,2,0).reshape(*self.tiles.shape, n_state_bits) # 1D State Vector + 1D State Bits + 2 Grid Dimensions = 4D State Tensor

    @property
    def state_tensor_aligned(self) -> np.ndarray:
        """Returns a tensor of state bits for all tiles on the map based on their current state duplicated to align with state space tensor.
        NDIMS: 4 
        SHAPE: (m: number of state bits, 
                n: number of possible state vectors (n x current state),
                x: grid x shape, 
                y: grid y shape)
        """
        
        n_states = len(self.state['tuples'])
        state_tensor_dimensions = [self.state_tensor] * n_states
        return np.stack(state_tensor_dimensions, axis=self.state_tensor.ndim - 2) # State Tensor x number of possible states = 4D State Tensor
    
    @property
    def state_space_label_map(self) -> np.ndarray:
        return self.state['state_label_map']

    @property
    def state_index_map(self) -> np.ndarray:
        label_indices = np.where(np.all(self.state_tensor_aligned == self.state_space_tensor, axis=3))

        index_map = np.full(self.tiles.shape, fill_value=-1, dtype=int)
        index_map[label_indices[0], label_indices[1]] = label_indices[2]
        return index_map

    def draw_tile(self, location: TileCoordinate | TileArea | None, tile_type: str = "floor") -> None:
        if location and tile_type in self.graphics and location.parent_map_size == self.grid.size:
            if isinstance(location, TileCoordinate):
                self.tiles['graphic_type'][location.to_xy_tuple] = self.graphics[tile_type]

            elif isinstance(location, TileArea):
                self.tiles['graphic_type'][location.to_slices] = self.graphics[tile_type]

    def reset_tile(self, location: TileCoordinate | TileArea | None) -> None:
        if location and location.parent_map_size == self.grid.size:
            if isinstance(location, TileCoordinate):
                self.tiles['graphic_type'][location.to_xy_tuple] = self.graphics['default']

            elif isinstance(location, TileArea):
                self.tiles['graphic_type'][location.to_slices] = self.graphics['default']

    def update_state_bit(self, bit: str, mask: np.ndarray) -> None:
        self.tiles[bit][:] = mask
    
    def reset_state_bit(self, bit: str) -> None:
        self.tiles[bit][:] = False

    def update_map_state(self) -> None:

        for index in np.unique(self.state_index_map):
            mask = self.state_index_map == index
            label = self.state['state_label_map'][index]
            if label is not None and self.graphics is not None and self.graphics['graphic'] is not None and self.graphics['graphic_type'] is not None:
                self.graphics['graphic'][mask] = self.graphics['graphic_type'][label][mask]

    def reset_state(self) -> None:
        for bit in self.state['bits']:
            self.tiles[bit][:] = False
    
        