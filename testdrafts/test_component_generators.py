import pytest
import numpy as np

from core_components.tiles.base import TileCoordinate
from core_components.maps.base import BaseTileGrid
from core_components.generators.base import BaseMapGenerator
from core_components.generators.library import DEFAULT_MAP_TEMPLATE, CIRCULAR_ROOM_TEMPLATE, RECTANGULAR_ROOM_TEMPLATE, DungeonGenerator


def test_something():
    assert True

# def test_generator_random_empty_init():
#     # Arrange & Act
#     dungeon_gen = DungeonGenerator()

#     # Act & Assert
#     try:
#         assert isinstance(dungeon_gen.map_template, BaseTileGrid), "Expected tilemap to be an instance of BaseTileGrid"
#         assert dungeon_gen.width == DEFAULT_MAP_TEMPLATE.grid.width, "Expected width to match template width upon initialization"
#         assert dungeon_gen.height == DEFAULT_MAP_TEMPLATE.grid.height, "Expected height to match template height upon initialization"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_generator_random_parameter_init():
#     # Arrange & Act
#     size = (30, 40)
#     dungeon_gen = GenericDungeonGenerator(size=size)

#     # Act & Assert
#     try:
#         assert dungeon_gen.tilemap.width == size[0], "Expected tilemap width to match initialized size"
#         assert dungeon_gen.tilemap.height == size[1], "Expected tilemap height to match initialized size"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass    

# def test_generator_random_attributes():
#     # Arrange & Act
#     dungeon_gen = GenericDungeonGenerator()

#     # Act & Assert
#     try:
#         assert hasattr(dungeon_gen, "rooms"), "Expected 'rooms' attribute to exist"
#         assert isinstance(dungeon_gen.rooms, list), "Expected 'rooms' attribute to be a list"
#         assert hasattr(dungeon_gen, "corridors"), "Expected 'corridors' attribute to exist"
#         assert isinstance(dungeon_gen.corridors, list), "Expected 'corridors' attribute to be a list"

#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

# def test_generator_random_clear():
#     # Arrange
#     dungeon_gen = GenericDungeonGenerator() 
#     dungeon_gen.rooms.append(RECTANGULAR_ROOM_TEMPLATE)
#     dungeon_gen.corridors.append(np.full((10, 10), fill_value=True))
#     dungeon_gen.tilemap.tiles['type'][:] = dungeon_gen.tilemap.resources['tiles']['floor']
    
#     # Act
#     dungeon_gen.clear()

#     # Assert
#     try:
#         assert dungeon_gen.rooms == [], "Expected 'rooms' list to be empty after clear()"
#         assert dungeon_gen.corridors == [], "Expected 'corridors' list to be empty after clear()"
#         assert np.all(dungeon_gen.tilemap.tiles['type']['name'][:] == 'default'), "Expected all tiles to be 'default' after clear()"
    
#     except AssertionError as e:
#         pytest.fail(str(e))
    
#     # Atavise
#     finally:
#         pass

