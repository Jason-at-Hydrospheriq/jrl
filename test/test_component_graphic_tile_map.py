import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.maps.base import ascii_graphic, GraphicTileMap, DEFAULT_MANIFEST
from core_components.tiles.base import BaseTileGrid, TileTuple


# Test Cases for ascii_graphic dtype
def test_graphic_tile_map_ascii_graphic_dtype():
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
def test_graphic_tile_map_dtype_generator():
    # Arrange & Act
    tile_type_dtype = np.dtype([("type_name", "U10")])
    graphic_dtype = ascii_graphic
    tile_location_dtype = grid_tile_dtype(tile_type_dtype, graphic_dtype)

    # Act & Assert
    try:
        expected_fields = ['graphic_type', 'traversable', 'transparent', 'visible', 'explored', 'graphic_state']
        actual_fields = tile_location_dtype.names

        assert actual_fields == tuple(expected_fields), f"Expected fields {expected_fields}, got {actual_fields}"
        assert tile_location_dtype['graphic_type'] == tile_type_dtype, "Expected 'graphic_type' field to match provided tile_type_dtype"
        assert tile_location_dtype['traversable'] == np.dtype(np.bool_), "Expected 'traversable' field to be of type bool"
        assert tile_location_dtype['transparent'] == np.dtype(np.bool_), "Expected 'transparent' field to be of type bool"
        assert tile_location_dtype['visible'] == np.dtype(np.bool_), "Expected 'visible' field to be of type bool"
        assert tile_location_dtype['explored'] == np.dtype(np.bool_), "Expected 'explored' field to be of type bool"
        assert tile_location_dtype['graphic_state'] == graphic_dtype, "Expected 'graphic_state' field to match provided graphic_dtype"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

