#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, NewType, OrderedDict, Protocol, AbstractSet, Tuple, TypeVar, TypedDict, runtime_checkable
from warnings import warn
from transitions import Machine
from queue import Queue
import numpy as np
from numpy import random  


@runtime_checkable
class StatefulObject(Protocol):
    """The StatefulObject Protocol is a mixin class that has a 'machine' attribute."""
    machine: Machine # Has a state machine that defines states and transitions.


@runtime_checkable
class StoredStateObject(Protocol):
    """The StoredStateObject Protocol is a mixin class that has a 'store' attribute. It is used to refer to a StatefulObject instance for context."""
    store: StatefulObject | None 


@runtime_checkable
class StateActionObject(Protocol):
    """
    A StateActionObject is any object with 'store' and 'handler' attributes. The 'store' attribute refers to a StatefulObject instance for context,
    and the 'handler' attribute refers to a StateHandler instance that can transform and send the object to a State queue.

    Duck Types: StatefulObject

    """
    store: StatefulObject | None
    handler: StateHandler | None

S = TypeVar('S', bound=StateActionObject, covariant=True)

@runtime_checkable
class StateBehaviorObject[S](Protocol):
    """The StatefulBehaviorObject Protocol is a mixin class that has a 'state' and 'behaviors' attribute."""
    behaviors: AbstractSet[Tuple[str, S]] | None # Has a set of behaviors (events/actions) that can be queued for execution by the game engine.


@runtime_checkable
class EventTransformer[S](StateBehaviorObject, Protocol):
    """
    The EventTransformer Protocol is a mixin class that has methods for sending events and transformed actions to queues.
    
    Duck Types: StatefulObject
    """
    store: StatefulObject | None

    def transform(self, event: StateActionObject) -> StateActionObject | None:
        """Transforms an event into an action based on the defined behaviors."""
        ...


@runtime_checkable
class GameLoopObject[S](Protocol):
    """
    The GameLoopObject Protocol is a mixin class that has an events and actions queue.
    
    Duck Types: StatefulObject
    """
    store: StatefulObject | None
    events: Queue[S]
    actions: Queue[S]
    
    def send(self, loop_item: StateActionObject) -> bool:
        """Sends an event or action to the appropriate queue."""
        ...


@runtime_checkable
class StateHandler[S](EventTransformer, GameLoopObject, Protocol):
    """
    The StateHandler Protocol is a mixin class that combines the EventTransformer and GameLoopObject Protocols.
    
    Duck Types: StatefulObject
    """
    machine: Machine
    
    def handle(self, event: StateActionObject | None) -> bool:
        """Handles an event by transforming and sending it to the appropriate queue."""
        ...


@runtime_checkable
class EntityActionObject(StateActionObject, Protocol):
    """The EntityActionObject Protocol is a mixin class that has an 'entity' attribute."""
    entity: StatefulObject | None


@runtime_checkable
class EntityDestinationObject(EntityActionObject, Protocol):
    """The EntityDestinationObject Protocol is a mixin class that has a 'destination' attribute."""
    destination: TileCoordinate | None


@runtime_checkable
class EntityTargetObject(EntityActionObject, Protocol):
    """The EntityTargetObject Protocol is a mixin class that has a 'target' attribute."""
    target: StatefulObject | None


@runtime_checkable
class GameAction(StateActionObject, Protocol):
    """
    The GameAction Protocol is a mixin class that has 'store' and 'handler' attributes. The 'store' attribute refers to a StatefulObject instance for context,
    and the 'handler' attribute refers to a StateHandler instance that can transform and send the action to a State queue.

    Duck Types: StatefulObject

    """

    def perform(self) -> None:
        """Performs the action."""
        ... 
    
@runtime_checkable
class GameEvent(StateActionObject, Protocol):
    """
    The GameEvent Protocol is a mixin class that has 'store' and 'handler' attributes. The 'store' attribute refers to a StatefulObject instance for context,
    and the 'handler' attribute refers to a StateHandler instance that can transform and send the action to a State queue.

    Duck Types: StatefulObject

    """

    def trigger(self) -> None:
        """Performs the action."""
        ... 

@runtime_checkable
class EntitySubState(Protocol):
    machine: Machine
    name: str
    store: StatefulObject
    state_bit_dtypes: Tuple[np.dtype, ...]


@runtime_checkable
class EntityParentState(Protocol):
    machine: Machine
    substates: list[EntitySubState]


@runtime_checkable
class GameEntity(Protocol):
    """The EntityActionObject Protocol is a mixin class that has an 'entity' attribute."""
    store: StatefulObject | None
    machine: Machine
    location: TileCoordinate | None
    blocks_movement: bool | None


