import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.maps.rooms import RectangularRoom, CircularRoom
from core_components.maps.base import MapCoords

def test_rectangular_room_empty_init():
    # Arrange & Act
    room = RectangularRoom()

    # Assert
    try:
        assert room.center == MapCoords(0, 0), "Expected center to be at (0,0)"
        assert room.width == 4, "Expected width to be 4"
        assert room.height == 4, "Expected height to be 4"
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_parameter_init():
    # Arrange & Act
    room = RectangularRoom(center=MapCoords(5, 5), size=(8, 6))

    # Assert
    try:
        assert room.center == MapCoords(5, 5), "Expected center to be at (5,5)"
        assert room.width == 8, "Expected width to be 8"
        assert room.height == 6, "Expected height to be 6"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_inner_area():
    # Arrange & Act
    room = RectangularRoom(center=MapCoords(0, 0), size=(5, 6))
    inner_area = room.inner_area

    # Assert
    try:
        expected_area = np.full((5, 6), False, dtype=bool)
        expected_area[1:-1, 1:-1] = True
        assert np.array_equal(inner_area, expected_area), "Inner area does not match expected area"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_area_coordinates():
    # Arrange & Act
    room = RectangularRoom(center=MapCoords(5, 5), size=(7, 9))
    area_coords = room.area_coordinates()

    # Assert
    try:
        expected_coords = np.array([[3, 2], [3, 3], [3, 4], [3, 5], [3, 6], [3, 7], [3, 8],
                                    [4, 2], [4, 3], [4, 4], [4, 5], [4, 6], [4, 7], [4, 8],
                                    [5, 2], [5, 3], [5, 4], [5, 5], [5, 6], [5, 7], [5, 8],
                                    [6, 2], [6, 3], [6, 4], [6, 5], [6, 6], [6, 7], [6, 8],
                                    [7, 2], [7, 3], [7, 4], [7, 5], [7, 6], [7, 7], [7, 8]])
        assert np.array_equal(area_coords, expected_coords), "Area coordinates do not match expected coordinates"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_upperlower_corners():
    # Arrange & Act
    room = RectangularRoom(center=MapCoords(10, 10), size=(6, 4))

    # Assert
    try:
        assert room.upperLeft_corner == MapCoords(7, 8), "Expected upper left corner to be at (7,8)"
        assert room.lowerRight_corner == MapCoords(13, 12), "Expected lower right corner to be at (13,12)"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass
    
def test_rectangular_room_contains():
    # Arrange
    room = RectangularRoom(center=MapCoords(5, 5), size=(6, 4))

    # Act & Assert
    try:
        assert room.contains(MapCoords(5, 5)) == True, "Expected center to be inside the room"
        assert room.contains(MapCoords(3, 4)) == True, "Expected (3,4) to be inside the room"
        assert room.contains(MapCoords(8, 6)) == False, "Expected (8,6) to be outside the room"
        assert room.contains(MapCoords(2, 2)) == False, "Expected (2,2) to be outside the room"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_intersects():
    # Arrange
    room1 = RectangularRoom(center=MapCoords(5, 5), size=(6, 4))
    room2 = RectangularRoom(center=MapCoords(7, 5), size=(6, 4))
    room3 = RectangularRoom(center=MapCoords(12, 5), size=(6, 4))

    # Act & Assert
    try:
        assert room1.intersects(room2) == True, "Expected room1 to intersect with room2"
        assert room1.intersects(room3) == False, "Expected room1 to not intersect with room3"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_rectangular_room_random_location():
    # Arrange
    room = RectangularRoom(center=MapCoords(10, 10), size=(8, 6))

    # Act
    random_location = room.random_location()

    # Assert
    try:
        assert room.contains(random_location) == True, "Expected random location to be inside the room"

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
        assert room.center == MapCoords(0, 0), "Expected center to be at (0,0)"
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
    room = CircularRoom(center=MapCoords(10, 10), radius=7)

    # Assert
    try:
        assert room.center == MapCoords(10, 10), "Expected center to be at (10,10)"
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
    room = CircularRoom(center=MapCoords(0, 0), radius=3)
    inner_area = room.inner_area
    center = (room.width // 2, room.height // 2)

    # Assert
    try:
        expected_area = np.fromfunction(lambda xx, yy: (xx - center[0]) ** 2 + (yy - center[1]) ** 2 + 2 <= 9,
                               (7, 7), dtype=int)
        assert np.array_equal(inner_area, expected_area), "Inner area does not match expected area"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_room_area_coordinates():
    # Arrange & Act
    room = CircularRoom(center=MapCoords(5, 5), radius=5)
    area_coords = room.area_coordinates()

    # Assert
    try:
        expected_area = np.fromfunction(lambda xx, yy: (xx - 5) ** 2 + (yy - 5) ** 2 + 2 <= 25,
                               (11, 11), dtype=int)
        expected_coords = np.argwhere(expected_area) + np.array([room.upperLeft_corner.x, room.upperLeft_corner.y])
        assert np.array_equal(area_coords, expected_coords), "Area coordinates do not match expected coordinates"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_room_contains():
    # Arrange
    room = CircularRoom(center=MapCoords(5, 5), radius=3)
    area = room.inner_area

    # Act & Assert
    try:
        assert room.contains(MapCoords(5, 5)) == True, "Expected center to be inside the room"
        assert room.contains(MapCoords(7, 5)) == True, "Expected (7,5) to be inside the room"
        assert room.contains(MapCoords(9, 5)) == False, "Expected (9,5) to be outside the room"
        assert room.contains(MapCoords(2, 2)) == False, "Expected (2,2) to be outside the room"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_room_intersects():
    # Arrange
    room1 = CircularRoom(center=MapCoords(5, 5), radius=3)
    room2 = CircularRoom(center=MapCoords(7, 5), radius=3)
    room3 = CircularRoom(center=MapCoords(12, 5), radius=3)

    # Act & Assert
    try:
        assert room1.intersects(room2) == True, "Expected room1 to intersect with room2"
        assert room1.intersects(room3) == False, "Expected room1 to not intersect with room3"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_room_random_location():
    # Arrange
    room = CircularRoom(center=MapCoords(10, 10), radius=5)

    # Act
    random_location = room.random_location()

    # Assert
    try:
        assert room.contains(random_location) == True, "Expected random location to be inside the room"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_circular_rectangular_intersects():
    # Arrange
    circular_room = CircularRoom(center=MapCoords(5, 5), radius=3)
    rectangular_room1 = RectangularRoom(center=MapCoords(7, 5), size=(6, 4))
    rectangular_room2 = RectangularRoom(center=MapCoords(12, 5), size=(6, 4))

    # Act & Assert
    try:
        assert circular_room.intersects(rectangular_room1) == True, "Expected circular room to intersect with rectangular_room1"
        assert circular_room.intersects(rectangular_room2) == False, "Expected circular room to not intersect with rectangular_room2"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass