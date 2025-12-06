import pytest
import numpy as np
import sys

# Ensure the src directory is on sys.path so dataset can be imported
SRC_DIR = r'C:\Users\jason\workspaces\repos\jrl' or ".."

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from src.components.game_map import GameMap
from src.resources.tile_types import graphic_dtype

def test_width_height():
    game_map = GameMap(20, 30)
    try:
        assert game_map.width == 20
        assert game_map.height == 30

    except AssertionError:
        pytest.fail("Width or height did not match expected values")

def test_tiles_initialization():
    game_map = GameMap(10, 10)
    blank_color =  np.array((0, [0, 0, 0], [0, 0, 0]), dtype=graphic_dtype)

    try:
        assert game_map.tiles.shape == (10, 10)
        assert np.all(game_map.tiles['traversable'] == False)
        assert np.all(game_map.tiles['transparent'] == False)
        assert np.all(game_map.tiles['visible'] == False)
        assert np.all(game_map.tiles['explored'] == False)
        assert np.all(game_map.tiles['color'] == blank_color)

    except AssertionError:
        pytest.fail("Tiles initialization did not match expected values")

def test_in_bounds():
    game_map = GameMap(5, 5)
    try:
        assert game_map.in_bounds(GameMap.get_map_coords(0, 0)) == True
        assert game_map.in_bounds(GameMap.get_map_coords(4, 4)) == True
        assert game_map.in_bounds(GameMap.get_map_coords(5, 5)) == False
        assert game_map.in_bounds(GameMap.get_map_coords(-1, 0)) == False
        assert game_map.in_bounds(GameMap.get_map_coords(0, -1)) == False
        
    except AssertionError:
        pytest.fail("In bounds check did not match expected values")

def test_set_visible_and_reset():
    game_map = GameMap(3, 3)
    fov = np.array([[True, False, True],
                    [False, True, False],
                    [True, True, True]])
    try:
        game_map.set_visible(fov)
        assert np.array_equal(game_map.tiles['visible'], fov)
    except AssertionError:
        pytest.fail("Set visible did not match expected values")

    try:
        game_map.reset_visibility()
        assert np.all(game_map.tiles['visible'] == False)
    except AssertionError:
        pytest.fail("Reset visibility did not match expected values")

def test_update_explored():
    game_map = GameMap(3, 3)
    fov1 = np.array([[True, False, False],
                     [False, True, False],
                     [False, False, False]])
    fov2 = np.array([[False, True, False],
                     [False, False, True],
                     [False, False, False]])
    
    try:
        game_map.update_explored(fov1)
        assert np.array_equal(game_map.tiles['explored'], fov1)
    except AssertionError:
        pytest.fail("Update explored with fov1 did not match expected values")
    
    try:
        game_map.update_explored(fov2)
        expected_explored = np.array([[True, True, False],
                                      [False, True, True],
                                      [False, False, False]])
        assert np.array_equal(game_map.tiles['explored'], expected_explored)
    except AssertionError:
        pytest.fail("Update explored with fov2 did not match expected values")

def test_is_traversable_transparent_visible_explored():
    game_map = GameMap(2, 2)
    
    # Set tile (0,0) as traversable, transparent, visible, and explored
    game_map.tiles['traversable'][0, 0] = True
    game_map.tiles['transparent'][0, 0] = True
    game_map.tiles['visible'][0, 0] = True
    game_map.tiles['explored'][0, 0] = True
    
    # Tile (0,0) should return True for all checks
    try:
        assert game_map.is_traversable(GameMap.get_map_coords(0, 0)) == True
        assert game_map.is_transparent(GameMap.get_map_coords(0, 0)) == True
        assert game_map.is_visible(GameMap.get_map_coords(0, 0)) == True
        assert game_map.is_explored(GameMap.get_map_coords(0, 0)) == True
    except AssertionError:
        pytest.fail("Tile (0,0) checks did not match expected values")
    
    # Tile (1,1) is not set, should return False for all checks
    try:
        assert game_map.is_traversable(GameMap.get_map_coords(1, 1)) == False
        assert game_map.is_transparent(GameMap.get_map_coords(1, 1)) == False
        assert game_map.is_visible(GameMap.get_map_coords(1, 1)) == False
        assert game_map.is_explored(GameMap.get_map_coords(1, 1)) == False
    except AssertionError:
        pytest.fail("Tile (1,1) checks did not match expected values")

def test_out_of_bounds_checks():
    game_map = GameMap(2, 2)
    out_of_bounds_coords = [
        GameMap.get_map_coords(-1, 0),
        GameMap.get_map_coords(0, -1),
        GameMap.get_map_coords(2, 0),
        GameMap.get_map_coords(0, 2),
    ]
    try:
        for coords in out_of_bounds_coords:
            assert game_map.in_bounds(coords) == False
    except AssertionError:
        pytest.fail("In bounds check did not match expected values")

    try:
        for coords in out_of_bounds_coords:
            assert game_map.is_traversable(coords) == False
            assert game_map.is_transparent(coords) == False
            assert game_map.is_visible(coords) == False
            assert game_map.is_explored(coords) == False
    except AssertionError:
        pytest.fail("Out of bounds checks did not match expected values")

def test_get_map_coords():
    coords = GameMap.get_map_coords(3, 4)
    try:
        assert coords.x == 3
        assert coords.y == 4
    except AssertionError:
        pytest.fail("Get map coords did not match expected values")
