import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np
print(path)

from core_components.tiles.library import DEFAULT_CENTER_LOCATION, RectangularRoom, CircularRoom, DEFAULT_CENTER_COORDINATE, DEFAULT_GRID_SIZE
from core_components.tiles.base import TileCoordinate, TileTuple

def test_rectangular_room_empty_init():
    # Arrange & Act
    room = RectangularRoom()

    # Assert
    try:
        assert room.center == DEFAULT_CENTER_COORDINATE, "Expected center to be at DEFAULT_CENTER_COORDINATE"
        assert room.width == DEFAULT_CENTER_COORDINATE.x, "Expected width to be DEFAULT_CENTER_COORDINATE.x"
        assert room.height == DEFAULT_CENTER_COORDINATE.y, "Expected height to be DEFAULT_CENTER_COORDINATE.y"
        assert room.parent_map_size == DEFAULT_CENTER_COORDINATE.parent_map_size, "Expected parent_map_size to match DEFAULT_CENTER_COORDINATE.parent_map_size"
        assert room.top_left == TileCoordinate(TileTuple(([3], [3])), DEFAULT_CENTER_COORDINATE.parent_map_size), "Expected top left corner to be at (0,0)"
        assert room.bottom_right == TileCoordinate(TileTuple(([7], [7])), DEFAULT_CENTER_COORDINATE.parent_map_size), "Expected bottom right corner to be at (width,height)"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_parameter_init():
    # Arrange & Act
    room = RectangularRoom(DEFAULT_CENTER_COORDINATE, width=6, height=6)

    # Assert
    try:
        assert room.center == DEFAULT_CENTER_COORDINATE
        assert room.width == 6, "Expected width to be 6"
        assert room.height == 6, "Expected height to be 6"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_to_mask():
    # Arrange 
    room = RectangularRoom(DEFAULT_CENTER_COORDINATE, width=6, height=6)
    room.wall_thickness = 2

    # Act
    area = room.to_mask

    # Assert
    try:
        expected_area = np.full((10, 10), False, dtype=bool)
        expected_area[4:7, 4:7] = True
        assert np.array_equal(area, expected_area), "Inner area does not match expected area"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_resize():
    # Arrange & Act
    room = RectangularRoom(DEFAULT_CENTER_COORDINATE, width=6, height=6)

    updated_room = RectangularRoom(DEFAULT_CENTER_COORDINATE, width=6, height=6)
    updated_room.width = 8
    updated_room.height = 10

    # Assert
    try:
        assert np.any(room.to_mask != updated_room.to_mask), "Expected masks to differ after resizing"
         
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_room_empty_init():
    # Arrange & Act
    room = CircularRoom()

    # Assert
    try:
        assert room.center == DEFAULT_CENTER_COORDINATE, "Expected center to be at (0,0)"
        assert room.width == 6, "Expected width to be 6"
        assert room.height == 6, "Expected height to be 6"
        assert room.radius == 3, "Expected radius to be 3"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_room_parameter_init():
    # Arrange & Act
    room = CircularRoom(center=DEFAULT_CENTER_COORDINATE, radius=7)

    # Assert
    try:
        assert room.center == DEFAULT_CENTER_COORDINATE, "Expected center to be at (10,10)"
        assert room.width == 14, "Expected width to be 14"
        assert room.height == 14, "Expected height to be 14"
        assert room.radius == 7, "Expected radius to be 7"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_room_inner_area():
    # Arrange & Act
    grid_size = TileTuple( ([50], [50]) )
    center_location = TileTuple( ([20], [20]) )
    center_coordinate = TileCoordinate(center_location, grid_size)

    room = CircularRoom(center=center_coordinate, radius=4)
    grid_size_tuple = room.center._tiletuple_to_xy_tuple(room.parent_map_size)
    inner_radius = room.radius - room.wall_thickness
    expected_area = np.fromfunction(
        lambda xx, yy: (xx - center_coordinate.x) ** 2 + (yy - center_coordinate.y) ** 2 + 2 <= inner_radius ** 2,
        grid_size_tuple, dtype=int)
    
    # Assert
    try:
        inner_area = room.to_mask
        assert np.array_equal(inner_area, expected_area), "Inner area does not match expected area"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass
        