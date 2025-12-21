#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from warnings import warn
import numpy as np
import itertools
from typing import Any, List, Protocol, Dict, Tuple, TypedDict, OrderedDict
from copy import deepcopy
import numpy as np

from core_components.maps.tiles import BaseTileGrid, TileTuple, TileArea, TileCoordinate
from core_components.ui.graphics import ascii_graphic

# A typed dictionary for map graphics
class GraphicsManifestDict(TypedDict):
    dimensions: Dict[str,TileTuple]
    statespace: Dict[str, Tuple[str, ...] | Tuple[tuple, ...] | Dict[str, Any]] | None
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
    """The GraphicTileMap defines the interface for all TileMaps in the game. This ensures that all TileMaps conform to a standard interface. A GraphicTileMap
    holds the graphics, dtypes, and tile states for the map. It has a TileGrid that manages the tile data and provides methods for initializing and manipulating 
    the TileCoordinateSystem. It also has a graphics dictionary that holds the graphic definitions for the tiles. The graphics dictionary can be stored as JSON 
    and is loaded at runtime to set the GraphicTileMap attributes. The GraphicTileMap methods allow for reading, updating, and resetting the tile states and 
    graphics on the map.

    Implementations of this protocol are responsible for managing the state and graphics of the tiles on the map bases on the specific definitions in the graphics 
    manifest. Each new map should have its own associated graphics manifest standard.

    For a full implementation, see the `core_components.maps.library` module.
    """
    _graphics_manifest: GraphicsManifestDict
    _graphics_resources: Dict[str, Any | None]
    _grid: BaseTileGrid
    statespace: Dict[str, Any] | None
    colors: Dict[str, np.ndarray | None]
    dtypes: Dict[str, np.dtype | None ]
    graphics: Dict[str, np.ndarray | None]
    tiles: np.ndarray
    areas: OrderedDict[str, TileArea] = OrderedDict()
    paths: OrderedDict[str, TileArea] = OrderedDict()

    def __init__(self, graphics_manifest: GraphicsManifestDict | None) -> None:

        if graphics_manifest:

            # Initialize the internal copy of the graphics manifest and resources
            self._graphics_manifest = deepcopy(graphics_manifest) # May be possible to not persist this at all if we just use the manifest to initialize the grid and graphics
            self._graphics_resources = dict.fromkeys(graphics_manifest) 
            
            # Link attributes to graphics resources
            for key in self._graphics_resources.keys():
                    setattr(self, key, self._graphics_resources[key])
            
            # Copy information from the graphics manifest into the resources dictionary
            self.statespace = deepcopy(self._graphics_manifest['statespace'])
            self.colors = {}
            self.dtypes = deepcopy(self._graphics_manifest['dtypes'])
            self.graphics = {}

            # Initialize the datatypes, colors, and graphics
            self._initialize_colors()
            self._initialize_dtypes()
            self._initialize_graphics()
            self._initialize_state_vectors()
            self._initialize_state_map()
            
            # Initialize the grid
            if "tile_grid" in self.dtypes:
                dtype = self.dtypes["tile_grid"]
                if dtype is not None:
                    self._grid = BaseTileGrid(dtype)

                    self.grid.size = graphics_manifest['dimensions']["grid_size"]
                    self.grid._initialize_grid()
                    self.tiles = self.grid.tiles
                    self.tiles['graphic_type'][:] = self.graphics['default']

                    self.reset_state()
                    self.update_state()

    def _initialize_colors(self) -> None:
        """Generates the color graphic definitions for the map"""
        color_dtype = ascii_graphic
        for color_name, color_def in self._graphics_manifest['colors'].items():
            self.colors[color_name] = np.array(color_def, dtype=color_dtype)
 
    def _initialize_dtypes(self) -> None:

        """Generates the tile and tile location dtypes based on the graphic definitions"""
        # Generate the tile state vector dtype based on the provided state bits
        if self.statespace is not None:
            state_bit_dtypes = [(name, np.bool) for name in self.statespace['bits']]
            self.dtypes['tile_state_vector'] = np.dtype(state_bit_dtypes, metadata={"__name__": "tile_state_vector"})

        # Generate the tile graphic dtype based on the provided state labels
            state_labels = self.statespace['dtype_labels']
            state_dtypes = [(state_label, ascii_graphic) for state_label in state_labels.get('names', [])]
            self.dtypes['tile_graphic'] = np.dtype([('name', 'U16')] + state_dtypes, metadata={"__name__": "tile_graphic"})

        # Generate the tile grid dtype based on the provided tile graphic and state dtypes
            graphic_dtypes = [('graphic_type', self.dtypes['tile_graphic']), ('graphic', ascii_graphic)]
            self.dtypes["tile_grid"] = np.dtype( graphic_dtypes + state_bit_dtypes, metadata={"__name__": "tile_grid"})

    def _initialize_graphics(self) -> None:
        graphic_dtype = self.dtypes['tile_graphic']
        for graphic_name, package in self._graphics_manifest['graphics'].items():
            graphic = np.empty(1, dtype=graphic_dtype)

            graphic['name'] = graphic_name

            for state, color in package['state_definitions'].items():
                graphic[state] = self.colors[color]
            
            self.graphics[graphic_name] = graphic

    def _initialize_state_vectors(self) -> None:
        if self.statespace is not None and self.statespace['vector_tuples'] is not None:
            state_vectors = []
            for vector_tuple in self.statespace['vector_tuples']:
                vector = np.array(list(vector_tuple), dtype=self.dtypes['tile_state_vector'])
                state_vectors.append(vector)
            self.statespace['vectors'] = state_vectors

    def _initialize_state_map(self) -> None:
        label_map = []
        if self.statespace is not None and self.statespace['bits'] is not None and self.statespace['dtype_labels'] is not None:
            for statespace_vector_tuple in self.statespace['vector_tuples']:
                add_label = False
                statespace_vector = np.array(list(statespace_vector_tuple))
                fixed_bit_vector_tuples = self.statespace['dtype_labels']['fixed_bits']
                for label, vector_tuple in fixed_bit_vector_tuples.items():
                    fixed_bit_vector = np.array(list(vector_tuple))        
                    add_label = np.array_equal(np.where(statespace_vector == fixed_bit_vector), np.where(fixed_bit_vector != None))
                    if add_label:
                        label_map.append(label)
                        break

            self.statespace['label_map'] = tuple(label_map)
    
    @property
    def grid(self) -> BaseTileGrid:
        return self._grid

    @property
    def center(self) -> TileCoordinate:
        return self.grid.get_location(self.grid.center[0], self.grid.center[1]) 
    
    @property
    def statespace_array(self) -> np.ndarray | None:
        if self.statespace and self.statespace['vector_tuples'] is not None:
            return np.array(self.statespace['vector_tuples']) # 1D State Vector + 1D State Bits = 2D State Space Array

    @property
    def statespace_tensor(self) -> np.ndarray | None:
        """Returns a tensor of all possible state labels for all tiles on the map.
        NDIMS: 4 
        SHAPE: (m: number of state bits, 
                n: number of possible state vectors,
                x: grid x shape, 
                y: grid y shape)
        """
        if self.statespace is not None and self.statespace['vector_tuples'] is not None:
            n_states = len(self.statespace['vector_tuples'])
            n_state_bits = len(self.statespace['bits'])
            ss_array = self.statespace_array # 1D State Vector + 1D State Bits = 2D State Space Array
            ss_3d_tensor = np.concatenate([ss_array] * self.tiles.shape[0]).reshape(self.tiles.shape[0], n_states, n_state_bits) # +1D Grid
            return np.stack([ss_3d_tensor] * self.tiles.shape[1], axis = 1) # +1D Grid = 4D State Space Tensor
        
    @property
    def statespace_label_map(self) -> np.ndarray | None:
        if self.statespace is not None:
            return np.array(self.statespace['label_map'])

    @property
    def statespace_index_map(self) -> np.ndarray:
        label_indices = np.where(np.all(self.state_tensor_aligned == self.statespace_tensor, axis=3))

        index_map = np.full(self.tiles.shape, fill_value=-1, dtype=int)
        index_map[label_indices[0], label_indices[1]] = label_indices[2]
        return index_map
        
    @property
    def state_tensor(self) -> np.ndarray | None:
        """Returns a tensor of state bits for all tiles on the map based on their current states.
        NDIMS: 4 
        SHAPE: (m: number of state bits, 
                n: 1 state vector (current state),
                x: grid x shape, 
                y: grid y shape)
        """
        if self.statespace is not None and self.statespace['vector_tuples'] is not None:
            n_state_bits = len(self.statespace['bits'])
            state_tensor_dimensions = [self.tiles[bit] for bit in self.statespace['bits']]
            
            return np.stack(state_tensor_dimensions, axis = 0).transpose(1,2,0).reshape(*self.tiles.shape, 1, n_state_bits) # 1D State Vector + 1D State Bits + 2 Grid Dimensions = 4D State Tensor

    @property
    def state_tensor_aligned(self) -> np.ndarray | None:
        """Returns a tensor of state bits for all tiles on the map based on their current state duplicated to align with state space tensor.
        NDIMS: 4 
        SHAPE: (m: number of state bits, 
                n: number of possible state vectors (n x current state),
                x: grid x shape, 
                y: grid y shape)
        """
        if self.statespace is not None and self.statespace['vector_tuples'] is not None and self.statespace_tensor is not None:
            n_state_bits = len(self.statespace['bits'])
            n_states = len(self.statespace['vector_tuples'])
            state_tensor_dimensions = [self.state_tensor] * n_states
            
            return np.stack(state_tensor_dimensions, axis=2).reshape(*self.tiles.shape, n_states, n_state_bits) # type: ignore State Tensor x number of possible states = 4D State Tensor

    def get_tiles(self) -> np.ndarray | None:
        if self.graphics is not None:
            return deepcopy(self.tiles['graphic_type'])

    def set_tiles(self, layout: np.ndarray | None = None, graphic_name: str = 'default', join_type: str = 'merge') -> None:

        if layout is None:
            merge_layout = self.get_tile_layout()
        else:
            merge_layout = layout

        if merge_layout is not None and self.graphics is not None and self.statespace is not None:
            # Merge the new graphic onto the existing tile layout
            merged_layout = self.merge_tile_layout(merge_layout, graphic_name=graphic_name, join_type=join_type)
            
            # Reset and set the tile layout
            self.set_tile_layout(merged_layout, graphic_name) # Set

            # Set the fixed state bits for the tiles based on the graphic
            self.set_fixed_state_bits(merged_layout, graphic_name=graphic_name)

    def reset_tiles(self) -> None:
        if self.graphics is not None:
           self.tiles['graphic_type'][:] = self.graphics['default']

    def get_statespace_vector(self, index: int) -> np.ndarray | None:
        if self.statespace is not None:
            return deepcopy(self.statespace['vectors'][index])

    def get_tile_layout(self, graphic_name: str | None = None) -> np.ndarray | None:
        layout = None

        if graphic_name is None:
            layout = np.full(self.tiles.shape, fill_value=True, dtype=bool)
        
        if self.graphics is not None and graphic_name is not None:
            tiles = self.get_tiles()
            if tiles is not None:
                layout = tiles['name'] == graphic_name
        
        return layout

    def merge_tile_layout(self, layout: np.ndarray, graphic_name: str = 'default', join_type: str = 'merge', ) -> np.ndarray | None:
        """Merge a new graphic layout onto the existing tile layout.

        Args:
            layout: A boolean mask representing the area to update.
            graphic_name: The name of the graphic to apply to the specified layout.
            join_type: The type of join operation to perform ('merge', 'outer', 'inner').
        """
        current_layout = None

        if self.graphics is not None:
            current_layout = self.get_tile_layout(graphic_name)

        if self.graphics and self.statespace and current_layout is not None:
            match join_type:
            
                case 'merge':
                    return current_layout | layout # NAND: Keep all tiles labeled True in both layouts
                case 'outer':
                    return current_layout ^ layout # XOR: Keep only True tiles that are different between layouts
                case 'inner':
                    return current_layout & layout # NOR: Keep only True tiles that are the same between layouts
                
    def set_fixed_state_bits(self, layout: np.ndarray | None = None, *, graphic_name: str) -> None:
        """Set the fixed state bits for a given graphic on the specified layout.
        
        Args:
            layout: A boolean mask representing the area to update.
            graphic_name: The name of the graphic to apply to the specified layout.
            join_type: The type of join operation to perform ('merge' or 'replace').
        """
        fixed_bits = self._graphics_manifest['graphics'][graphic_name]['fixed_state_bits']
        if layout is None:
            layout = self.get_tile_layout() #type: ignore

        if layout is not None and self.graphics is not None and self.statespace is not None:
            for idx, bit in enumerate(fixed_bits):
                bit_name = self.statespace['bits'][idx]
                if bit is not None:
                    blocked_layout = layout == bool(bit) # Make sure layout matches the fixed bit value, ie floor=True in the layout, but False for blocks_movement
                    self.set_state_bits(bit_name, blocked_layout) #type: ignore

    def set_tile_layout(self, layout: np.ndarray | None = None, graphic_name: str = 'default') -> None:
        """Set a new graphic layout on the tile map.

        Args:
            layout: A boolean mask representing the area to update.
            graphic_name: The name of the graphic to apply to the specified layout.
        """
        if layout is not None and self.graphics is not None:
            self.tiles['graphic_type'][layout] = self.graphics[graphic_name]
        elif self.graphics is not None and layout is None and graphic_name != 'default':
            self.tiles['graphic_type'][:] = self.graphics[graphic_name]
        elif self.graphics is not None and layout is None and graphic_name == 'default':
            self.tiles['graphic_type'][:] = self.graphics['default']

    def get_state_bits(self, bit: str) -> np.ndarray:
        return deepcopy(self.tiles[bit])
    
    def set_state_bits(self, bit: str, mask: np.ndarray) -> None:
        self.tiles[bit][:] = mask

    def reset_state_bits(self, bit: str) -> None:
        self.tiles[bit][:] = False

    def get_state(self) -> np.ndarray | None:
        if self.graphics is not None:
            return deepcopy(self.tiles['graphic'][:])
    
    def update_state(self) -> None:
        if self.statespace is not None:
            for index in np.unique(self.statespace_index_map):
                mask = self.statespace_index_map == index
                state_label = self.statespace['label_map'][index]
                color = self.tiles['graphic_type'][state_label][mask]
                if color is not None:
                    self.tiles['graphic'][mask] = color

    def reset_state(self) -> None:
        if self.statespace is not None:
            for bit in self.statespace['bits']:
                self.tiles[bit][:] = False
            
    def reset_all(self) -> None:
        self.reset_tiles()
        self.reset_state()
        self.areas.clear()
        self.paths.clear()

    def object_collision(self, location: TileCoordinate) -> bool:
        isblocked = False
        isblocked = bool(self.tiles['blocks_movement'][location.x, location.y])
        return isblocked