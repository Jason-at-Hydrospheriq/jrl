import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')

from core_components.generators.library import DEFAULT_MAP_TEMPLATE, DungeonGenerator, CIRCULAR_ROOM_TEMPLATE, RECTANGULAR_ROOM_TEMPLATE
from core_components.maps.library import DefaultTileMap
from core_components.tiles.library import TileCoordinate, TileTuple 

def test_generator_random_empty_init():
    # Arrange & Act
    dungeon_gen = DungeonGenerator()

    # Act & Assert
    try:
        assert isinstance(dungeon_gen.map_template, DefaultTileMap), "Expected tilemap to be an instance of DefaultTileMap upon initialization"
        assert dungeon_gen.width == DEFAULT_MAP_TEMPLATE.grid.width, "Expected width to match template width upon initialization"
        assert dungeon_gen.height == DEFAULT_MAP_TEMPLATE.grid.height, "Expected height to match template height upon initialization"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_generate():
    # Arrange
    dungeon_gen = DungeonGenerator()

    # Act
    dungeon = dungeon_gen.generate()

    # Act
    wall_layout = dungeon.get_tile_layout('wall')
    floor_layout = dungeon.get_tile_layout('floor')

    if wall_layout is not None and floor_layout is not None:
        expected_floor_count = dungeon.tiles.size - wall_layout.sum()
        expected_wall_count = dungeon.tiles.size - floor_layout.sum()

        # Assert
        try:
            assert isinstance(dungeon, DefaultTileMap), "Expected generated map to be an instance of DefaultTileMap"
            assert id(dungeon) != id(dungeon_gen.map_template), "Expected generated map to be a new instance and not the same as the template"
            assert dungeon.grid.width == dungeon_gen.width, "Expected generated map width to match generator width"
            assert dungeon.grid.height == dungeon_gen.height, "Expected generated map height to match generator height"
        
            assert wall_layout is not None, "Expected generated map to have a wall layout object"
            assert floor_layout is not None, "Expected generated map to have a floor layout object"
            assert expected_wall_count > 0, "Expected generated map to have wall tiles"
            assert expected_floor_count > 0, "Expected generated map to have floor tiles"
            assert wall_layout.sum() == (floor_layout.size - floor_layout.sum()), "Expected all tiles other than floors to be walls"

            assert dungeon.blocks_movement.sum() == expected_floor_count, "Expected all visible tiles to be floors"
            assert dungeon.tiles.size - dungeon.blocks_vision.sum() == expected_wall_count, "Expected all transparent tiles to be floors"    
        
        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass

def test_generator_dungeon_add_rectangularroom():
    # Arrange
    dungeon_gen = DungeonGenerator() 
    room_template = RECTANGULAR_ROOM_TEMPLATE
    center =  dungeon_gen.map_template.center
    size = TileTuple(([10], [8]))

    # Act
    room_instance = dungeon_gen.add(room_template, center=center, size=size)

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

def test_generator_dungeon_add_circularroom():
    # Arrange
    dungeon_gen = DungeonGenerator() 
    room_template = CIRCULAR_ROOM_TEMPLATE
    center =  dungeon_gen.map_template.center
    radius = 5

    # Act
    room_instance = dungeon_gen.add(room_template, center=center, size=TileTuple(([radius*2], [radius*2])))

    # Assert
    try:
        assert room_instance is not None, "Expected spawned room instance to not be None"
        assert room_instance.to_mask.shape == dungeon_gen.map_template.tiles.shape, "Expected spawned room mask to match tilemap dimensions"
        assert room_instance.radius == 5, "Expected spawned room radius to be 5" #type: ignore
        assert room_instance.center == center, "Expected spawned room center to be at (15, 15)"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_dungeon_room_generator():
    # Arrange
    max_rooms = 5
    min_room_size = 4
    max_room_size = 10
    dungeon_gen = DungeonGenerator()

    # Act
    dungeon = dungeon_gen.generate()
    rooms = dungeon_gen.room_generator(dungeon=dungeon, max_rooms=max_rooms, min_room_size=min_room_size, max_room_size=max_room_size)
    
    # Assert
    try:
        assert len(list(rooms)) > 0, "Expected at least one room to be spawned"
        assert len(list(rooms)) <= max_rooms, f"Expected at most {max_rooms} rooms to be spawned"
        for room in rooms:
            assert room is not None, "Expected spawned room instance to not be None"
            assert min_room_size <= room.width <= max_room_size, f"Expected room width to be between {min_room_size} and {max_room_size}"
            assert min_room_size <= room.height <= max_room_size, f"Expected room height to be between {min_room_size} and {max_room_size}"

    except AssertionError as e:
        pytest.fail(str(e))
    
    # Atavise
    finally:
        pass

def test_generator_add_corridors():
    # Arrange
    max_rooms = 5
    min_room_size = 4
    max_room_size = 10
    dungeon_gen = DungeonGenerator()
    dungeon = dungeon_gen.generate()

    # Act
    area_centers = [area.center for key, area in dungeon.areas.items() if not key.startswith('corridor_')]
    corridors = dungeon_gen.add_corridors(dungeon)

    if corridors and area_centers is not None:
        # Assert
        try:
            for idx, items in enumerate(zip(area_centers[:-1], area_centers[1:])):
                start, end = items
                assert corridors[idx].start == start, "Expected corridor to start at area center"
                assert corridors[idx].end == end, "Expected corridor to end at area center"

                assert corridors[idx].to_mask.shape == dungeon.tiles.shape, "Expected corridor mask to match tilemap dimensions"


        except AssertionError as e:
            pytest.fail(str(e))
        
        # Atavise
        finally:
            pass
