import pytest
from sys import path
import numpy as np
import tcod

path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from core_components.maps.atlas import Atlas
from core_components.maps.library import DefaultTileMap

def test_component_atlas_initialization():
    atlas = Atlas()
    assert isinstance(atlas.generators, dict)
    assert isinstance(atlas.library, dict)
    assert isinstance(atlas.active, DefaultTileMap)
    assert '_empty' in atlas.library

def test_component_atlas_create_map():
    atlas = Atlas()
    atlas.create_map()
    n_walls = np.sum(atlas.active.tiles['graphic_type']['name'] == 'wall')
    n_blocks_movement = np.sum(atlas.active.tiles['blocks_movement'])
    n_blocks_vision = np.sum(atlas.active.tiles['blocks_vision'])
    assert n_walls > 0
    assert n_blocks_movement > 0
    assert n_blocks_vision > 0
    assert n_walls == n_blocks_movement == n_blocks_vision

    assert len(atlas.library) == 2  # _empty and level_0
    assert atlas.active == atlas.library['level_0']
    
    atlas.create_map()
    assert len(atlas.library) == 3  # _empty, level_0, and level_1
    assert atlas.active == atlas.library['level_1']
    assert atlas.active != atlas.library['level_0']

def test_component_atlas_set_active_map():
    atlas = Atlas()
    atlas.create_map()
    atlas.create_map()
    
    atlas.set_active_map('level_0')
    assert atlas.active == atlas.library['level_0']
    
    atlas.set_active_map('level_1')
    assert atlas.active == atlas.library['level_1']
    
    with pytest.raises(ValueError):
        atlas.set_active_map('non_existent_map')
    
def test_component_atlas_get_map():
    atlas = Atlas()
    atlas.create_map()
    atlas.create_map()
    
    map_0 = atlas.get_map('level_0')
    assert map_0 == atlas.library['level_0']
    
    map_1 = atlas.get_map('level_1')
    assert map_1 == atlas.library['level_1']
    
    with pytest.raises(ValueError):
        atlas.get_map('non_existent_map')