# Test Cases for GraphicTileMap class
def test_graphic_tile_map_empty_init():
    # Arrange & Act
    tile_map = GraphicTileMap()

    # Assert
    try:
        assert tile_map.dtypes != DEFAULT_MANIFEST['dtypes'], "Expected dtypes to be different instances"
        for key in ['tile_graphics', 'grid_tile_dtype']:
            assert key in tile_map.dtypes, f"Expected {key} to be in tile_map.dtypes"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_parameter_init():
    # Arrange & Act
    tile_map = GraphicTileMap(graphics=DEFAULT_MANIFEST)

    # Assert
    try:
        assert tile_map.dtypes != DEFAULT_MANIFEST['dtypes'], "Expected dtypes to be different instances"
        for key in ['tile_graphics', 'grid_tile_dtype']:
            assert key in tile_map.dtypes, f"Expected {key} to be in tile_map.dtypes"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_properties():
    # Arrange & Act
    tile_map = GraphicTileMap()
    size = tile_map.tiles.shape
    expected_size_tiletuple = TileTuple(([size[0]], [size[1]]))

    # Assert
    try:
        assert isinstance(tile_map._graphics_manifest, dict), "Expected _graphics_manifest to be a dictionary"
        assert len(tile_map._graphics_manifest) > 0, "Expected _graphics_manifest to be initialized"

        assert isinstance(tile_map._graphics_resources, dict), "Expected _graphics_resources to be a dictionary"
        assert len(tile_map._graphics_resources) > 0, "Expected _graphics_resources to be initialized"

        assert tile_map.grid is not None, "Expected grid to be initialized"
        assert isinstance(tile_map.grid, BaseTileGrid), "Expected grid to be a BaseTileGrid instance"

        assert isinstance(tile_map.dimensions, dict), "Expected dimensions to be a dictionary"
        assert len(tile_map.dimensions) > 0, "Expected dimensions to be initialized"
        
        assert isinstance(tile_map.colors, dict), "Expected colors to be a dictionary"
        assert len(tile_map.colors) > 0, "Expected colors to be initialized"
        
        assert isinstance(tile_map.dtypes, dict), "Expected dtypes to be a dictionary"
        assert len(tile_map.dtypes) > 0, "Expected dtypes to be initialized"

        assert isinstance(tile_map.graphics, dict), "Expected graphics to be a dictionary"
        assert len(tile_map.graphics) > 0, "Expected graphics to be initialized"

        assert isinstance(tile_map.tiles, np.ndarray), "Expected tiles to be a numpy array"
        assert tile_map.grid.tiles is not None, "Expected grid tiles to be initialized"
        assert tile_map.tiles is not None, "Expected tiles to be initialized"
        assert expected_size_tiletuple == tile_map.grid.size, "Expected tiles shape to match grid size"
        assert tile_map.tiles.dtype == tile_map.grid.dtype, "Expected tiles dtype to match grid dtype"
        assert tile_map.tiles['visible'].all() == False, "Expected all tiles to be initially not visible"
        assert tile_map.tiles['explored'].all() == False, "Expected all tiles to be initially not explored"

        assert np.array_equal(tile_map.tiles['graphic_type'][:]['name'], np.full((80,50), fill_value='default')), "Expected all tiles to have 'default' graphic_type"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_reset_methods():
    # Arrange
    tile_map = GraphicTileMap()
    tile_map.tiles['traversable'][:, :] = True
    tile_map.tiles['transparent'][:, :] = True
    tile_map.tiles['visible'][:, :] = True
    tile_map.tiles['explored'][:, :] = True

    assert tile_map.tiles['traversable'].all() == 1, "Setup failed: all tiles should be traversable"
    assert tile_map.tiles['transparent'].all() == 1, "Setup failed: all tiles should be transparent"
    assert tile_map.tiles['visible'].all() == 1, "Setup failed: all tiles should be visible"
    assert tile_map.tiles['explored'].all() == 1, "Setup failed: all tiles should be explored"

    # Act
    tile_map.reset_traversable()
    tile_map.reset_transparency()
    tile_map.reset_visibility()
    tile_map.reset_exploration()

    # Assert
    try:
        assert tile_map.tiles['traversable'].all() == False, "Expected all tiles to be not traversable after reset"
        assert tile_map.tiles['transparent'].all() == False, "Expected all tiles to be not transparent after reset"
        assert tile_map.tiles['visible'].all() == False, "Expected all tiles to be not visible after reset"
        assert tile_map.tiles['explored'].all() == False, "Expected all tiles to be not explored after reset"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_update_traversable():
    # Arrange
    tile_map = GraphicTileMap()
    area_mask = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
    state_tuple = StateTuple((True, None, None, None))
    traversable_value = state_tuple[0]

    # Act
    tile_map.update_traversable(area_mask, state_tuple)

    # Assert
    try:
        assert np.array_equal(tile_map.tiles['traversable'][area_mask], np.full(np.sum(area_mask), traversable_value)), "Expected tiles 'traversable' state to match traversable_value"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_update_transparency():
    # Arrange
    tile_map = GraphicTileMap()
    area_mask = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
    state_tuple = StateTuple((None, True, None, None))
    transparency_value = state_tuple[1]

    # Act
    tile_map.update_transparency(area_mask, state_tuple)

    # Assert
    try:
        assert np.array_equal(tile_map.tiles['transparent'][area_mask], np.full(np.sum(area_mask), transparency_value)), "Expected tiles 'transparent' state to match transparency_value"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_update_visibility():
    # Arrange
    tile_map = GraphicTileMap()
    fov = np.random.choice(a=[False, True], size=tile_map.tiles.shape)

    # Act
    tile_map.update_visible(fov)

    # Assert
    try:
        assert np.array_equal(tile_map.tiles['visible'], fov), "Expected tiles 'visible' state to match fov"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_update_explored():
    # Arrange
    tile_map = GraphicTileMap()
    initial_explored = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
    tile_map.tiles['explored'][:, :] = initial_explored
    fov = np.random.choice(a=[False, True], size=tile_map.tiles.shape)

    # Act
    tile_map.update_explored(fov)

    # Assert
    try:
        expected_explored = np.logical_or(initial_explored, fov)
        assert np.array_equal(tile_map.tiles['explored'], expected_explored), "Expected tiles 'explored' state to be updated correctly"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_get_state_array():
    # Arrange
    tile_map = GraphicTileMap()
    state_tuple = StateTuple((False, False, False, False))
    state_label = tile_map.state_tuple_to_label(state_tuple)
    expected_state_array = np.full(tile_map.tiles.shape, state_label)
    
    # Act
    state_array = tile_map.get_state_array()

    # Assert
    try:
        assert np.array_equal(state_array, expected_state_array), f"Expected state array for '{state_tuple}' to match tiles data"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_update_rendered():
    # Arrange
    tile_map = GraphicTileMap()
    area_mask = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
    graphic_state_label = 'g_visible'
    expected_rendered = tile_map.tiles['graphic_type'][area_mask][graphic_state_label]

    # Act
    tile_map.update_rendered_state(area_mask, graphic_state_label)

    # Assert
    try:
        assert np.array_equal(tile_map.tiles['rendered'][area_mask], expected_rendered), "Expected tiles 'rendered' state to match graphic_type for given label"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_set_graphics():
    # Arrange
    tile_map = GraphicTileMap()
    

    # Act
    tile_map.set_graphics(new_graphics)

    # Assert
    try:
        assert np.array_equal(tile_map.tiles['rendered'], new_graphics), "Expected tiles 'rendered' state to match new_graphics"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_custom_init():
    # Arrange
    custom_graphics = MapGraphics({
                    "dimensions": {
                        "grid_size": TileTuple(([20], [20]))
                    },
                    "dtypes": {
                        "grid_tile_dtype": grid_tile_dtype(np.dtype('U1'))
                    },
                    "colors": {
                        "grass": (0, (34, 139, 34), (0, 100, 0)),
                        "water": (1, (0, 191, 255), (25, 25, 112)),
                    },
                    "graphics": {
                        "grass_tile": {
                            "visible": "grass",
                            "walkable": "grass"
                        },
                        "water_tile": {
                            "visible": "water",
                            "walkable": "water"
                        }
                    },
                    "_graphic_fields": ["visible", "walkable"]
                })

    # Act
    tile_map = GraphicTileMap(graphics=custom_graphics)

    # Assert
    try:
        assert tile_map._graphics_manifest == custom_graphics, "Expected graphics to match custom_graphics"
        assert tile_map.dimensions["grid_size"] == (20, 20), "Expected grid_size to be (20, 20)"
        assert tile_map.dtypes["grid_tile_dtype"] == grid_tile_dtype, "Expected grid_tile_dtype to match"
        assert "grass" in tile_map.colors, "Expected 'grass' color to be initialized"
        assert "water" in tile_map.colors, "Expected 'water' color to be initialized"
        assert "grass_tile" in tile_map.graphics, "Expected 'grass_tile' graphic to be initialized"
        assert "water_tile" in tile_map.graphics, "Expected 'water_tile' graphic to be initialized"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass