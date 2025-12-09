import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.tiles.base import BaseTileGrid, TileCoordinates
from core_components.tiles.library import TileArea, BaseTileGrid

# Test Cases for TileArea
def test_base_tile_area_empty_init():
    # Arrange & Act
    empty_area = TileArea()

    set_area = TileArea()
    set_area.top_left = TileCoordinates(1, 2, (10, 10))
    set_area.bottom_right = TileCoordinates(5, 6, (10, 10))

    # Act
    try:
        assert not hasattr(empty_area, "top_left"), "Expected no 'top_left' attribute for TileArea instantiated without parameters"
        assert not hasattr(empty_area, "bottom_right"), "Expected no 'bottom_right' attribute for TileArea instantiated without parameters"

        assert set_area.top_left == TileCoordinates(1, 2, (10, 10)), "Expected 'top_left' attribute to be TileCoordinates(1, 2) after setting"
        assert set_area.bottom_right == TileCoordinates(5, 6, (10, 10)), "Expected 'bottom_right' attribute to be TileCoordinates(5, 6) after setting"
        assert set_area.parent_map_size == (10, 10), "Expected 'parent_map_size' attribute to be (10, 10) after setting coordinates"
        assert set_area.tiles.shape == (5, 5), "Expected 'tiles' attribute shape to be (5, 5) after setting coordinates"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_init():
    # Arrange & Act
    top_left = TileCoordinates(2, 3, (10, 10))
    bottom_right = TileCoordinates(6, 7, (10, 10))
    area = TileArea(top_left=top_left, bottom_right=bottom_right)

    # Act & Assert
    try:
        assert area.top_left == top_left, "Expected 'top_left' attribute to match the initialized value"
        assert area.bottom_right == bottom_right, "Expected 'bottom_right' attribute to match the initialized value"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_hash():
    # Arrange & Act
    area1 = TileArea(
        top_left=TileCoordinates(1, 1, (10, 10)),
        bottom_right=TileCoordinates(5, 5, (10, 10))
    )
    area2 = TileArea(
        top_left=TileCoordinates(1, 1, (10, 10)),
        bottom_right=TileCoordinates(5, 5, (10, 10))
    )
    area3 = TileArea(
        top_left=TileCoordinates(2, 2, (10, 10)),
        bottom_right=TileCoordinates(6, 6, (10, 10))
    )

    # Act & Assert
    try:
        assert hash(area1) == hash(area2), "Expected hashes of area1 and area2 to be equal"
        assert hash(area1) != hash(area3), "Expected hashes of area1 and area3 to be different"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_repr():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(1, 2, (10, 10)),
        bottom_right=TileCoordinates(5, 6, (10, 10))
    )

    # Act & Assert
    try:
        expected_repr = "TileArea(top_left=TileCoordinates(x=1, y=2, parent_map_size=(10, 10)), bottom_right=TileCoordinates(x=5, y=6, parent_map_size=(10, 10)))"
        assert repr(area) == expected_repr, f"Expected repr to be '{expected_repr}'"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_equality():
    # Arrange & Act
    area1 = TileArea(
        top_left=TileCoordinates(1, 1, (10, 10)),
        bottom_right=TileCoordinates(5, 5, (10, 10))
    )
    area2 = TileArea(
        top_left=TileCoordinates(1, 1, (10, 10)),
        bottom_right=TileCoordinates(5, 5, (10, 10))
    )
    area3 = TileArea(
        top_left=TileCoordinates(2, 2, (10, 10)),
        bottom_right=TileCoordinates(6, 6, (10, 10))
    )

    # Act & Assert
    try:
        assert area1 == area2, "Expected area1 to be equal to area2"
        assert area1 != area3, "Expected area1 to not be equal to area3"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_parent_map_size():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(1, 1, (10, 10)),
        bottom_right=TileCoordinates(5, 5, (10, 10))
    )

    # Act & Assert
    try:
        assert area.parent_map_size == (10, 10), "Expected 'parent_map_size' attribute to be (10, 10)"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_dimensions():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(7, 9, (10, 10))
    )

    # Act & Assert
    try:
        assert area.width == 6, "Expected width to be 6"
        assert area.height == 7, "Expected height to be 7"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_is_inbounds():
    # Arrange & Act
    area_inbounds = TileArea(
        top_left=TileCoordinates(1, 1, (10, 10)),
        bottom_right=TileCoordinates(5, 5, (10, 10))
    )
    area_out_of_bounds = TileArea(
        top_left=TileCoordinates(8, 8, (10, 10)),
        bottom_right=TileCoordinates(12, 12, (10, 10))
    )

    # Act & Assert
    try:
        assert area_inbounds.is_inbounds, "Expected area_inbounds to be in bounds"
        assert not area_out_of_bounds.is_inbounds, "Expected area_out_of_bounds to be out of bounds"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_to_slices():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(6, 8, (10, 10))
    )
    map_array = np.zeros((10, 10))

    # Act
    slices = area.to_slices()

    # Act & Assert
    try:
        expected_slices = (slice(2, 7), slice(3, 9))
        assert slices == expected_slices, f"Expected slices to be {expected_slices}"
        sub_array = map_array[slices]
        assert sub_array.shape == (5, 6), "Expected sub-array shape to be (5, 6)"
        
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_base_tile_area_is_traversable_at():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(6, 8, (10, 10))
    )

    # Act
    area.tiles['traversable'][2:4, 2:4] = True

    # Assert
    try:
        for x in range(5):
            for y in range(6):
                location = area.get_coordinate(x, y)
                if 2 <= x < 4 and 2 <= y < 4:
                    expected_traversable = True
                else:
                    expected_traversable = False

                actual_traversable = area.is_traversable_at(location)
                assert actual_traversable == expected_traversable, f"Expected traversability at ({x}, {y}) to be '{expected_traversable}', but got '{actual_traversable}'"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass

def test_base_tile_area_is_transparent_at():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(6, 8, (10, 10))
    )

    # Act
    area.tiles['transparent'][1:5, 1:5] = True

    # Assert
    try:
        for x in range(5):
            for y in range(6):
                location = area.get_coordinate(x, y)
                if 1 <= x < 5 and 1 <= y < 5:
                    expected_transparent = True
                else:
                    expected_transparent = False

                actual_transparent = area.is_transparent_at(location)
                assert actual_transparent == expected_transparent, f"Expected transparency at ({x}, {y}) to be '{expected_transparent}', but got '{actual_transparent}'"
    except AssertionError as e:
        pytest.fail(str(e))
    # Atavise
    finally:
        pass

def test_base_tile_area_is_visible_at():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(6, 8, (10, 10))
    )

    # Act
    area.tiles['visible'][0:3, 0:3] = True

    # Assert
    try:
        for x in range(5):
            for y in range(6):
                location = area.get_coordinate(x, y)
                if 0 <= x < 3 and 0 <= y < 3:
                    expected_visible = True
                else:
                    expected_visible = False

                actual_visible = area.is_visible_at(location)
                assert actual_visible == expected_visible, f"Expected visibility at ({x}, {y}) to be '{expected_visible}', but got '{actual_visible}'"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass

def test_base_tile_area_is_explored_at():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(6, 8, (10, 10))
    )

    # Act
    area.tiles['explored'][1:4, 1:4] = True

    # Assert
    try:
        for x in range(5):
            for y in range(6):
                location = area.get_coordinate(x, y)
                if 1 <= x < 4 and 1 <= y < 4:
                    expected_explored = True
                else:
                    expected_explored = False

                actual_explored = area.is_explored_at(location)
                assert actual_explored == expected_explored, f"Expected explored status at ({x}, {y}) to be '{expected_explored}', but got '{actual_explored}'"
    
    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass

def test_base_tile_area_get_type_at():
    # Arrange 
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(6, 8, (10, 10))
    )
    area.tiles['type']['name'][:, :] = "default"

    # Act
    location = area.get_coordinate(4, 4)
    actual_tile_type = area.get_type_at(location)['name']

    # Assert
    try:
        expected_tile_type = "default"
        assert actual_tile_type == expected_tile_type, f"Expected tile type at (4,4) to be '{expected_tile_type}', but got '{actual_tile_type}'"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass

def test_base_tile_area_properties():
    # Arrange & Act
    area = TileArea(
        top_left=TileCoordinates(2, 3, (10, 10)),
        bottom_right=TileCoordinates(6, 8, (10, 10))
    )
    width = 5
    height = 6

    # Assert
    try:        
        assert area.size == (width, height), "'size' property shape does not match expected"
        assert area.traversable.shape == (width, height), "'traversable' property shape does not match expected"
        assert area.transparent.shape == (width, height), "'transparent' property shape does not match expected"
        assert area.types.shape == (width, height), "'types' property shape does not match expected"
        assert area.visible.shape == (width, height), "'visible' property shape does not match expected"
        assert area.explored.shape == (width, height), "'explored' property shape does not match expected"
        assert area.graphics.shape == (width, height), "'graphics' property shape does not match expected"

    except AssertionError as e:
        pytest.fail(str(e))

    # Atavise
    finally:
        pass    
