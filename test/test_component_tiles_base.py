import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.tiles.base import TileCoordinate, TileArea, TileTuple, BaseTileGrid
from core_components.maps.base import new_tile_dtype
from core_components.maps.base import ascii_graphic

PARENT_MAP_SIZE = TileTuple( ([10], [10]) )
TOP_LEFT = TileCoordinate(TileTuple(([1], [2])), PARENT_MAP_SIZE)
BOTTOM_RIGHT = TileCoordinate(TileTuple(([5], [4])), PARENT_MAP_SIZE)
CENTER = TileCoordinate(TileTuple(([3], [3])), PARENT_MAP_SIZE)
WIDTH = 5
HEIGHT = 3

# Test Cases for TileCoordinate
def test_base_empty_coords():
    # Arrange & Act
    empty_coords = TileCoordinate()

    set_coords = TileCoordinate()
    set_coords.x = 3
    set_coords.y = 4
    set_coords.parent_map_size = PARENT_MAP_SIZE

    # Act
    try:
        assert not hasattr(empty_coords, "x"), "Expected no 'x' attribute for TileCoordinate instantiated without parameters"
        assert not hasattr(empty_coords, "y"), "Expected no 'y' attribute for TileCoordinate instantiated without parameters"
        assert not hasattr(empty_coords, "parent_map_size"), "Expected no 'parent_map_size' attribute for TileCoordinate instantiated without parameters"

        assert set_coords.x == 3, "Expected 'x' attribute to be 3 after setting"
        assert set_coords.y == 4, "Expected 'y' attribute to be 4 after setting"
        assert set_coords.parent_map_size == PARENT_MAP_SIZE, "Expected 'parent_map_size' attribute to be (10, 10) after setting"
    
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_empty_coords_to_types():
    # Arrange & Act
    empty_coords = TileCoordinate()

    # Act & Assert
    try:
        with pytest.raises(AttributeError):
            _ = empty_coords.to_tuple
        
        with pytest.raises(AttributeError):
            _ = empty_coords.to_array
        
        with pytest.raises(AttributeError):
            _ = empty_coords.to_list

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_partial_coords_to_types():

    # Arrange, Act & Assert
    try:
        with pytest.raises(AttributeError):
            _ = TileCoordinate().to_tuple
        
        with pytest.raises(AttributeError):
            _ = TileCoordinate(TileTuple(([2], []))).to_array
        
        with pytest.raises(AttributeError):
            _ = TileCoordinate(TileTuple(([], [3]))).to_list

        with pytest.raises(AttributeError):
            _ = TileCoordinate(parent_map_size=PARENT_MAP_SIZE).to_tuple

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_partial_coords_hash():

    # Arrange, Act & Assert
    try:
        with pytest.raises(AttributeError):
            _ = hash(TileCoordinate())
        
        with pytest.raises(AttributeError):
            _ = hash(TileCoordinate(TileTuple(([2], []))))
        
        with pytest.raises(AttributeError):
            _ = hash(TileCoordinate(TileTuple(([], [3]))))

        with pytest.raises(AttributeError):
            _ = hash(TileCoordinate(parent_map_size=PARENT_MAP_SIZE))

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords():
    # Arrange & Act
    coords = TileCoordinate(TileTuple(([3], [4])), PARENT_MAP_SIZE)
    set_coords = TileCoordinate()
    set_coords.x = 3
    set_coords.y = 4
    set_coords.parent_map_size = PARENT_MAP_SIZE
    
    # Act & Assert
    try:
        assert coords.x == 3, "Expected 'x' attribute to be 3 for TileCoordinate instantiated with parameters"
        assert coords.y == 4, "Expected 'y' attribute to be 4 for TileCoordinate instantiated with parameters"
        assert coords.parent_map_size == PARENT_MAP_SIZE, "Expected 'map_size' attribute to be (10, 10) for TileCoordinate instantiated with parameters"

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
    coords = TileCoordinate(TileTuple(([5], [7])), PARENT_MAP_SIZE)

    # Act & Assert
    try:
        tuple_coords = coords.to_tuple
        array_coords = coords.to_array
        list_coords = coords.to_list

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
    location1 = TileTuple(([6], [8]))
    location2 = TileTuple(([1], [2]))
    parent_map_size1 = TileTuple( ([15], [15]) )

    coords1 = TileCoordinate(location1, parent_map_size1)
    coords2 = TileCoordinate(location2, parent_map_size1)
    coords3 = TileCoordinate(location2, parent_map_size1)
    coords4 = TileCoordinate(location1, PARENT_MAP_SIZE) # Different map_size
    
    # Act & Assert
    try:
        assert hash(coords2) == hash(coords3), "Expected hashes of coords2 and coords3 to be equal"
        assert hash(coords1) != hash(coords3), "Expected hashes of coords1 and coords3 to be different"
        assert hash(coords1) != hash(coords4), "Expected hashes of coords1 and coords4 to be different due to different map_size"
    
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_repr():
    # Arrange & Act
    coords = TileCoordinate(TileTuple(([1], [2])), PARENT_MAP_SIZE)
    partial_coords1 = TileCoordinate()
    partial_coords1.x = 1
    partial_coords2 = TileCoordinate()
    partial_coords2.y = 2
    partial_coords3 = TileCoordinate()
    partial_coords3.parent_map_size = PARENT_MAP_SIZE

    # Act & Assert
    try:
        expected_repr = "TileCoordinate(x=1, y=2, parent_map_size=([10], [10]))"
        assert repr(coords) == expected_repr, f"Expected repr to be '{expected_repr}'"
        expected_partial_repr1 = "TileCoordinate(x=1, y=None, parent_map_size=None)"
        assert repr(partial_coords1) == expected_partial_repr1, f"Expected repr to be '{expected_partial_repr1}'"
        expected_partial_repr2 = "TileCoordinate(x=None, y=2, parent_map_size=None)"
        assert repr(partial_coords2) == expected_partial_repr2, f"Expected repr to be '{expected_partial_repr2}'"
        expected_partial_repr3 = "TileCoordinate(x=None, y=None, parent_map_size=([10], [10]))"
        assert repr(partial_coords3) == expected_partial_repr3, f"Expected repr to be '{expected_partial_repr3}'"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_equality():
    # Arrange & Act
    coords1 = TileCoordinate(TileTuple(([2], [3])), PARENT_MAP_SIZE)
    coords2 = TileCoordinate(TileTuple(([2], [3])), PARENT_MAP_SIZE)
    coords3 = TileCoordinate(TileTuple(([4], [5])), PARENT_MAP_SIZE)
    coords4 = TileCoordinate(TileTuple(([2], [3])), TileTuple(([5], [5])))  # Different map_size

    # Act & Assert
    try:
        assert coords1 == coords2, "Expected coords1 to be equal to coords2"
        assert coords1 != coords3, "Expected coords1 to not be equal to coords3"
        assert coords1 != coords4, "Expected coords1 to not be equal to coords4 due to different map_size"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_coords_inbounds():
    # Arrange & Act
    coords_inbounds = TileCoordinate(TileTuple(([3], [4])), PARENT_MAP_SIZE)
    coords_out_of_bounds_x = TileCoordinate(TileTuple(([11], [4])), PARENT_MAP_SIZE)
    coords_out_of_bounds_y = TileCoordinate(TileTuple(([3], [11])), PARENT_MAP_SIZE)
    coords_negative_x = TileCoordinate(TileTuple(([-1], [4])), PARENT_MAP_SIZE)
    coords_negative_y = TileCoordinate(TileTuple(([3], [-1])), PARENT_MAP_SIZE)
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

# Test Cases for TileArea
def test_base_tiles_area_empty_init():
    # Arrange & Act
    area = TileArea()

    # Act & Assert
    try:
        assert not hasattr(area, "top_left"), "Expected no 'top_left' attribute for TileArea instantiated without parameters"
        assert not hasattr(area, "bottom_right"), "Expected no 'bottom_right' attribute for TileArea instantiated without parameters"
 
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_parameter_init():
    # Arrange & Act
    area = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)

    # Act & Assert
    try:
        assert area.top_left == TOP_LEFT, "Expected 'top_left' attribute to be TOP_LEFT after setting: (1,2)"
        assert area.bottom_right == BOTTOM_RIGHT, "Expected 'bottom_right' attribute to be BOTTOM_RIGHT after setting: (4,5)"
        assert area.parent_map_size == PARENT_MAP_SIZE, "Expected 'parent_map_size' attribute to be (10, 10) after setting"
        assert area.width == 5, "Expected 'width' attribute to be 5 after setting corners"
        assert area.height == 3, "Expected 'height' attribute to be 3 after setting corners"
        assert area.center == TileCoordinate(TileTuple(([3], [3])), PARENT_MAP_SIZE), "Expected 'center' attribute to be (3, 3) after setting corners"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_empty_set_center():
    # Arrange & Act

    set_area = TileArea(width=WIDTH, height=HEIGHT)
    set_area.center = CENTER

    # Act & Assert
    try:       
        assert set_area.top_left == TOP_LEFT, "Expected 'top_left' attribute to be TOP_LEFT after setting: (1,2)"
        assert set_area.bottom_right == BOTTOM_RIGHT, "Expected 'bottom_right' attribute to be BOTTOM_RIGHT after setting: (4,5)"
        assert set_area.parent_map_size == PARENT_MAP_SIZE, "Expected 'parent_map_size' attribute to be (10, 10) after setting"
        assert set_area.width == 5, "Expected 'width' attribute to be 5 after setting corners"
        assert set_area.height == 3, "Expected 'height' attribute to be 3 after setting corners"
        assert set_area.center == TileCoordinate(TileTuple(([3], [3])), PARENT_MAP_SIZE), "Expected 'center' attribute to be (3, 3) after setting corners"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_empty_to_types():
    # Arrange & Act
    area = TileArea()

    # Act & Assert
    try:
        with pytest.raises(AttributeError):
            _ = area.to_slices
        
        with pytest.raises(AttributeError):
            _ = area.to_mask

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_to_types():
    # Arrange & Act
    area = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)

    # Act & Assert
    try:
        slices = area.to_slices
        mask = area.to_mask

        expected_slices = (slice(1, 6, None), slice(2, 5, None))
        expected_mask = np.full((10, 10), fill_value=False, dtype=bool)
        expected_mask[1:6, 2:5] = True

        assert slices == expected_slices, f"Expected slices to be {expected_slices}, got {slices}"
        assert np.array_equal(mask, expected_mask), "Expected mask to match the expected boolean array"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_hash():
    # Arrange & Act
    area1 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    area2 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    area3 = TileArea(center=TileCoordinate(TileTuple(([4], [5])), PARENT_MAP_SIZE), width=WIDTH, height=HEIGHT) # Different center
    area4 = TileArea(center=CENTER, width=WIDTH + 1, height=HEIGHT) # Different size
    
    # Act & Assert
    try:
        assert hash(area1) == hash(area2), "Expected hashes of area1 and area2 to be equal"
        assert hash(area1) != hash(area3), "Expected hashes of area1 and area3 to be different"
        assert hash(area1) != hash(area4), "Expected hashes of area1 and area4 to be different due to different map_size"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_repr():
    # Arrange & Act
    area = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)

    # Act & Assert
    try:
        expected_repr = "TileArea(center=TileCoordinate(x=3, y=3, parent_map_size=([10], [10])), width=5, height=3)"
        assert repr(area) == expected_repr, f"Expected repr to be '{expected_repr}'"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_equality():
    # Arrange & Act
    area1 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    area2 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    area3 = TileArea(center=TileCoordinate(TileTuple(([4], [5])), PARENT_MAP_SIZE), width=WIDTH, height=HEIGHT) # Different center
    area4 = TileArea(center=CENTER, width=WIDTH + 1, height=HEIGHT) # Different size
    
    # Act & Assert
    try:
        assert area1 == area2, "Expected area1 to be equal to area2"
        assert area1 != area3, "Expected area1 to not be equal to area3"
        assert area1 != area4, "Expected area1 to not be equal to area4 due to different map_size"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_inbounds():
    # Arrange & Act
    area_inbounds = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    area_out_of_bounds1 = TileArea(center=CENTER, width=WIDTH + 10, height=HEIGHT)
    area_out_of_bounds2 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT + 10)
    area_negative = TileArea(center=TileCoordinate(TileTuple(([-1], [-1])), PARENT_MAP_SIZE), width=WIDTH, height=HEIGHT)

    # Act & Assert
    try:
        assert area_inbounds.is_inbounds, "Expected area_inbounds to be in bounds"
        assert not area_out_of_bounds1.is_inbounds, "Expected area_out_of_bounds1 to be out of bounds"
        assert not area_out_of_bounds2.is_inbounds, "Expected area_out_of_bounds2 to be out of bounds"
        assert not area_negative.is_inbounds, "Expected area_negative to be out of bounds"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_contains():
    # Arrange & Act
    area = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    inside_coord = TileCoordinate(TileTuple(([3], [4])), PARENT_MAP_SIZE)
    outside_coord = TileCoordinate(TileTuple(([7], [8])), PARENT_MAP_SIZE)

    # Act & Assert
    try:
        assert area.contains(inside_coord), "Expected area to contain inside_coord"
        assert not area.contains(outside_coord), "Expected area to not contain outside_coord"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_intersects():
    # Arrange & Act
    area1 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    area2 = TileArea(center=CENTER, width=WIDTH - 1, height=HEIGHT -1) # Overlapping area
    area3 = TileArea(center=TileCoordinate(TileTuple(([8], [8])), PARENT_MAP_SIZE), width=2, height=2) # Non-overlapping area

    # Act & Assert
    try:
        assert area1.intersects(area2), "Expected area1 to intersect with area2"
        assert not area1.intersects(area3), "Expected area1 to not intersect with area3"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_random_location():
    # Arrange & Act
    area = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)

    # Act
    random_location = area.get_random_location()

    # Assert
    try:
        assert area.contains(random_location), "Expected random location to be inside the area"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_size_change():
    # Arrange
    area1 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    expected_top_left1 = TileCoordinate(TileTuple(([0], [2])), PARENT_MAP_SIZE)
    expected_bottom_right1 = TileCoordinate(TileTuple(([6], [4])), PARENT_MAP_SIZE)

    area2 = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    expected_top_left2 = TileCoordinate(TileTuple(([1], [1])), PARENT_MAP_SIZE)
    expected_bottom_right2 = TileCoordinate(TileTuple(([5], [5])), PARENT_MAP_SIZE)

    # Act
    area1.width += 2
    area2.height += 2

    # Assert
    try:
        assert area1.width == WIDTH + 2, "Expected width to be updated after change"
        assert area1.top_left == expected_top_left1, "Expected aligned top_left to updated top_left after width change"
        assert area1.bottom_right == expected_bottom_right1, "Expected aligned bottom_right to updated bottom_right after width change"

        assert area2.height == HEIGHT + 2, "Expected height to be updated after change"
        assert area2.top_left == expected_top_left2, "Expected aligned top_left to updated top_left after height change"
        assert area2.bottom_right == expected_bottom_right2, "Expected aligned bottom_right to updated bottom_right after height change"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_area_center_change():
    # Arrange
    area = TileArea(center=CENTER, width=WIDTH, height=HEIGHT)
    new_center = TileCoordinate(TileTuple(([4], [5])), PARENT_MAP_SIZE)
    expected_top_left = TileCoordinate(TileTuple(([2], [4])), PARENT_MAP_SIZE)
    expected_bottom_right = TileCoordinate(TileTuple(([6], [6])), PARENT_MAP_SIZE)
    
    # Act
    area.center = new_center

    # Act & Assert
    try:
        assert area.height == HEIGHT, "Expected height to remain unchanged after center change"
        assert area.width == WIDTH, "Expected width to remain unchanged after center change"
        assert area.center == new_center, "Expected center to be updated after change"
        assert area.top_left == expected_top_left, "Expected aligned top_left to updated top_left after center change"
        assert area.bottom_right == expected_bottom_right, "Expected aligned bottom_right to updated bottom_right after center change"


    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

# Test Cases for TileGrid
def test_base_tiles_grid_empty():
    # Arrange & Act
    empty_grid = BaseTileGrid(np.dtype([("type_name", "U10")]))

    set_grid = BaseTileGrid(np.dtype([("type_name", "U10")]))
    set_grid.size = TileTuple( ([5], [5]) )

    # Act & Assert
    try:
        assert not hasattr(empty_grid, "size"), "Expected no 'size' attribute for BaseTileGrid instantiated without parameters"
        assert not hasattr(empty_grid, "tiles"), "Expected no 'tiles' attribute for BaseTileGrid instantiated without parameters"

        assert set_grid.size == TileTuple( ([5], [5]) ), "Expected 'size' attribute to be (5, 5) after setting"
        assert set_grid.tiles.shape == (5, 5), "Expected 'tiles' attribute to have shape (5, 5) after setting size and dtype"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_grid_init():
    # Arrange & Act
    grid_size = TileTuple( ([4], [6]) )
    grid_dtype = np.dtype([("visible_field", "U10"), ("_hidden_field", "i4")])
    grid = BaseTileGrid(size=grid_size, dtype=grid_dtype)

    # Act & Assert
    try:
        assert grid.size == grid_size, "Expected 'size' attribute to match provided size"
        assert grid.dtype == grid_dtype, "Expected 'dtype' attribute to match provided dtype"
        assert grid.tiles.shape == (4, 6), "Expected 'tiles' attribute to have shape (4, 6)"
        assert hasattr(grid, "visible_field"), "Expected 'visible_field' attribute to be initialized"
        assert not hasattr(grid, "_hidden_field"), "Expected '_hidden_field' attribute to be private and not directly accessible"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_grid_get_location():
    # Arrange & Act
    grid_size = TileTuple( ([3], [3]) )
    grid_dtype = np.dtype([("type_name", "U10")])
    grid = BaseTileGrid(size=grid_size, dtype=grid_dtype)


    # Act & Assert
    try:
        location = grid.get_location(2, 2)
        assert isinstance(location, TileCoordinate), "Expected get_location to return a TileCoordinate instance"
        assert location.x == 2 and location.y == 2, "Expected TileCoordinate to have correct x and y values"
        assert location.parent_map_size == grid_size, "Expected TileCoordinate to have correct parent_map_size"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tiles_grid_get_area():
    # Arrange & Act
    grid_dtype = np.dtype([("type_name", "U10")])
    grid = BaseTileGrid(size=PARENT_MAP_SIZE, dtype=grid_dtype)
    center = (3, 3)

    # Act & Assert
    try:
        area = grid.get_area(center=center, height=HEIGHT, width=WIDTH)
        assert isinstance(area, TileArea), "Expected get_area to return a TileArea instance"
        assert area.center == CENTER, "Expected get_area returns TileArea with correct center"
        assert area.width == WIDTH, "Expected get_area returns TileArea with correct width"
        assert area.height == HEIGHT, "Expected get_area returns TileArea with correct height"

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
    tile_location_dtype = new_tile_dtype(tile_type_dtype, graphic_dtype)

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