TileTuple = NewType("TileTuple", tuple[List[int], List[int]])


# A typed dictionary for map graphics
class GraphicsManifestDict(TypedDict):
    dimensions: Dict[str,TileTuple]
    statespace: Dict[str, Tuple[str, ...] | Tuple[tuple, ...] | Dict[str, Any]] | None
    colors: Dict[str, Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]]
    dtypes: Dict[str, np.dtype | None ]
    graphics: Dict[str, Any]


class UIManifestDict(TypedDict):
    widgets: Dict[str, Dict[str, Any]]


class TileCoordinateSystem:

    """A protocol defining methods for coordinate systems using TileTuple."""

    __slots__ = ("_size",)
    _size: TileTuple
    #TODO connect this with maps so that map size informatoin is consistent across components

    @property
    def _origin(self) -> TileTuple:
        return TileTuple( ([0], [0]) )

    @property
    def _system_coordinates(self) -> TileTuple:
        top_left = self._origin
        bottom_right = self._size

        return self._tiletuple_to_area_tiletuple(top_left, bottom_right)

    def _xy_to_tiletuple(self, x: int, y: int) -> TileTuple:
        return TileTuple(([x], [y]))

    def _tiletuple_to_area_tiletuple(self, top_left: TileTuple, lower_right: TileTuple) -> TileTuple:
        if top_left is None or lower_right is None:
            raise ValueError("Both top_left and lower_right TileTuple parameters must be provided.")

        if top_left[0][0] > lower_right[0][0] or top_left[1][0] > lower_right[1][0]:
            raise ValueError("Top-left coordinates must be less than or equal to bottom-right coordinates.")

        x_range = list(range(top_left[0][0], lower_right[0][0] + 1))
        y_range = list(range(top_left[1][0], lower_right[1][0] + 1))

        if top_left[0][0] == lower_right[0][0] and top_left[1][0] == lower_right[1][0]:
            warn("Top-left and bottom-right coordinates are the same; area will be a single point.", UserWarning)
            x_range = [top_left[0][0]]
            y_range = [top_left[1][0]]
        if top_left[0][0] == lower_right[0][0]:
            warn("The x coordinates are the same; area will be a line.", UserWarning)
            x_range = [top_left[0][0]]
        if top_left[1][0] == lower_right[1][0]:
            warn("The y coordinates are the same; area will be a line.", UserWarning)
            y_range = [top_left[1][0]]

        return TileTuple( (x_range, y_range) )

    def _tiletuple_to_xy_tuple(self, x_y: TileTuple) -> Tuple[int, int]:
        return (x_y[0][0], x_y[1][0])

    def _tiletuple_to_tile_coordinate(self, x_y: TileTuple) -> TileCoordinate:
        return TileCoordinate(x_y, self._size)

    @staticmethod
    def _overhang(dimension1: TileTuple, dimension2: TileTuple) -> bool:
        dim1_set1 = set(dimension1[0])
        dim1_set2 = set(dimension2[0])
        dim1_overhang = dim1_set2.issubset(dim1_set1)

        dim2_set1 = set(dimension1[1])
        dim2_set2 = set(dimension2[1])
        dim2_overhang = dim2_set2.issubset(dim2_set1)

        return not (dim1_overhang and dim2_overhang)

    @staticmethod
    def _overlap(dimension1: TileTuple, dimension2: TileTuple) -> bool:
        dim1_set1 = set(dimension1[0])
        dim1_set2 = set(dimension2[0])
        dim1_overlap = dim1_set1.isdisjoint(dim1_set2)

        dim2_set1 = set(dimension1[1])
        dim2_set2 = set(dimension2[1])
        dim2_overlap = dim2_set1.isdisjoint(dim2_set2)

        return not (dim1_overlap or dim2_overlap)


class TileCoordinateSystemElement(TileCoordinateSystem):
    """A protocol defining elements with parent coordinate systems that utilize TileCoordinateSystem methods."""

    @property
    def parent_map_size(self) -> TileTuple:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._size

    @parent_map_size.setter
    def parent_map_size(self, value: TileTuple) -> None:
        self._size = value

    @property
    def parent_map_width(self) -> int:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._size[0][0]

    @property
    def parent_map_height(self) -> int:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._size[1][0]

    @property
    def parent_map_coords(self) -> TileTuple:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'parent_map_size' has not been set.")
        return self._system_coordinates


class TileCoordinate(TileCoordinateSystemElement):
    """A simple class for x,y map coordinates. This class does not initialize the x,y attributes by default and can be 
    instantiated without parameters.

    Attributes:
        x: int, The x coordinate on the map
        y: int, The y coordinate on the map
    Empty Initialization:
        coords = TileCoordinate()
    Parameterized Initialization:
        coords = TileCoordinate(3, 4)
    Methods:
        __eq__(other: object) -> bool:  Compare two TileCoordinate instances for equality
    Raises:
        ValueError: If x or y are not integers.
        AttributeError: If x or y are accessed before being set.
    """
    __slots__ = ("x", "y")

    x: int
    y: int

    def __init__(self,
                 location: Tuple[List[int], List[int]] | None = None,
                 parent_map_size: TileTuple | None = None) -> None:
        if location is not None:
            if not location[0]:
                pass
            else:
                self.x = location[0][0]
            if not location[1]:
                pass
            else:
                self.y = location[1][0]
        if parent_map_size is not None:
            if not parent_map_size[0] or not parent_map_size[1]:
                pass
            else:
                self._size = parent_map_size

    def __eq__(self, other: object) -> bool:
        try:
            if not isinstance(other, TileCoordinate):
                return False

            return hash(self) == hash(other)

        except AttributeError as e:
            e.add_note("Both TileCoordinate instances must have 'x', 'y', and 'map_size' attributes set for comparison.")
            raise

    def __repr__(self) -> str:
        rep = "TileCoordinate("

        if hasattr(self, "x"):
            rep += f"x={self.x}, "
        else:
            rep += "x=None, "

        if hasattr(self, "y"):
            rep += f"y={self.y}, "
        else:
            rep += "y=None, "

        if hasattr(self, "parent_map_size"):
            rep += f"parent_map_size={self.parent_map_size})"
        else:
            rep += "parent_map_size=None)"

        return rep

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.parent_map_size[0][0], self.parent_map_size[1][0]))

    @property
    def to_xy_tiletuple(self) -> TileTuple:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to tuple.")

        return TileTuple( ([self.x], [self.y]) )

    @property
    def is_inbounds(self) -> bool:
        if not hasattr(self, "x") or not hasattr(self, "y") or not hasattr(self, "_size"):
            raise AttributeError("Attributes 'x', 'y', and 'parent_map_size' must be set to check inbounds status.")

        return self._overlap(self.parent_map_coords, self.to_xy_tiletuple)

    @property
    def to_tuple(self) -> Tuple[int, int]:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to tuple.")

        return (self.x, self.y)

    @property
    def to_array(self) -> np.ndarray:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to array.")

        return np.array([self.x, self.y])

    @property
    def to_list(self) -> list[int]:
        if not hasattr(self, "x") or not hasattr(self, "y"):
            raise AttributeError("Both 'x' and 'y' attributes must be set before converting to list.")

        return [self.x, self.y]

    @classmethod
    def from_tuple(cls, coords: Tuple[int, int], parent_map_size: TileTuple | None = None) -> TileCoordinate:
        """Create a TileCoordinate from a tuple of (x, y) coordinates."""
        if not isinstance(coords, tuple) or len(coords) != 2:
            raise ValueError("coords must be a tuple of (x, y).")

        x, y = coords
        return cls( TileTuple( ([x], [y]) ), parent_map_size=parent_map_size )


class TileArea(TileCoordinateSystemElement):

    """A simple class for defining rectangular areas on a map using TileCoordinate for top-left and bottom-right corners.

    Attributes:
        top_left: TileCoordinate, The top-left corner of the area
        bottom_right: TileCoordinate, The bottom-right corner of the area
    Initialization:
        area = TileArea(top_left: TileCoordinate, bottom_right: TileCoordinate)
    Methods:
        width() -> int: Returns the width of the area
        height() -> int: Returns the height of the area
    Raises:
        ValueError: If top_left or bottom_right are not TileCoordinate instances.
    """
    __slots__ = ("_top_left", "_bottom_right", "_center", "_height", "_width")

    _top_left: TileCoordinate
    _bottom_right: TileCoordinate
    _center: TileCoordinate
    _height: int
    _width: int
    _min_dimension_size: int = 3

    def __init__(self, center: TileCoordinate | None = None,
                 height: int | None = None,
                 width: int | None = None) -> None:

        if center:
            self._center = center
            self.parent_map_size = center.parent_map_size
        if height:
            self.height = height
        if width:
            self.width = width

        self._align_corners()

    def __repr__(self) -> str:
        return f"TileArea(center={self.center}, width={self.width}, height={self.height})"

    def __hash__(self) -> int:
        return hash((self.center, self.width, self.height))

    def __eq__(self, other: object) -> bool:
        try:
            if not isinstance(other, TileArea):
                return False

            return hash(self) == hash(other)

        except AttributeError as e:
            e.add_note("Both MapArea instances must have 'top_left' and 'bottom_right' attributes set for comparison.")
            raise

    @property
    def top_left(self) -> TileCoordinate:
        if not hasattr(self, "_top_left"):
            raise AttributeError("Attribute 'top_left' has not been set.")
        return self._top_left

    @property
    def bottom_right(self) -> TileCoordinate:
        if not hasattr(self, "_bottom_right"):
            raise AttributeError("Attribute 'bottom_right' has not been set.")
        return self._bottom_right

    @property
    def width(self) -> int:
        if not hasattr(self, "_width"):
            raise AttributeError("Attribute 'width' has not been set.")
        return self._width

    @width.setter
    def width(self, value: int) -> None:
        if value < self._min_dimension_size:
            warn(f"Width {value} is less than minimum dimension size {self._min_dimension_size}. Setting width to minimum.", UserWarning)
            value = self._min_dimension_size

        self._width = value
        self._align_corners()

    @property
    def height(self) -> int:
        if not hasattr(self, "_height"):
            raise AttributeError("Attribute 'height' has not been set.")
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        if value < self._min_dimension_size:
            warn(f"Height {value} is less than minimum dimension size {self._min_dimension_size}. Setting height to minimum.", UserWarning)
            value = self._min_dimension_size

        self._height = value
        self._align_corners()

    @property
    def center(self) -> TileCoordinate:
        if not hasattr(self, "_center"):
            raise AttributeError("Attribute 'center' has not been set.")
        return self._center

    @center.setter
    def center(self, value: TileCoordinate) -> None:
        self._center = value
        self._size = value.parent_map_size
        self._align_corners()

    @property
    def is_inbounds(self) -> bool:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right") or not hasattr(self, "_size"):
            raise AttributeError("Attributes 'top_left', 'bottom_right', and 'parent_map_size' must be set to check inbounds status.")

        overhang = self._overhang(self.parent_map_coords, self.to_area_indicies_tuple)
        overlap = self._overlap(self.parent_map_coords, self.to_area_indicies_tuple)

        return overlap and not overhang

    @property
    def to_area_indicies_tuple(self) -> TileTuple:
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before converting to area tuple.")

        top_left_grid_indices = self.top_left.to_xy_tiletuple
        bottom_right_grid_indices = self.bottom_right.to_xy_tiletuple

        return self._tiletuple_to_area_tiletuple(top_left_grid_indices, bottom_right_grid_indices)

    @property
    def to_slices(self):
        if not hasattr(self, "top_left") or not hasattr(self, "bottom_right"):
            raise AttributeError("Both 'top_left' and 'bottom_right' attributes must be set before converting to slices.")

        return (slice(self.top_left.x, self.bottom_right.x + 1), slice(self.top_left.y, self.bottom_right.y + 1))

    @property
    def to_mask(self) -> np.ndarray:
        """ Return the coordinates of the area covered by this TileArea as a 2D numpy array of TileCoordinates."""
        map_tuple = self._tiletuple_to_xy_tuple(self.parent_map_size)
        mask = np.full(map_tuple, fill_value=False, dtype=bool)
        mask[self.to_slices] = True
        return mask

    def contains(self, location: TileCoordinate) -> bool:
        """Check if this area contains the given location."""
        mask = self.to_mask
        return bool(mask[location.x, location.y])

    def intersects(self, another_area: TileArea):
        """Check if this area intersects with another area."""
        if not isinstance(another_area, TileArea):
            raise TypeError("another_area must be an instance of TileArea.")

        return self._overlap(self.to_area_indicies_tuple, another_area.to_area_indicies_tuple)

    def get_random_location(self) -> TileCoordinate:
        """Return a random location within this area."""
        open_tiles = np.argwhere(self.to_mask)
        choices = np.arange(len(open_tiles))
        choice = random.choice(choices)
        x, y = open_tiles[choice]

        return TileCoordinate.from_tuple((x,y), self.parent_map_size)

    def _align_corners(self) -> None:
        if not hasattr(self, "_center") or not hasattr(self, "_width") or not hasattr(self, "_height"):
            warn("Cannot align corners without 'center', 'width', and 'height' attributes set.", UserWarning)
            return

        half_width = self._width // 2
        half_height = self._height // 2
        top_x = self._center.x - half_width
        top_y = self._center.y - half_height
        bottom_x = self._center.x + half_width
        bottom_y = self._center.y + half_height

        top_left_xy = TileTuple( ([top_x], [top_y]) )
        bottom_right_xy = TileTuple( ([bottom_x], [bottom_y]) )

        self._top_left = TileCoordinate(top_left_xy, self._center.parent_map_size)
        self._bottom_right = TileCoordinate(bottom_right_xy, self._center.parent_map_size)


class BaseTileGrid(TileCoordinateSystem):
    """A simple class for defining rectangular areas of Tiles using TileCoordinate for top-left and bottom-right corners.
    A TileArea is a 2D numpy array of Tiles. Tiles are defined using a custom numpy dtype defined in the new_tile_type
    function. A TileArea can be initialized with or without parameters."""

    _tiles: np.ndarray
    _dtype: np.dtype

    def __init__(self, dtype: np.dtype, size: TileTuple | None = None) -> None:

        self._dtype = dtype
        if self._dtype.names:
            for prop in self._dtype.names:
                if not prop.startswith("_"):
                    setattr(self, prop, self._dtype[prop])

        if size is not None:
            self.size = size

    @property
    def width(self) -> int:
        return self.size[0][0]

    @property
    def height(self) -> int:
        return self.size[1][0]

    @property
    def center(self) -> Tuple[int, int]:
        return (self.width // 2, self.height // 2)

    @property
    def size(self) -> TileTuple:
        if not hasattr(self, "_size"):
            raise AttributeError("Attribute 'size' has not been set.")
        return self._size

    @size.setter
    def size(self, value: TileTuple) -> None:
        self._size = value
        if hasattr(self, "_dtype"):
            self._initialize_grid()

    @property
    def dtype(self) -> np.dtype:
        if not hasattr(self, "_dtype"):
            raise AttributeError("Attribute 'dtype' has not been set.")
        return self._dtype

    @property
    def tiles(self) -> np.ndarray:
        if not hasattr(self, "_tiles"):
            raise AttributeError("Attribute 'tiles' has not been set.")
        return self._tiles

    def get_location(self, x: int, y: int) -> TileCoordinate:
        return TileCoordinate( TileTuple( ([x], [y]) ), self._size )

    def get_area(self, center: Tuple[int, int], height: int, width: int):
        center_location = self.get_location(x = center[0], y = center[1])
        return TileArea(center=center_location, height=height, width=width)

    def set_area(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def _initialize_grid(self) -> None:
        """This method should be overridden by subclasses to initialize the tile grid."""
        self._tiles = np.zeros((self.width, self.height), dtype=self._dtype)


# Tile graphic dtype definition
ascii_graphic = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors.
        ("bg", "3B"),
    ], metadata={"__name__": "ascii_graphic"}
)
# SHROUD represents unexplored, unseen tiles
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=ascii_graphic)


class GraphicTileMap(Protocol):
    """The GraphicTileMap defines the interface for all TileMaps in the game. This ensures that all TileMaps conform to a standard interface. A GraphicTileMap
    holds the graphics, dtypes, and tile states for the map. It has a TileGrid that manages the tile data and provides methods for initializing and manipulating 
    the TileCoordinateSystem. It also has a graphics dictionary that holds the graphic definitions for the tiles. The graphics dictionary can be stored as JSON 
    and is loaded at runtime to set the GraphicTileMap attributes. The GraphicTileMap methods allow for reading, updating, and resetting the tile states and 
    graphics on the map.

    Implementations of this protocol are responsible for managing the state and graphics of the tiles on the map bases on the specific definitions in the graphics 
    manifest. Each new map should have its own associated graphics manifest standard.

    For a full implementation, see the `atlas.components.library` module.
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

    def is_blocked(self, location: TileCoordinate) -> bool:
        return bool(self.tiles['blocks_movement'][location.x, location.y])


class BaseMapGenerator(Protocol):
    map_template: GraphicTileMap

    """
    The BaseMapGenerator Protocol defines the methods that all map generators must implement. This protocol ensures that all map generators can be used 
    interchangeably in the game engine. The generator is a component of the Atlas object and is responsible for creating and populating the map with rooms, 
    corridors, and other elements. The generator does NOT handle the placement of entities or items on the map. It only creates the map object and returns a copy
    of it to the Atlas object.

    For a full implementation, see the `core_components.generators` module.
    """

    def generate(self) -> GraphicTileMap:
        raise NotImplementedError()

    def add(self,
                area: TileArea,
                center: TileCoordinate,
                size: TileTuple) -> TileArea | None:

        method_name = "_add_" + area.__class__.__name__.lower()
        method = getattr(self, method_name, None)
        if method:
            return method(area, center, size)
        return None