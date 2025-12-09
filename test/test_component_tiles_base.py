import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.tiles.base import TileCoordinates, ascii_graphic, new_tile_location_dtype

# Test Cases for TileCoordinates
def test_base_empty_coords():
    # Arrange & Act
    empty_coords = TileCoordinates()

    set_coords = TileCoordinates()
    set_coords.x = 3
    set_coords.y = 4
    set_coords.parent_map_size = (10, 10)

    # Act
    try:
        assert not hasattr(empty_coords, "x"), "Expected no 'x' attribute for TileCoordinates instantiated without parameters"
        assert not hasattr(empty_coords, "y"), "Expected no 'y' attribute for TileCoordinates instantiated without parameters"
        assert not hasattr(empty_coords, "map_size"), "Expected no 'map_size' attribute for TileCoordinates instantiated without parameters"

        assert set_coords.x == 3, "Expected 'x' attribute to be 3 after setting"
        assert set_coords.y == 4, "Expected 'y' attribute to be 4 after setting"
        assert set_coords.parent_map_size == (10, 10), "Expected 'map_size' attribute to be (10, 10) after setting"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_empty_coords_to_types():
    # Arrange & Act
    empty_coords = TileCoordinates()

    set_coords = TileCoordinates()
    set_coords.x = 5
    set_coords.y = 7

    # Act & Assert
    try:
        with pytest.raises(AttributeError):
            _ = empty_coords.to_tuple()
        
        with pytest.raises(AttributeError):
            _ = empty_coords.to_array()
        
        with pytest.raises(AttributeError):
            _ = empty_coords.to_list()

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_partial_coords_to_types():

    # Arrange, Act & Assert
    try:
        with pytest.raises(AttributeError):
            _ = TileCoordinates().to_tuple()
        
        with pytest.raises(AttributeError):
            _ = TileCoordinates(x=2).to_array()
        
        with pytest.raises(AttributeError):
            _ = TileCoordinates(y=3).to_list()

        with pytest.raises(AttributeError):
            _ = TileCoordinates(parent_map_size=(10, 10)).to_tuple()

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_partial_coords_hash():

    # Arrange, Act & Assert
    try:
        with pytest.raises(AttributeError):
            _ = hash(TileCoordinates())
        
        with pytest.raises(AttributeError):
            _ = hash(TileCoordinates(x=2))
        
        with pytest.raises(AttributeError):
            _ = hash(TileCoordinates(y=3))

        with pytest.raises(AttributeError):
            _ = hash(TileCoordinates(parent_map_size=(10, 10)))

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords():
    # Arrange & Act
    coords = TileCoordinates(3, 4, (10, 10))
    set_coords = TileCoordinates()
    set_coords.x = 3
    set_coords.y = 4
    set_coords.parent_map_size = (10, 10)
    
    # Act & Assert
    try:
        assert coords.x == 3, "Expected 'x' attribute to be 3 for TileCoordinates instantiated with parameters"
        assert coords.y == 4, "Expected 'y' attribute to be 4 for TileCoordinates instantiated with parameters"
        assert coords.parent_map_size == (10, 10), "Expected 'map_size' attribute to be (10, 10) for TileCoordinates instantiated with parameters"

        assert coords.x == set_coords.x, "Expected 'x' attributes of both coords to be equal"
        assert coords.y == set_coords.y, "Expected 'y' attributes of both coords to be equal"
        assert coords.parent_map_size == set_coords.parent_map_size, "Expected 'map_size' attributes of both coords to be equal"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_to_types():
    # Arrange & Act
    coords = TileCoordinates(5, 7)

    # Act & Assert
    try:
        tuple_coords = coords.to_tuple()
        array_coords = coords.to_array()
        list_coords = coords.to_list()

        assert tuple_coords == (5, 7), "Expected tuple conversion to be (5, 7)"
        assert np.array_equal(array_coords, np.array([5, 7])), "Expected array conversion to be [5, 7]"
        assert list_coords == [5, 7], "Expected list conversion to be [5, 7]"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_hash():
    # Arrange & Act
    coords1 = TileCoordinates(6, 8, (15, 15))
    coords2 = TileCoordinates(6, 8, (15, 15))
    coords3 = TileCoordinates(1, 2, (15, 15))
    coords4 = TileCoordinates(6, 8, (10, 10))  # Different map_size

    # Act & Assert
    try:
        assert hash(coords1) == hash(coords2), "Expected hashes of coords1 and coords2 to be equal"
        assert hash(coords1) != hash(coords3), "Expected hashes of coords1 and coords3 to be different"
        assert hash(coords1) != hash(coords4), "Expected hashes of coords1 and coords4 to be different due to different map_size"
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_repr():
    # Arrange & Act
    coords = TileCoordinates(1, 2, (10, 10))
    partial_coords1 = TileCoordinates()
    partial_coords1.x = 1
    partial_coords2 = TileCoordinates()
    partial_coords2.y = 2
    partial_coords3 = TileCoordinates()
    partial_coords3.parent_map_size = (10, 10)

    # Act & Assert
    try:
        expected_repr = "TileCoordinates(x=1, y=2, parent_map_size=(10, 10))"
        assert repr(coords) == expected_repr, f"Expected repr to be '{expected_repr}'"
        expected_partial_repr1 = "TileCoordinates(x=1, y=None, parent_map_size=None)"
        assert repr(partial_coords1) == expected_partial_repr1, f"Expected repr to be '{expected_partial_repr1}'"
        expected_partial_repr2 = "TileCoordinates(x=None, y=2, parent_map_size=None)"
        assert repr(partial_coords2) == expected_partial_repr2, f"Expected repr to be '{expected_partial_repr2}'"
        expected_partial_repr3 = "TileCoordinates(x=None, y=None, parent_map_size=(10, 10))"
        assert repr(partial_coords3) == expected_partial_repr3, f"Expected repr to be '{expected_partial_repr3}'"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_equality():
    # Arrange & Act
    coords1 = TileCoordinates(2, 3, (10, 10))
    coords2 = TileCoordinates(2, 3, (10, 10))
    coords3 = TileCoordinates(4, 5, (10, 10))
    coords4 = TileCoordinates(2, 3, (5, 5))  # Different map_size

    # Act & Assert
    try:
        assert coords1 == coords2, "Expected coords1 to be equal to coords2"
        assert coords1 != coords3, "Expected coords1 to not be equal to coords3"
        assert coords1 != coords4, "Expected coords1 to not be equal to coords4 due to different map_size"

        pytest.raises(AttributeError, lambda: coords1 == TileCoordinates())
        pytest.raises(AttributeError, lambda: coords1 == TileCoordinates(x=2))
        pytest.raises(AttributeError, lambda: coords1 == TileCoordinates(y=3))
        pytest.raises(AttributeError, lambda: coords1 == TileCoordinates(parent_map_size=(10, 10)))

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_inbounds():
    # Arrange & Act
    coords_inbounds = TileCoordinates(3, 4, (10, 10))
    coords_out_of_bounds_x = TileCoordinates(10, 4, (10, 10))
    coords_out_of_bounds_y = TileCoordinates(3, 10, (10, 10))
    coords_negative_x = TileCoordinates(-1, 4, (10, 10))
    coords_negative_y = TileCoordinates(3, -1, (10, 10))

    # Act & Assert
    try:
        assert coords_inbounds.is_inbounds, "Expected coords_inbounds to be in bounds"
        assert not coords_out_of_bounds_x.is_inbounds, "Expected coords_out_of_bounds_x to be out of bounds"
        assert not coords_out_of_bounds_y.is_inbounds, "Expected coords_out_of_bounds_y to be out of bounds"
        assert not coords_negative_x.is_inbounds, "Expected coords_negative_x to be out of bounds"
        assert not coords_negative_y.is_inbounds, "Expected coords_negative_y to be out of bounds"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

# Test Cases for ascii_graphic dtype
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

# Test Cases for new_tile_location_dtype function
def test_base_new_tile_location_dtype():
    # Arrange & Act
    tile_type_dtype = np.dtype([("type_name", "U10")])
    graphic_dtype = ascii_graphic
    tile_location_dtype = new_tile_location_dtype(tile_type_dtype, graphic_dtype)

    # Act & Assert
    try:
        expected_fields = ['type', 'traversable', 'transparent', 'visible', 'explored', 'graphic']
        actual_fields = tile_location_dtype.names

        assert actual_fields == tuple(expected_fields), f"Expected fields {expected_fields}, got {actual_fields}"
        assert tile_location_dtype['type'] == tile_type_dtype, "Expected 'type' field to match provided tile_type_dtype"
        assert tile_location_dtype['traversable'] == np.dtype(np.bool_), "Expected 'traversable' field to be of type bool"
        assert tile_location_dtype['transparent'] == np.dtype(np.bool_), "Expected 'transparent' field to be of type bool"
        assert tile_location_dtype['visible'] == np.dtype(np.bool_), "Expected 'visible' field to be of type bool"
        assert tile_location_dtype['explored'] == np.dtype(np.bool_), "Expected 'explored' field to be of type bool"
        assert tile_location_dtype['graphic'] == graphic_dtype, "Expected 'graphic' field to match provided graphic_dtype"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass