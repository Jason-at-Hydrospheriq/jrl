import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.maps.tilemaps import GenericTileMap
from core_components.maps.base import ascii_graphic

def test_generic_tilemap_empty_init():
    # Arrange & Act
    empty_tile_map = GenericTileMap()

    # Assert & Act
    try:
        assert empty_tile_map.width == 1, "Expected 'width' attribute to be 1 in empty GenericTileMap"
        assert empty_tile_map.height == 1, "Expected 'height' attribute to be 1 in empty GenericTileMap"
        assert empty_tile_map.tiles.shape == (1, 1), "Expected 'tiles' attribute shape to be (1, 1) in empty GenericTileMap"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass

def test_generic_tilemap_parameter_init():
    # Arrange & Act
    width = 10
    height = 15
    tile_map = GenericTileMap(size=(width, height))

    # Assert
    try:
        assert tile_map.width == width, "Expected 'width' attribute to match initialized value"
        assert tile_map.height == height, "Expected 'height' attribute to match initialized value"
        assert tile_map.tiles.shape == (width, height), "Expected 'tiles' attribute shape to match (width, height)"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass
        
def test_generic_tilemap_add_area_by_slice():
    # Arrange & Act
    width = 10
    height = 10
    tile_map = GenericTileMap(size=(width, height))

    area = np.s_[2:5, 2:5]

    # Act
    tile_map.add_area(area, tile_type="wall")

    # Assert
    try:
        for x in range(width):
            for y in range(height):
                if 2 <= x < 5 and 2 <= y < 5:
                    expected_tile_type = "wall"
                else:
                    expected_tile_type = "default"

                actual_tile_type = tile_map.tiles['type'][x, y]['name']
                assert actual_tile_type == expected_tile_type, f"Expected tile at ({x}, {y}) to be of type '{expected_tile_type}', but got '{actual_tile_type}'"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass

def test_generic_tilemap_add_area_by_mask():
    # Arrange & Act
    width = 10
    height = 10
    tile_map = GenericTileMap(size=(width, height))

    mask = np.full((width, height), False)
    mask[2:5, 2:5] = True

    # Act
    tile_map.add_area(mask, tile_type="wall")

    # Assert
    try:
        for x in range(width):
            for y in range(height):
                if 2 <= x < 5 and 2 <= y < 5:
                    expected_tile_type = "wall"
                else:
                    expected_tile_type = "default"

                actual_tile_type = tile_map.tiles['type'][x, y]['name']
                assert actual_tile_type == expected_tile_type, f"Expected tile at ({x}, {y}) to be of type '{expected_tile_type}', but got '{actual_tile_type}'"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass
def test_generic_tilemap_resources():
    # Arrange & Act
    tile_map = GenericTileMap()

    # Assert
    try:
        graphics = tile_map._resources['graphics']
        expected_graphics_keys = {"fill_bluebell", "fill_light_yellow", "fill_black", "fill_dark_blue", "fill_golden_yellow"}
        assert set(graphics.keys()) == expected_graphics_keys, "Graphics keys do not match expected keys"

        tile_type_graphic_fields = tile_map._resources['tile_type_graphic_fields']
        expected_fields = ['g_shroud', 'g_explored', 'g_visible']
        assert tile_type_graphic_fields == expected_fields, "Tile type graphic fields do not match expected fields"

        dtypes = tile_map._resources['dtypes']
        assert "tile_graphic" in dtypes, "'tile_graphic' dtype missing in resources"
        assert dtypes["tile_graphic"].metadata["__name__"] == "ascii_graphic", "'tile_graphic' dtype does not match ascii_graphic"
        assert "tile_type" in dtypes, "'tile_type' dtype missing in resources"
        assert dtypes["tile_type"].metadata["__name__"] == "tile_type", "'tile_type' dtype does not match tile_type"
        assert set(dtypes["tile_type"].fields.keys()) == {"name", "g_shroud", "g_explored", "g_visible"}, "'tile_type' dtype fields do not match expected fields"
        assert "tile_location" in dtypes, "'tile_location' dtype missing in resources"
        assert dtypes["tile_location"].metadata["__name__"] == "tile_location", "'tile_location' dtype does not match tile_location"

        tiles = tile_map._resources['tiles']
        expected_tile_types = {"default", "floor", "wall"}
        assert set(tiles.keys()) == expected_tile_types, "Tile types do not match expected types"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass