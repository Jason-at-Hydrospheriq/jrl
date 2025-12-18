from copy import deepcopy
import itertools
import pytest
from sys import path

from core_components.graphics.tile_types import ascii_graphic
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.maps.library import DefaultTileMap, DEFAULT_MANIFEST
from core_components.tiles.base import BaseTileGrid, TileCoordinate, TileTuple


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

# Test Cases for DefaultTileMap class
def test_default_tile_map_init():
    # Arrange & Act
    tile_map = DefaultTileMap()

    # Assert
    try:
        assert hasattr(tile_map, 'grid'), "Expected tile_map to have a 'grid' attribute after initialization" 
        assert isinstance(tile_map.grid, BaseTileGrid), "Expected grid to be a BaseTileGrid instance"
        assert isinstance(tile_map._graphics_resources, dict), "Expected _graphic_resources to be a dictionary"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_default_tile_map_statespace():
    # Arrange & Act
    tile_map = DefaultTileMap()
    actual_state_vector = None
    expected_state_vector = np.array([False, False, False, False], dtype=tile_map.dtypes['tile_state_vector'])
    expected_dtype_metadata = 'tile_state_vector'
    expected_label_map = np.array(( 'shroud', 'explored', 'first_look', 'visible',
                                    'shroud', 'explored', 'first_look', 'visible',
                                    'shroud', 'explored', 'first_look', 'visible',
                                    'shroud', 'explored', 'first_look', 'visible'))
    
    if tile_map.statespace is not None:
        actual_state_vector = tile_map.get_statespace_vector(0)
        actual_dtype_metadata = actual_state_vector.dtype.metadata['__name__'] # type: ignore
        actual_label_map = tile_map.statespace_label_map

        # Assert
        try:
            assert isinstance(tile_map.statespace, dict), "Expected statespace to be a dictionary"
            assert len(tile_map.statespace) > 0, "Expected statespace to be initialized"
            assert actual_dtype_metadata == expected_dtype_metadata, "Expected statespace dtype to be 'tile_state_vector'"
            assert np.array_equal(actual_state_vector, expected_state_vector), "Expected state_vector to match expected_state_vector" #type: ignore
            assert np.array_equal(actual_label_map, expected_label_map), f"Expected state_space_label_map to be {expected_label_map}" #type: ignore

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_colors():
    # Arrange & Act
    tile_map = DefaultTileMap()
    color = None
    actual_bg = None
    actual_fg = None
    actual_ord_negated = None
    expected_fg = np.array([255, 255, 255], dtype=np.uint8)
    expected_bg = np.array([0, 0, 0], dtype=np.uint8)
    expected_ord_negated = ord("A")

    if tile_map.colors['fill_black'] is not None:
        color = tile_map.colors['fill_black']
        actual_fg = color['fg']
        actual_bg = color['bg']
        actual_ord_negated = color['ch']

        # Assert
        try:
            assert isinstance(tile_map.colors, dict), "Expected colors to be a dictionary"
            assert len(tile_map.colors) > 0, "Expected colors to be initialized"
            assert actual_ord_negated != expected_ord_negated, "Expected 'ch' field not to be ord('A')"
            assert np.array_equal(actual_fg, expected_fg), "Expected 'fg' field to be (255, 255, 255)"
            assert np.array_equal(actual_bg, expected_bg), "Expected 'bg' field to be (0, 0, 0)"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_dtypes():
    # Arrange & Act
    tile_map = DefaultTileMap()
    dtypes = tile_map.dtypes
    expected_dtype_names = ('tile_state_vector', 'tile_color', 'tile_graphic', 'tile_grid')
    expected_metadata_names = ('tile_state_vector', 'ascii_graphic', 'tile_graphic', 'tile_grid')

    if dtypes is not None:
        actual_dtype_names = tuple(dtypes.keys())
        actual_metadata_names = tuple([dtypes[key].metadata['__name__'] for key in actual_dtype_names if dtypes[key] is not None and hasattr(dtypes[key], 'metadata')]) # type: ignore

        # Assert
        try:
            assert isinstance(dtypes, dict), "Expected dtypes to be a dictionary"
            assert len(dtypes) > 0, "Expected dtypes to be initialized"
            assert actual_dtype_names == expected_dtype_names, f"Expected dtype names to be {expected_dtype_names}"
            assert actual_metadata_names == expected_metadata_names, f"Expected metadata names to be {expected_metadata_names}"
            
        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_graphics():
    # Arrange & Act
    tile_map = DefaultTileMap()
    graphic = None

    if tile_map.graphics is not None:
        graphic = tile_map.graphics['default']
        expected_dtype_metadata = 'tile_graphic'
        actual_dtype_metadata = graphic.dtype.metadata['__name__'] # type: ignore
        expected_graphics = ['default', 'floor', 'wall']
        actual_graphics = list(tile_map.graphics.keys())

        # Assert
        try:
            assert isinstance(tile_map.graphics, dict), "Expected graphics to be a dictionary"
            assert len(tile_map.graphics) > 0, "Expected graphics to be initialized"
            assert actual_dtype_metadata == expected_dtype_metadata, "Expected graphics dtype to be 'tile_graphic'"
            assert all([g in actual_graphics for g in expected_graphics]), f"Expected graphics keys to be {expected_graphics}"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_state_properties():
    # Arrange & Act
    tile_map = DefaultTileMap()

    if tile_map.statespace is not None:
        n_state_bits = len(tile_map.statespace['bits'])
        acutual_ss_array = tile_map.statespace_array
        actual_ss_tensor = tile_map.statespace_tensor
        actual_st_tensor = tile_map.state_tensor
        actual_st_tensor_aligned = tile_map.state_tensor_aligned

        expected_ss_array = np.array(tuple([i for i in itertools.product([0,1], repeat=n_state_bits)]))
        tensor_1 = np.concatenate([expected_ss_array] * tile_map.tiles.shape[0]).reshape(tile_map.tiles.shape[0], 2 ** n_state_bits, n_state_bits) # +1D Grid
        expected_ss_tensor = np.stack([tensor_1] * tile_map.tiles.shape[1], axis = 1) # +1D Grid

        expected_st_tensor = np.full((*tile_map.tiles.shape, 1, n_state_bits), fill_value=0)
        expected_st_tensor_aligned =  np.full((*tile_map.tiles.shape, n_state_bits ** 2, n_state_bits), fill_value=0)

        # Assert
        try:
            assert isinstance(acutual_ss_array, np.ndarray), "Expected statespace_array to be a numpy array"
            assert isinstance(actual_ss_tensor, np.ndarray), "Expected statespace_tensor to be a numpy array"
            assert isinstance(actual_st_tensor, np.ndarray), "Expected state_tensor to be a numpy array"
            assert isinstance(actual_st_tensor_aligned, np.ndarray), "Expected state_tensor_aligned to be a numpy array"
            assert np.array_equal(acutual_ss_array, expected_ss_array), "Expected statespace_array to match expected_ss_array"
            assert np.array_equal(actual_ss_tensor, expected_ss_tensor), "Expected statespace_tensor to  match expected_ss_tensor"   # type: ignore
            assert np.array_equal(actual_st_tensor, expected_st_tensor), "Expected state_tensor to match expected_st_tensor"   # type: ignore
            assert np.array_equal(actual_st_tensor_aligned, expected_st_tensor_aligned), "Expected state_tensor_aligned to match expected_st_tensor_aligned"   # type: ignore

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_state_bit_management():
    # Arrange
    tile_map = DefaultTileMap()

    expected_bits = np.full([*tile_map.tiles.shape], fill_value=False)
    expected_set_bits = np.full([*tile_map.tiles.shape], fill_value=True)

    # Act
    actual_initial_bits = tile_map.get_state_bits('visible')
    tile_map.set_state_bits('visible', expected_set_bits)
    actual_set_bits = tile_map.get_state_bits('visible')
    tile_map.reset_state_bits('visible')
    actual_reset_bits = tile_map.get_state_bits('visible')

    # Assert
    try:
        assert np.array_equal(actual_initial_bits, expected_bits), "Expected initial state bits to be False"
        assert np.array_equal(actual_set_bits, expected_set_bits), "Expected set state bits to be True"
        assert np.array_equal(actual_reset_bits, expected_bits), "Expected reset state bits to be False"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_default_tile_map_get_tiles():
    # Arrange
    tile_map = DefaultTileMap()

    if tile_map.graphics and tile_map.graphics['default'] is not None:
        expected_tiles = np.full([*tile_map.tiles.shape], fill_value=tile_map.graphics['default'])

        # Act
        actual_tiles = tile_map.get_tiles()

        # Assert
        try:
            assert actual_tiles is not None, "Expected get_tiles to return a non-None value"
            assert np.array_equal(actual_tiles, expected_tiles), "Expected get_tiles to match expected_tiles"
            
        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_get_tile_layout():
    # Arrange
    tile_map = DefaultTileMap()
    if tile_map.graphics and tile_map.graphics['default'] is not None:
        expected_layout = np.full([*tile_map.tiles.shape], fill_value=True)

        # Act
        actual_layout = tile_map.get_tile_layout('default')

        # Assert
        try:
            assert actual_layout is not None, "Expected get_tile_layout to return a non-None value"
            assert np.array_equal(actual_layout, expected_layout), "Expected get_tile_layout to match expected_layout"
            
        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_set_tile_noargs():
    # Arrange
    tile_map = DefaultTileMap()
    if tile_map.graphics and tile_map.graphics['default'] is not None:
        expected_tile_names = np.array(['default'] * tile_map.tiles.size)
        expected_blocks_movement = np.array([True] * tile_map.tiles.size)
        expected_blocks_vision = np.array([True] * tile_map.tiles.size)

        # Act
        tile_map.set_tiles()
        actual_tile_names = tile_map.tiles['graphic_type'].flatten()['name']
        actual_blocks_movement = tile_map.tiles['blocks_movement'].flatten()
        actual_blocks_vision = tile_map.tiles['blocks_vision'].flatten()

        # Assert
        try:
            assert actual_tile_names is not None, "Expected set_tiles to return a non-None value"
            assert np.array_equal(actual_tile_names, expected_tile_names), "Expected set_tiles to update the tiles correctly"
            assert np.array_equal(actual_blocks_movement, expected_blocks_movement), "Expected set_tiles to update blocks_movement correctly"
            assert np.array_equal(actual_blocks_vision, expected_blocks_vision), "Expected set_tiles to update blocks_vision correctly"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_set_tiles_args():
    # Arrange
    tile_map = DefaultTileMap()
    if tile_map.graphics and tile_map.graphics['default'] is not None:
        layout = np.full([*tile_map.tiles.shape], fill_value=False)
        layout[10:15, 10:15] = True
        expected_tile_names = np.array(['floor'] * 25)
        expected_blocks_movement = np.array([False] * 25)
        expected_blocks_vision = np.array([False] * 25)

        # Act
        tile_map.set_tiles(layout, 'floor')
        actual_tile_names = tile_map.tiles['graphic_type'][10:15, 10:15].flatten()['name']
        actual_blocks_movement = tile_map.tiles['blocks_movement'][10:15, 10:15].flatten()
        actual_blocks_vision = tile_map.tiles['blocks_vision'][10:15, 10:15].flatten()

        # Assert
        try:
            assert actual_tile_names is not None, "Expected set_tiles to return a non-None value"
            assert np.array_equal(actual_tile_names, expected_tile_names), "Expected set_tiles to update the tiles correctly"
            assert np.array_equal(actual_blocks_movement, expected_blocks_movement), "Expected set_tiles to update blocks_movement correctly"
            assert np.array_equal(actual_blocks_vision, expected_blocks_vision), "Expected set_tiles to update blocks_vision correctly"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_merge_tile_merge():
    # Arrange
    tile_map = DefaultTileMap()
    tile_map.tiles['graphic_type'][2:4, 2:4] = tile_map.graphics['floor']

    if tile_map.graphics and tile_map.graphics['default'] is not None:
        layout1 = np.full([*tile_map.tiles.shape], fill_value=False)
        layout1[2:4, 2:4] = True

        layout2 = np.full([*tile_map.tiles.shape], fill_value=False)
        layout2[2:4, 3:5] = True

        expected_layout = np.full([*tile_map.tiles.shape], fill_value=False)
        expected_layout[2:4, 2:5] = True
        
        # Act
        actual_layout1 = tile_map.merge_tile_layout(layout2, graphic_name='floor', join_type='merge')


        # Assert
        try:
            assert actual_layout1 is not None, "Expected merge_tile_layout to return a non-None value"
            assert np.array_equal(actual_layout1, expected_layout), "Expected merge_tile_layout to update the layout correctly"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_merge_tile_inner():
    # Arrange
    tile_map = DefaultTileMap()
    tile_map.tiles['graphic_type'][2:4, 2:4] = tile_map.graphics['floor']

    if tile_map.graphics and tile_map.graphics['default'] is not None:
        layout1 = np.full([*tile_map.tiles.shape], fill_value=False)
        layout1[2:4, 2:4] = True

        layout2 = np.full([*tile_map.tiles.shape], fill_value=False)
        layout2[2:4, 3:5] = True

        expected_layout = np.full([*tile_map.tiles.shape], fill_value=False)
        expected_layout[2:4, 3:4] = True
        
        # Act
        actual_layout1 = tile_map.merge_tile_layout(layout2, graphic_name='floor', join_type='inner')


        # Assert
        try:
            assert actual_layout1 is not None, "Expected merge_tile_layout to return a non-None value"
            assert np.array_equal(actual_layout1, expected_layout), "Expected merge_tile_layout to update the layout correctly"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_merge_tile_outer():
    # Arrange
    tile_map = DefaultTileMap()
    tile_map.tiles['graphic_type'][2:4, 2:4] = tile_map.graphics['floor']

    if tile_map.graphics and tile_map.graphics['default'] is not None:
        layout1 = np.full([*tile_map.tiles.shape], fill_value=False)
        layout1[2:4, 2:4] = True

        layout2 = np.full([*tile_map.tiles.shape], fill_value=False)
        layout2[2:4, 3:5] = True

        expected_layout = np.full([*tile_map.tiles.shape], fill_value=False)
        expected_layout[2:4, 2:3] = True
        expected_layout[2:4, 4:5] = True
        
        # Act
        actual_layout1 = tile_map.merge_tile_layout(layout2, graphic_name='floor', join_type='outer')


        # Assert
        try:
            assert actual_layout1 is not None, "Expected merge_tile_layout to return a non-None value"
            assert np.array_equal(actual_layout1, expected_layout), "Expected merge_tile_layout to update the layout correctly"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_default_tile_map_reset_tiles():
    # Arrange
    tile_map = DefaultTileMap()

    if tile_map.graphics and tile_map.graphics['default'] is not None:
        layout = np.full([*tile_map.tiles.shape], fill_value=True)
        expected_tiles = tile_map.get_tiles()

        # Act
        tile_map.set_tiles(layout, 'floor')
        tile_map.reset_tiles()
        actual_tiles = tile_map.get_tiles()

        # Assert
        try:
            assert actual_tiles is not None, "Expected reset_tiles to return a non-None value"
            assert expected_tiles is not None, "Expected expected_tiles to be a non-None value"
            assert np.array_equal(expected_tiles, actual_tiles), "Expected reset_tiles to update the tiles correctly"

        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_graphic_tile_map_object_collision():
    # Arrange
    tile_map = DefaultTileMap()
    collision_layout = np.full([*tile_map.tiles.shape], fill_value=False)
    collision_layout[10:15, 10:15] = True
    tile_map.set_state_bits('blocks_movement', collision_layout)
    destination = TileCoordinate(TileTuple(([12], [12])), TileTuple(([80], [50])))

    # Act
    

    # Assert
    try:
        assert tile_map.object_collision(destination), "Expected get_object_collision to return a non-None value"
     
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_graphic_tile_map_get_tile_layout():
    # Arrange
    tile_map = DefaultTileMap()

    mask = np.full([*tile_map.tiles.shape], fill_value=True)
    mask[20:30, 20:30] = False
    tile_map.tiles['graphic_type'][mask] = tile_map.graphics['floor']

    if tile_map.graphics and tile_map.graphics['default'] is not None:
        expected_layout_no_graphic_name = np.full([*tile_map.tiles.shape], fill_value=True)
        expected_layout_graphic_name = ~mask

        # Act
        actual_layout_no_graphic_name = np.full([*tile_map.tiles.shape], fill_value=True)
        actual_layout_graphic_name = tile_map.get_tile_layout('default')

        # Assert
        try:
            assert actual_layout_graphic_name is not None, "Expected get_tile_layout to return a non-None value"
            assert np.array_equal(actual_layout_no_graphic_name, expected_layout_no_graphic_name), "Expected get_tile_layout to match expected_layout"
            assert np.array_equal(actual_layout_graphic_name, expected_layout_graphic_name), "Expected get_tile_layout to match expected_layout"

        except AssertionError as e:
            pytest.fail(str(e))

# def test_graphic_tile_map_parameter_init():
#     # Arrange & Act
#     tile_map = GraphicTileMap(graphics=DEFAULT_MANIFEST)

#     # Assert
#     try:
#         assert tile_map.dtypes != DEFAULT_MANIFEST['dtypes'], "Expected dtypes to be different instances"
#         for key in ['tile_graphics', 'grid_tile_dtype']:
#             assert key in tile_map.dtypes, f"Expected {key} to be in tile_map.dtypes"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_properties():
#     # Arrange & Act
#     tile_map = GraphicTileMap()
#     size = tile_map.tiles.shape
#     expected_size_tiletuple = TileTuple(([size[0]], [size[1]]))

#     # Assert
#     try:
#         assert isinstance(tile_map._graphics_manifest, dict), "Expected _graphics_manifest to be a dictionary"
#         assert len(tile_map._graphics_manifest) > 0, "Expected _graphics_manifest to be initialized"

#         assert isinstance(tile_map._graphics_resources, dict), "Expected _graphics_resources to be a dictionary"
#         assert len(tile_map._graphics_resources) > 0, "Expected _graphics_resources to be initialized"

#         assert tile_map.grid is not None, "Expected grid to be initialized"
#         assert isinstance(tile_map.grid, BaseTileGrid), "Expected grid to be a BaseTileGrid instance"

#         assert isinstance(tile_map.dimensions, dict), "Expected dimensions to be a dictionary"
#         assert len(tile_map.dimensions) > 0, "Expected dimensions to be initialized"
        
#         assert isinstance(tile_map.colors, dict), "Expected colors to be a dictionary"
#         assert len(tile_map.colors) > 0, "Expected colors to be initialized"
        
#         assert isinstance(tile_map.dtypes, dict), "Expected dtypes to be a dictionary"
#         assert len(tile_map.dtypes) > 0, "Expected dtypes to be initialized"

#         assert isinstance(tile_map.graphics, dict), "Expected graphics to be a dictionary"
#         assert len(tile_map.graphics) > 0, "Expected graphics to be initialized"

#         assert isinstance(tile_map.tiles, np.ndarray), "Expected tiles to be a numpy array"
#         assert tile_map.grid.tiles is not None, "Expected grid tiles to be initialized"
#         assert tile_map.tiles is not None, "Expected tiles to be initialized"
#         assert expected_size_tiletuple == tile_map.grid.size, "Expected tiles shape to match grid size"
#         assert tile_map.tiles.dtype == tile_map.grid.dtype, "Expected tiles dtype to match grid dtype"
#         assert tile_map.tiles['visible'].all() == False, "Expected all tiles to be initially not visible"
#         assert tile_map.tiles['explored'].all() == False, "Expected all tiles to be initially not explored"

#         assert np.array_equal(tile_map.tiles['graphic_type'][:]['name'], np.full((80,50), fill_value='default')), "Expected all tiles to have 'default' graphic_type"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_reset_methods():
#     # Arrange
#     tile_map = GraphicTileMap()
#     tile_map.tiles['traversable'][:, :] = True
#     tile_map.tiles['transparent'][:, :] = True
#     tile_map.tiles['visible'][:, :] = True
#     tile_map.tiles['explored'][:, :] = True

#     assert tile_map.tiles['traversable'].all() == 1, "Setup failed: all tiles should be traversable"
#     assert tile_map.tiles['transparent'].all() == 1, "Setup failed: all tiles should be transparent"
#     assert tile_map.tiles['visible'].all() == 1, "Setup failed: all tiles should be visible"
#     assert tile_map.tiles['explored'].all() == 1, "Setup failed: all tiles should be explored"

#     # Act
#     tile_map.reset_traversable()
#     tile_map.reset_transparency()
#     tile_map.reset_visibility()
#     tile_map.reset_exploration()

#     # Assert
#     try:
#         assert tile_map.tiles['traversable'].all() == False, "Expected all tiles to be not traversable after reset"
#         assert tile_map.tiles['transparent'].all() == False, "Expected all tiles to be not transparent after reset"
#         assert tile_map.tiles['visible'].all() == False, "Expected all tiles to be not visible after reset"
#         assert tile_map.tiles['explored'].all() == False, "Expected all tiles to be not explored after reset"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_update_traversable():
#     # Arrange
#     tile_map = GraphicTileMap()
#     area_mask = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
#     state_tuple = StateTuple((True, None, None, None))
#     traversable_value = state_tuple[0]

#     # Act
#     tile_map.update_traversable(area_mask, state_tuple)

#     # Assert
#     try:
#         assert np.array_equal(tile_map.tiles['traversable'][area_mask], np.full(np.sum(area_mask), traversable_value)), "Expected tiles 'traversable' state to match traversable_value"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_update_transparency():
#     # Arrange
#     tile_map = GraphicTileMap()
#     area_mask = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
#     state_tuple = StateTuple((None, True, None, None))
#     transparency_value = state_tuple[1]

#     # Act
#     tile_map.update_transparency(area_mask, state_tuple)

#     # Assert
#     try:
#         assert np.array_equal(tile_map.tiles['transparent'][area_mask], np.full(np.sum(area_mask), transparency_value)), "Expected tiles 'transparent' state to match transparency_value"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_update_visibility():
#     # Arrange
#     tile_map = GraphicTileMap()
#     fov = np.random.choice(a=[False, True], size=tile_map.tiles.shape)

#     # Act
#     tile_map.update_visible(fov)

#     # Assert
#     try:
#         assert np.array_equal(tile_map.tiles['visible'], fov), "Expected tiles 'visible' state to match fov"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_update_explored():
#     # Arrange
#     tile_map = GraphicTileMap()
#     initial_explored = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
#     tile_map.tiles['explored'][:, :] = initial_explored
#     fov = np.random.choice(a=[False, True], size=tile_map.tiles.shape)

#     # Act
#     tile_map.update_explored(fov)

#     # Assert
#     try:
#         expected_explored = np.logical_or(initial_explored, fov)
#         assert np.array_equal(tile_map.tiles['explored'], expected_explored), "Expected tiles 'explored' state to be updated correctly"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_get_state_array():
#     # Arrange
#     tile_map = GraphicTileMap()
#     state_tuple = StateTuple((False, False, False, False))
#     state_label = tile_map.state_tuple_to_label(state_tuple)
#     expected_state_array = np.full(tile_map.tiles.shape, state_label)
    
#     # Act
#     state_array = tile_map.get_state_array()

#     # Assert
#     try:
#         assert np.array_equal(state_array, expected_state_array), f"Expected state array for '{state_tuple}' to match tiles data"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_update_rendered():
#     # Arrange
#     tile_map = GraphicTileMap()
#     area_mask = np.random.choice(a=[False, True], size=tile_map.tiles.shape)
#     graphic_state_label = 'g_visible'
#     expected_rendered = tile_map.tiles['graphic_type'][area_mask][graphic_state_label]

#     # Act
#     tile_map.update_rendered_state(area_mask, graphic_state_label)

#     # Assert
#     try:
#         assert np.array_equal(tile_map.tiles['rendered'][area_mask], expected_rendered), "Expected tiles 'rendered' state to match graphic_type for given label"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_set_graphics():
#     # Arrange
#     tile_map = GraphicTileMap()
    

#     # Act
#     tile_map.set_graphics(new_graphics)

#     # Assert
#     try:
#         assert np.array_equal(tile_map.tiles['rendered'], new_graphics), "Expected tiles 'rendered' state to match new_graphics"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_graphic_tile_map_custom_init():
    # Arrange
    # custom_graphics = MapGraphics({
    #                 "dimensions": {
    #                     "grid_size": TileTuple(([20], [20]))
    #                 },
    #                 "dtypes": {
    #                     "grid_tile_dtype": grid_tile_dtype(np.dtype('U1'))
    #                 },
    #                 "colors": {
    #                     "grass": (0, (34, 139, 34), (0, 100, 0)),
    #                     "water": (1, (0, 191, 255), (25, 25, 112)),
    #                 },
    #                 "graphics": {
    #                     "grass_tile": {
    #                         "visible": "grass",
    #                         "walkable": "grass"
    #                     },
    #                     "water_tile": {
    #                         "visible": "water",
    #                         "walkable": "water"
    #                     }
    #                 },
    #                 "_graphic_fields": ["visible", "walkable"]
    #             })

    # # Act
    # tile_map = GraphicTileMap(graphics=custom_graphics)

    # # Assert
    # try:
    #     assert tile_map._graphics_manifest == custom_graphics, "Expected graphics to match custom_graphics"
    #     assert tile_map.dimensions["grid_size"] == (20, 20), "Expected grid_size to be (20, 20)"
    #     assert tile_map.dtypes["grid_tile_dtype"] == grid_tile_dtype, "Expected grid_tile_dtype to match"
    #     assert "grass" in tile_map.colors, "Expected 'grass' color to be initialized"
    #     assert "water" in tile_map.colors, "Expected 'water' color to be initialized"
    #     assert "grass_tile" in tile_map.graphics, "Expected 'grass_tile' graphic to be initialized"
    #     assert "water_tile" in tile_map.graphics, "Expected 'water_tile' graphic to be initialized"

    # except AssertionError as e:
    #     pytest.fail(str(e))
    
    # # Atavise
    # finally:
    #     pass