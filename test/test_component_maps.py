import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.maps.base import MapCoords, ascii_graphic

def test_base_empty_map_coords():
    # Arrange & Act
    empty_coords = MapCoords()

    set_coords = MapCoords()
    set_coords.x = 3
    set_coords.y = 4

    # Act
    try:
        assert not hasattr(empty_coords, "x"), "Expected no 'x' attribute for MapCoords instantiated without parameters"
        assert not hasattr(empty_coords, "y"), "Expected no 'y' attribute for MapCoords instantiated without parameters"

        assert set_coords.x == 3, "Expected 'x' attribute to be 3 after setting"
        assert set_coords.y == 4, "Expected 'y' attribute to be 4 after setting"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_map_coords():
    # Arrange & Act
    coords = MapCoords(3, 4)
    set_coords = MapCoords()
    set_coords.x = 3
    set_coords.y = 4

    # Act & Assert
    try:
        assert coords.x == 3, "Expected 'x' attribute to be 3 for MapCoords instantiated with parameters"
        assert coords.y == 4, "Expected 'y' attribute to be 4 for MapCoords instantiated with parameters"

        assert coords == set_coords, "Expected coords and set_coords to be equal"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_ascii_graphic_dtype():
    # Arrange & Act
    graphic = np.array((ord("A"), (0, 0, 0), (0, 0, 0)), dtype=ascii_graphic)

    # Act & Assert
    try:
        assert graphic['ch'] == ord("A"), "Expected 'ch' field to be ord('A')"
        assert graphic['ch'].dtype == np.int32, "Expected 'ch' field to be of type int32"
        assert np.array_equal(graphic['fg'], (0, 0, 0)), "Expected 'fg' field to be (0, 0, 0)"
        assert graphic['fg'].dtype == np.uint8, "Expected 'fg' field to be of type 3 unsigned bytes"
        assert np.array_equal(graphic['bg'], (0, 0, 0)), "Expected 'bg' field to be (0, 0, 0)"
        assert graphic['bg'].dtype == np.uint8, "Expected 'bg' field to be of type 3 unsigned bytes"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

