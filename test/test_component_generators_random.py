import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.tilemaps.base import MapCoords
from core_components.tilemaps.library import GenericTileMap
from core_components.generators.library import CIRCULAR_ROOM_TEMPLATE, RECTANGULAR_ROOM_TEMPLATE, GenericDungeonGenerator

def test_generator_random_empty_init():
    # Arrange & Act
    dungeon_gen = GenericDungeonGenerator()

    # Act & Assert
    try:
        assert isinstance(dungeon_gen.tilemap, GenericTileMap), "Expected tilemap to be an instance of GenericTileMap"
        assert dungeon_gen.rooms == [], "Expected rooms list to be empty upon initialization"
        assert dungeon_gen.corridors == [], "Expected corridors list to be empty upon initialization"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_random_parameter_init():
    # Arrange & Act
    size = (30, 40)
    dungeon_gen = GenericDungeonGenerator(size=size)

    # Act & Assert
    try:
        assert dungeon_gen.tilemap.width == size[0], "Expected tilemap width to match initialized size"
        assert dungeon_gen.tilemap.height == size[1], "Expected tilemap height to match initialized size"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass    

def test_generator_random_attributes():
    # Arrange & Act
    dungeon_gen = GenericDungeonGenerator()

    # Act & Assert
    try:
        assert hasattr(dungeon_gen, "rooms"), "Expected 'rooms' attribute to exist"
        assert isinstance(dungeon_gen.rooms, list), "Expected 'rooms' attribute to be a list"
        assert hasattr(dungeon_gen, "corridors"), "Expected 'corridors' attribute to exist"
        assert isinstance(dungeon_gen.corridors, list), "Expected 'corridors' attribute to be a list"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_random_clear():
    # Arrange
    dungeon_gen = GenericDungeonGenerator() 
    dungeon_gen.rooms.append(RECTANGULAR_ROOM_TEMPLATE)
    dungeon_gen.corridors.append(np.full((10, 10), fill_value=True))
    dungeon_gen.tilemap.tiles['type'][:] = dungeon_gen.tilemap.resources['tiles']['floor']
    
    # Act
    dungeon_gen.clear()

    # Assert
    try:
        assert dungeon_gen.rooms == [], "Expected 'rooms' list to be empty after clear()"
        assert dungeon_gen.corridors == [], "Expected 'corridors' list to be empty after clear()"
        assert np.all(dungeon_gen.tilemap.tiles['type']['name'][:] == 'default'), "Expected all tiles to be 'default' after clear()"
    
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_random_spawn_rectangularroom():
    # Arrange
    dungeon_gen = GenericDungeonGenerator() 
    room_template = RECTANGULAR_ROOM_TEMPLATE
    center = MapCoords(15, 15)
    size = (10, 8)

    # Act
    room_instance = dungeon_gen.spawn_room(room_template, center=center, size=size)

    # Assert
    try:
        assert room_instance is not None, "Expected spawned room instance to not be None"
        assert room_instance.width == 10, "Expected spawned room width to be 10"
        assert room_instance.height == 8, "Expected spawned room height to be 8"
        assert room_instance.center == center, "Expected spawned room center to be at (15, 15)"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_random_spawn_room_circularroom():
    # Arrange
    dungeon_gen = GenericDungeonGenerator() 
    circular_room_template = CIRCULAR_ROOM_TEMPLATE
    center = MapCoords(20, 20)
    radius = 5

    # Act
    room_instance = dungeon_gen.spawn_room(circular_room_template, center=center, size=(radius*2, radius))
    # Assert
    try:    
        assert room_instance is not None, "Expected spawned circular room instance to not be None"
        assert isinstance(room_instance, type(circular_room_template)), "Expected spawned room to be instance of circular room template type"
        assert room_instance.radius == radius, "Expected spawned circular room radius to be 5"
        assert room_instance.center == center, "Expected spawned circular room center to be at (20, 20)"
    except AssertionError as e:
        pytest.fail(str(e))
    # Atavise
    finally:
        pass

def test_generator_random_spawn_random_rooms():
    # Arrange
    dungeon_gen = GenericDungeonGenerator() 
    max_rooms = 5
    min_room_size = 4
    max_room_size = 10

    # Act
    rooms = list(dungeon_gen.spawn_random_rooms(max_rooms, min_room_size, max_room_size))

    # Assert
    try:
        assert len(rooms) > 0, "Expected at least one room to be spawned"
        assert len(rooms) <= max_rooms, f"Expected at most {max_rooms} rooms to be spawned"
        for room in rooms:
            assert room is not None, "Expected spawned room instance to not be None"
            assert min_room_size <= room.width <= max_room_size, f"Expected room width to be between {min_room_size} and {max_room_size}"
            assert min_room_size <= room.height <= max_room_size, f"Expected room height to be between {min_room_size} and {max_room_size}"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_random_spawn_corridor():
    # Arrange
    dungeon_gen = GenericDungeonGenerator(size=(30, 30)) 
    start = MapCoords(5, 5)
    end = MapCoords(15, 10)

    # Act
    corridor_mask = dungeon_gen.spawn_corridor(start, end)

    # Assert
    try:
        assert corridor_mask.shape == (dungeon_gen.tilemap.width, dungeon_gen.tilemap.height), "Expected corridor mask to match tilemap dimensions"
        assert corridor_mask[start.x, start.y] == True, "Expected corridor to include start point"
        assert corridor_mask[end.x, end.y] == True, "Expected corridor to include end point"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_random_generate():
    # Arrange
    dungeon_gen = GenericDungeonGenerator(size=(100, 100)) 
    max_rooms = 10
    min_room_size = 5
    max_room_size = 15

    # Act
    dungeon_gen.generate(max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size)

    # Assert
    try:
        assert len(dungeon_gen.rooms) > 0, "Expected at least one room to be generated"
        assert len(dungeon_gen.rooms) <= max_rooms, f"Expected at most {max_rooms} rooms to be generated"
        assert len(dungeon_gen.corridors) > 0, "Expected at least one corridor to be generated"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass