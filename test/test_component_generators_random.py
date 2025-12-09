import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.tilemaps.base import MapCoords
from core_components.tilemaps.library import GenericTileMap
from core_components.generators.random import RECTANGULAR_ROOM_TEMPLATE, GenericDungeonGenerator

def test_dungeon_generator_empty_init():
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

def test_dungeon_generator_parameter_init():
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

def test_dungeon_generator_attributes():
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

def test_dungeon_generator_clear():
    # Arrange
    dungeon_gen = GenericDungeonGenerator() 
    dungeon_gen.rooms.append(RECTANGULAR_ROOM_TEMPLATE)
    dungeon_gen.corridors.append(np.full((10, 10), fill_value=True))
    dungeon_gen.tilemap.tiles[:] = dungeon_gen.tilemap.resources['tile_types']["floor"]
    
    # Act
    dungeon_gen.clear()

    # Assert
    try:
        assert dungeon_gen.rooms == [], "Expected 'rooms' list to be empty after clear()"
        assert dungeon_gen.corridors == [], "Expected 'corridors' list to be empty after clear()"
        assert np.all(dungeon_gen.tilemap.tiles == dungeon_gen.tilemap.resources['tile_types']["default"]), "Expected all tiles to be 'default' after clear()"
    
    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass