import pytest
import numpy as np
from src.core_components.maps.base import BaseTileMap, BaseRoom, BaseMapGenerator, MapCoords, map_dtype, tile_dtype, graphic_dtype

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

def test_base_graphic_dtype():
    # Arrange & Act
    graphic = np.array((ord("A"), (0, 0, 0), (0, 0, 0)), dtype=graphic_dtype)

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

def test_base_tile_dtype():
    # Arrange & Act
    graphic = np.array((ord("A"), (0, 0, 0), (0, 0, 0)), dtype=graphic_dtype)
    tile = np.array(("a"*17, graphic, graphic, graphic), dtype=tile_dtype)

    # Act & Assert
    try:
        assert tile['name'] == "a"*16, "Expected 'name' field to be 'a'*16"
        assert tile['name'].dtype == "U16", "Expected 'name' field to be of type str"
        assert len(tile['name'].item()) == 16, "Expected 'name' field length to be 16 characters"
        assert np.array_equal(tile['shroud'], graphic), "Expected 'shroud' field to match graphic"
        assert np.array_equal(tile['dark'], graphic), "Expected 'dark' field to match graphic"
        assert np.array_equal(tile['light'], graphic), "Expected 'light' field to match graphic"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_map_dtype():
    # Arrange & Act
    graphic = np.array((ord("A"), (0, 0, 0), (0, 0, 0)), dtype=graphic_dtype)
    tile = np.array(("a"*16, graphic, graphic, graphic), dtype=tile_dtype)
    map_tile = np.array((tile, True, False, True, False, graphic), dtype=map_dtype)

    # Act & Assert
    try:
        assert np.array_equal(map_tile['type'], tile), "Expected 'type' field to match tile"
        assert map_tile['traversable'] == True, "Expected 'traversable' field to be True"
        assert map_tile['transparent'] == False, "Expected 'transparent' field to be False"
        assert map_tile['visible'] == True, "Expected 'visible' field to be True"
        assert map_tile['explored'] == False, "Expected 'explored' field to be False"
        assert np.array_equal(map_tile['color'], graphic), "Expected 'color' field to match graphic"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_empty_tile_map():
    # Arrange & Act
    empty_tile_map = BaseTileMap()

    # Assert & Act
    try:
        assert not hasattr(empty_tile_map, "width"), "Expected no width attribute in empty BaseTileMap"
        assert not hasattr(empty_tile_map, "height"), "Expected no height attribute in empty BaseTileMap"
        assert empty_tile_map.tiles is None, "Expected tiles to be None in empty BaseTileMap"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass

def test_base_tile_map():
    # Arrange & Act
    width = 10
    height = 15
    default_graphic = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dtype)
    default_tile = np.array(("floor", default_graphic, default_graphic, default_graphic), dtype=tile_dtype)
    tile_map = BaseTileMap(width=width, height=height, default_tile_type=default_tile)

    set_tile_map = BaseTileMap()
    set_tile_map.width = width
    set_tile_map.height = height
    set_tile_map.tiles['traversable'][5, 5] = True
    set_tile_map.tiles = np.full((width, height), default_tile, dtype=tile_dtype)

    # Assert
    try:
        assert tile_map.width == width, "Expected 'width' attribute to match initialized value"
        assert tile_map.height == height, "Expected 'height' attribute to match initialized value"
        assert tile_map.tiles.shape == (width, height), "Expected 'tiles' attribute shape to match (width, height)"
        assert np.array_equal(tile_map.tiles["type"], default_tile), "Expected all tiles in 'tiles' attribute to match default_tile"
 
    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass