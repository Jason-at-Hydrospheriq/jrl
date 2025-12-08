import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np

from core_components.maps.tilemaps import GenericTileMap
from core_components.maps.generators import GenericDungeonGenerator

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


