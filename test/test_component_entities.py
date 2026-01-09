import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
from transitions import Machine 
from unittest.mock import Mock, MagicMock, patch
import numpy as np


from entities import BaseGameEntity, AICharacter, Character, CombatEntity, MobileEntity, TargetableEntity, TargetingEntity
from entities.base import BaseGameSubState, BaseParentState
from entities.components  import CollisionSubState, CombatSubState, TargetedSubState, TargetingSubState, CharacterHealthSubState
from game_types import GameEntity, EntityParentState
from atlas_components.tiles.base import TileCoordinate
from store.components import Atlas
from loop_resources import investigate, PlayerCharacter
from store import GameStore
from loop_resources.components import SubLoopHandler


class DummyGameStore:
    location: None = None
    state_vector = {}
    machine: Machine | None = None
    targeter: BaseGameEntity | None = None
    target: BaseGameEntity | None = None
    target_in_fov: bool = False
    threat_level: int = 0
    distance_to_target: int = 10
    focus: TargetingSubState | None = None
    destination_is_blocking_entity: bool = False
    destination_is_blocking_terrain: bool = False
    destination_is_map_boundary: bool = False
    atlas: Atlas = Atlas()


class DummyPortfolio:
    live_actors: list[BaseGameEntity] = [BaseGameEntity(name='existing_entity')]


class DummyTarget:
    target: BaseGameEntity | None = None
    targeter: BaseGameEntity | None = None
    location: TileCoordinate | None = None
    hp: int = 0
    max_hp: int = 0

    def set_targeter(self, targeter: BaseGameEntity) -> None:
        self.targeter = targeter

    def clear_targeter(self) -> None:
        self.targeter = None

    def take_damage(self, damage: int) -> None:
        self.hp = max(0, self.hp - damage)


def test_entity_base_game_substate():
    try:
        # Arrange
        store = DummyGameStore()
        substate = BaseGameSubState(store=store, name='test') # type: ignore

        # Act
        substate.set_bits()
        actual_on_map_no_location = substate.is_on_map() # Expect False
        actual_not_on_map_no_location = substate.is_not_on_map() # Expect True
        substate.store.location = 'some_location' # type: ignore
        substate.set_bits()
        actual_on_map_w_location = substate.is_on_map() # Expect True
        actual_not_on_map_w_location = substate.is_not_on_map() # Expect False

        # Assert
        assert actual_on_map_no_location == False, "Expected is_on_map to be False when no location is set"
        assert actual_not_on_map_no_location == True, "Expected is_not_on_map to be True when no location is set"
        assert actual_on_map_w_location == True, "Expected is_on_map to be True when location is set"
        assert actual_not_on_map_w_location == False, "Expected is_not_on_map to be False when location is set"
        assert substate.store.state_vector == {'on_map': True}, "Expected state_vector to have 'on_map' set to True" # type: ignore

    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass
    
def test_entity_base_game_entity():
    try:
        # Arrange
        store = GameStore()

        # Act 
        entity = BaseGameEntity(store=store, name='test_entity')
        entity.machine = Machine()

        # Assert
        assert isinstance(entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"
        assert isinstance(entity, BaseParentState), "Expected entity be an instance of BaseParentState"
        assert isinstance(entity, GameEntity), "Expected entity to duck type to GameEntity"
        assert isinstance(entity, EntityParentState), "Expected entity to duck type to EntityParentState"

        assert entity.name == 'test_entity'
        assert entity.state_vector == {'on_map': False}, "Expected initial state_vector to have 'on_map' set to False"
        assert len(entity._substates_manifest) == 1, "Expected one substate in _substates_manifest"
        assert isinstance(entity.substates[0], BaseGameSubState), "Expected first substate to be instance of BaseGameSubState"
        assert entity.location == None, "Expected initial location to be None"
        assert entity.blocks_movement == True, "Expected blocks_movement to be True by default"
        assert entity.spawn.is_not_in_play() == True, "Expected spawn to be not in play initially" # type: ignore

        entity.location = TileCoordinate.from_tuple((0,0))
        entity.update()

        assert entity.state_vector == {'on_map': True}, "Expected state_vector to have 'on_map' set to True after update"
        assert isinstance(entity.location, TileCoordinate), "Expected location to be instance of TileCoordinate"
        assert entity.spawn.is_in_play() == True, "Expected spawn to be in play after update" # type: ignore 

    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_entity_collision_substate():
    try:
        # Arrange
        store = DummyGameStore()
        store.state_vector = {'on_map': False}
        substate = CollisionSubState(store=store, name='collision_test') # type: ignore

        # Act
        substate.set_bits()
        substate.update() # type: ignore
        actual_none_state = substate.state # type: ignore

        store.location = TileCoordinate.from_tuple((0,0)) # type: ignore
        substate.store.state_vector['on_map'] = True # type: ignore simulate basegamesubstate update
        substate.set_bits()
        substate.update() # type: ignore
        actual_with_location_state = substate.state # type: ignore
        actual_is_on_map_location = substate.is_on_map() # Expect True

        store.destination_is_blocking_entity = False
        store.destination_is_blocking_terrain = True
        substate.set_bits()
        substate.update() # type: ignore
        actual_with_terrain_collision_state = substate.state # type: ignore

        store.destination_is_blocking_entity = True
        store.destination_is_blocking_terrain = False
        substate.set_bits()
        substate.update() # type: ignore
        actual_with_entity_collision_state = substate.state # type: ignore

        store.destination_is_blocking_entity = False
        store.destination_is_map_boundary = True
        substate.set_bits()
        substate.update() # type: ignore
        actual_with_boundary_collision_state = substate.state # type: ignore

        # Assert
        assert actual_none_state == 'unknown', "Expected state to be 'unknown' when no location is set"
        assert actual_with_location_state == 'not_colliding', "Expected state to be 'not_colliding' when location is set and no collisions"
        assert actual_is_on_map_location == True, "Expected is_on_map to be true when location is set"
        assert actual_with_entity_collision_state == 'colliding_with_entity', "Expected state to be 'colliding_with_entity' when destination is blocking entity"
        assert actual_with_terrain_collision_state == 'colliding_with_terrain', "Expected state to be 'colliding_with_terrain' when destination is blocking terrain"
        assert actual_with_boundary_collision_state == 'colliding_with_boundary', "Expected state to be 'colliding_with_boundary' when destination is blocking boundary"

    except AssertionError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")

    # Atavise
    finally:
        pass

def test_entity_targeted_substate():
    try:
        # Arrange
        store = DummyGameStore()
        store.state_vector = {'on_map': False}
        substate = TargetedSubState(store=store, name='targeted_test') # type: ignore

        # Act
        substate.set_bits()
        substate.update() # type: ignore
        actual_is_on_map_none = substate.is_on_map() # Expect False
        actual_is_target_none = substate.is_target() # Expect False
        actual_is_not_target_none = substate.is_not_target() # Expect True
        actual_none_state = substate.state # type: ignore

        store.targeter = BaseGameEntity(name='dummy_targeter') # type: ignore
        substate.set_bits()
        substate.update() # type: ignore
        actual_is_target_with_targeter = substate.is_target() # Expect True
        actual_is_not_target_with_targeter = substate.is_not_target() # Expect False
        actual_no_location_state = substate.state # type: ignore

        store.location = TileCoordinate.from_tuple((0,0)) # type: ignore
        substate.store.state_vector['on_map'] = True # type: ignore simulate basegamesubstate update
        substate.set_bits()
        substate.update() # type: ignore
        actual_with_location_state = substate.state # type: ignore
        actual_is_on_map_location = substate.is_on_map() # Expect True

        store.targeter = None # type: ignore
        substate.set_bits()
        substate.update() # type: ignore
        actual_without_targeter_state = substate.state # type: ignore

        # Assert
        assert substate.is_target() == substate.store.state_vector['is_target'], "Expected is_target method to reflect state_vector value" # type: ignore
        assert substate.is_not_target() == (not substate.store.state_vector['is_target']), "Expected is_not_target method to reflect inverse of state_vector value" # type: ignore
        assert actual_is_target_none == False, "Expected is_target to be False when no targeter is set"
        assert actual_is_not_target_none == True, "Expected is_not_target to be True when no targeter is set"
        assert actual_is_on_map_none == False, "Expected is_on_map to be false when no location is set"
        assert actual_none_state == 'unknown', "Expected state to be 'unknown' when no targeter/location is set"

        assert actual_is_target_with_targeter == True, "Expected is_target to be True when targeter is set"
        assert actual_is_not_target_with_targeter == False, "Expected is_not_target to be False when targeter is set"
        assert actual_no_location_state == 'unknown', "Expected state to be 'unknown' when no location is set"

        assert actual_is_on_map_location == True, "Expected is_on_map to be true when location is set"
        assert actual_with_location_state == 'targeted', "Expected state to be 'targeted' when targeter and location are set"

        assert actual_without_targeter_state == 'not_targeted', "Expected state to be 'not_targeted' when targeter is none and location is set"

    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_entity_targeting_substate():
    try:
        # Arrange
        store = DummyGameStore()
        store.state_vector = {'on_map': False}
        substate = TargetingSubState(store=store, name='targeting_test') # type: ignore

        # Act
        substate.set_bits()
        substate.update() # type: ignore
        actual_is_on_map_none = substate.is_on_map() # Expect False
        actual_has_visible_target_none = substate.has_visible_target() # Expect False
        actual_has_no_visible_target_none = substate.has_no_visible_target() # Expect True
        actual_has_hostile_target_none = substate.has_hostile_target() # Expect False
        actual_has_no_hostile_target_none = substate.has_no_hostile_target() # Expect True
        actual_none_state = substate.state # type: ignore

        store.location = TileCoordinate.from_tuple((0,0)) # type: ignore
        substate.store.state_vector['on_map'] = True # type: ignore simulate basegamesubstate update
        substate.set_bits()
        substate.update() # type: ignore
        actual_with_location_state = substate.state # type: ignore
        actual_is_on_map_location = substate.is_on_map() # Expect True

        store.target = BaseGameEntity(name='dummy_target') # type: ignore
        substate.set_bits()
        substate.update() # type: ignore
        actual_new_target_state = substate.state # type: ignore

        store.target_in_fov = True
        substate.set_bits()
        substate.update() # type: ignore
        actual_has_visible_target_state = substate.state # type: ignore
        actual_state_changed = substate.state_changed

        store.threat_level = 95
        substate.set_bits()
        substate.update() # type: ignore
        actual_has_hostile_target_state = substate.state # type: ignore

        # Assert
        assert substate.has_visible_target() == substate.store.state_vector['target_in_fov'], "Expected has_visible_target method to reflect state_vector value" # type: ignore
        assert substate.has_no_visible_target() == (not substate.store.state_vector['target_in_fov']), "Expected has_no_visible_target method to reflect inverse of state_vector value" # type: ignore
        assert substate.has_hostile_target() == substate.store.state_vector['target_is_hostile'], "Expected has_hostile_target method to reflect state_vector value" # type: ignore
        assert substate.has_no_hostile_target() == (not substate.store.state_vector['target_is_hostile']), "Expected has_no_hostile_target method to reflect inverse of state_vector value" # type: ignore
        assert actual_has_visible_target_none == False, "Expected has_visible_target to be False when no target is set"
        assert actual_has_no_visible_target_none == True, "Expected has_no_visible_target to be True when no target is set"
        assert actual_has_hostile_target_none == False, "Expected has_hostile_target to be False when no target is set"
        assert actual_has_no_hostile_target_none == True, "Expected has_no_hostile_target to be True when no target is set"
        assert actual_is_on_map_none == False, "Expected is_on_map to be false when no location is set"
        assert actual_none_state == 'unknown', "Expected state to be 'unknown' when no target/location is set"
        
        assert actual_with_location_state == 'idle', "Expected state to be 'idle' when no location is set"
        assert actual_is_on_map_location == True, "Expected is_on_map to be true when location is set"

        assert actual_new_target_state == 'searching', "Expected state to be 'searching' when target is set that is not visible or hostile"

        assert actual_has_visible_target_state == 'tracking', "Expected state to be 'tracking' when target is visible but not hostile"
        assert actual_state_changed == True, "Expected state_changed to be True after state transition"

        assert actual_has_hostile_target_state == 'targeting', "Expected state to be 'targeting' when target is hostile"

    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_entity_combat_substate():
    try:
        # Arrange
        store = DummyGameStore()
        store.state_vector = {'on_map': False}
        combat_substate = CombatSubState(store=store, name='combat_test') # type: ignore
        target_substate = TargetingSubState(store=store, name='targeting') # type: ignore
        store.focus = target_substate
        
        # Act
        target_substate.set_bits()
        target_substate.update() # type: ignore
        combat_substate.set_bits()
        combat_substate.update() # type: ignore
        actual_none_state = combat_substate.state # type: ignore

        store.location = TileCoordinate.from_tuple((0,0)) # type: ignore
        store.state_vector['on_map'] = True # Simulate substate update
        target_substate.set_bits()
        target_substate.update() # type: ignore
        combat_substate.set_bits()
        combat_substate.update() # type: ignore
        actual_location_state = combat_substate.state # type: ignore        

        store.target = BaseGameEntity(name='dummy_target')
        store.target_in_fov = True
        target_substate.set_bits()
        target_substate.update() # type: ignore
        combat_substate.set_bits()
        combat_substate.update() # type: ignore
        actual_no_threat_state = combat_substate.state # type: ignore

        store.threat_level = 95
        target_substate.set_bits()
        target_substate.update() # type: ignore
        combat_substate.set_bits()
        combat_substate.update() # type: ignore
        actual_threat_state = combat_substate.state # type: ignore

        store.distance_to_target = 1
        target_substate.set_bits()
        target_substate.update() # type: ignore
        combat_substate.set_bits()
        combat_substate.update() # type: ignore
        actual_attack_state = combat_substate.state # type: ignore

        store.threat_level = 0
        target_substate.set_bits()
        target_substate.update() # type: ignore
        combat_substate.set_bits()
        combat_substate.update() # type: ignore
        actual_disengaged_state = combat_substate.state # type: ignore

        # Assert
        assert actual_none_state == 'unknown', "Expected state to be 'unknown' when no location is set"
        assert actual_location_state == 'peaceful', "Expected state to be 'peaceful' when location is set and not targeting"
        assert actual_no_threat_state == 'peaceful', "Expected state to be 'peaceful' when location is set and tracking target"
        assert actual_threat_state == 'engaged', "Expected state to be 'engaged' when location is set and targeting target"
        assert actual_attack_state == 'fighting', "Expected state to be 'fighting' when hostile target is in range"
        assert actual_disengaged_state == 'disengaged', "Expected state to be 'disengaged' when not targeting a target that is in range"

    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_entity_mobile_entity():
    try:
    # Arrange
        store = GameStore()
        store.atlas = Atlas(store=store)
        store.portfolio = DummyPortfolio() # type: ignore
        if store.portfolio:
            store.portfolio.live_actors[0].location = TileCoordinate.from_tuple((0,1), parent_map_size=store.atlas.active.grid.size) # type: ignore

        tile_layout = store.atlas.active.get_tile_layout('wall')
        if tile_layout is not None:
            tile_layout[1,1] = True
        store.atlas.active.set_tiles(tile_layout, graphic_name='wall')

        # Act 
        entity = MobileEntity(store=store, name='mobile_entity')
        entity.blocks_movement = True
        initial_state_vector = entity.state_vector.copy()
        initial_location = entity.location
        initial_in_play_state = entity.spawn.is_in_play() # type: ignore
        initial_collision_state = entity.collision.state # type: ignore

        entity.location = TileCoordinate.from_tuple((0,0), parent_map_size=store.atlas.active.grid.size)
        entity.update()
        set_location = entity.location
        set_location_in_play_state = entity.spawn.is_in_play() # type: ignore
        set_location_state_vector = entity.state_vector.copy()
        set_location_collision_state = entity.collision.state # type: ignore

        entity.destination = TileCoordinate.from_tuple((-1,-1), parent_map_size=store.atlas.active.grid.size)
        entity.update()
        offmap_state_vector = entity.state_vector.copy()
        offmap_collision_state = entity.collision.state # type: ignore

        entity.destination = TileCoordinate.from_tuple((0,1), parent_map_size=store.atlas.active.grid.size)
        entity.update()
        blocking_entity_state_vector = entity.state_vector.copy()
        blocking_entity_collision_state = entity.collision.state # type: ignore

        entity.destination = TileCoordinate.from_tuple((1,1), parent_map_size=store.atlas.active.grid.size)
        entity.update()
        blocking_terrain_state_vector = entity.state_vector.copy()
        blocking_terrain_collision_state = entity.collision.state # type: ignore

        entity.destination = TileCoordinate.from_tuple((1,0), parent_map_size=store.atlas.active.grid.size)
        entity.update()
        no_blocker_state_vector = entity.state_vector.copy()
        no_blocker_collision_state = entity.collision.state # type: ignore

        entity.move()
        entity.update()
        final_location = entity.location

        initial_hp = entity.hp
        entity.action_locked = True
        entity.hp = 10
        final_hp = entity.hp

        # Assert
        assert isinstance(entity, MobileEntity), "Expected entity to be instance of MobileEntity"
        assert isinstance(entity, BaseGameEntity), "Expected entity to be instance of BaseGameEntity"
        assert isinstance(entity, BaseParentState), "Expected entity be an instance of BaseParentState"
        assert isinstance(entity, GameEntity), "Expected entity to duck type to GameEntity"
        assert isinstance(entity, EntityParentState), "Expected entity to duck type to EntityParentState"

        assert entity.name == 'mobile_entity'
        assert initial_state_vector == {'on_map': False, 'in_boundary_collision': False, 'in_entity_collision': False, 
                                       'in_terrain_collision': False}, "Expected initial state_vector to have 'on_map' set to False"
        assert len(entity._substates_manifest) == 2, "Expected two substates in _substates_manifest"
        assert isinstance(entity.substates[0], BaseGameSubState), "Expected first substate to be instance of BaseGameSubState"
        assert initial_location == None, "Expected initial location to be None"
        assert entity.blocks_movement == True, "Expected blocks_movement to be True by default"
        assert initial_in_play_state == False, "Expected spawn to be not in play initially" # type: ignore
        assert initial_collision_state == 'unknown', "Expected collision state to be 'unknown' initially" # type: ignore

        assert isinstance(set_location, TileCoordinate), "Expected location to be instance of TileCoordinate"
        assert set_location_state_vector['on_map'] == True, "Expected state_vector to have 'on_map' set to True after update"
        assert set_location_in_play_state == True, "Expected spawn to be in play after update" # type: ignore
        assert set_location_collision_state == 'not_colliding', "Expected collision state to be 'not_colliding' after update" # type: ignore

        assert offmap_state_vector['in_boundary_collision'] == True, "Expected state_vector to have 'in_boundary_collision' set to True after moving off map"
        assert offmap_collision_state == 'colliding_with_boundary', "Expected collision state to be 'colliding_with_boundary' after moving off map" # type: ignore
        assert blocking_terrain_state_vector['in_terrain_collision'] == True, "Expected state_vector to have 'in_terrain_collision' set to True after moving into terrain"
        assert blocking_terrain_collision_state == 'colliding_with_terrain', "Expected collision state to be 'colliding_with_terrain' after moving into terrain" # type: ignore
        assert blocking_entity_state_vector['in_entity_collision'] == True, "Expected state_vector to have 'in_entity_collision' set to True after moving into entity"
        assert blocking_entity_collision_state == 'colliding_with_entity', "Expected collision state to be 'colliding_with_entity' after moving into entity" # type: ignore
        assert no_blocker_state_vector['in_entity_collision'] == False, "Expected state_vector to have 'in_entity_collision' set to False after moving into free space"
        assert no_blocker_state_vector['in_terrain_collision'] == False, "Expected state_vector to have 'in_terrain_collision' set to False after moving into free space"
        assert no_blocker_state_vector['in_boundary_collision'] == False, "Expected state_vector to have 'in_boundary_collision' set to False after moving into free space"
        assert no_blocker_collision_state == 'not_colliding', "Expected collision state to be 'not_colliding' after moving into free space" # type: ignore

        assert final_location == TileCoordinate.from_tuple((1,0), parent_map_size=store.atlas.active.grid.size), "Expected final location to be (1,0) after move"
        assert entity.destination == None, "Expected destination to be None after move"
        assert final_hp == initial_hp, "Expected hp to remain unchanged after action_locked move attempt"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    finally:
        pass

def test_entity_targetable_entity():
    try:
        # Arrange
        targeter = BaseGameEntity()
        target = TargetableEntity(name='targetable_entity')
        target.hp = 100
        target.max_hp = 100

        # Act
        initial_targeter = target.targeter
        initial_target_state = target.perception.state # type: ignore | Expect 'unknown'
        initial_target_state_vector = target.state_vector.copy()
        initial_hp = target.hp
        initial_max_hp = target.max_hp

        target.location = TileCoordinate.from_tuple((0,0))
        target.update()
        set_location_target_state = target.perception.state # type: ignore | Expect 'not_targeted'
        set_location_state_vector = target.state_vector.copy()

        target.targeter = targeter # type: ignore
        target.update()
        with_targeter_state = target.perception.state # type: ignore | Expect 'targeted'
        with_targeter_state_vector = target.state_vector.copy()

        target.take_damage(30)
        target.update()
        after_damage_target_state = target.perception.state # type: ignore | Expect 'targeted'
        after_damage_state_vector = target.state_vector.copy()
        after_damage_hp = target.hp
        after_damage_max_hp = target.max_hp

        target.action_locked = True
        target.hp = 10
        final_hp = target.hp

        # Assert
        assert isinstance(target, TargetableEntity), "Expected target to be instance of TargetableEntity"
        assert isinstance(target, BaseGameEntity), "Expected target to be instance of BaseGameEntity"
        assert isinstance(target, BaseParentState), "Expected target be an instance of BaseParentState"
        assert isinstance(target, GameEntity), "Expected target to duck type to GameEntity"
        assert isinstance(target, EntityParentState), "Expected target to duck type to EntityParentState"

        assert len(target._substates_manifest) == 2, "Expected two substates in _substates_manifest"
        assert isinstance(target.substates[0], BaseGameSubState), "Expected first substate to be instance of BaseGameSubState"
        assert isinstance(target.substates[1], TargetedSubState), "Expected second substate to be instance of TargetedSubState"

        assert initial_targeter == None, "Expected initial targeter to be None"
        assert initial_target_state == 'unknown', "Expected initial perception state to be 'unknown'" # type: ignore
        assert initial_target_state_vector == {'on_map': False, 'is_target': False}, "Expected initial state_vector to have 'on_map' set to False and 'is_target' set to False"
        assert initial_hp == 100, "Expected initial hp to be 100"
        assert initial_max_hp == 100, "Expected initial max_hp to be 100"

        assert set_location_target_state == 'not_targeted', "Expected perception state to be 'not_targeted' after setting location" # type: ignore
        assert set_location_state_vector['on_map'] == True, "Expected state_vector to have 'on_map' set to True after setting location"
        assert with_targeter_state == 'targeted', "Expected perception state to be 'targeted' after setting targeter" # type: ignore
        assert with_targeter_state_vector['is_target'] == True, "Expected state_vector to have 'is_target' set to True after setting targeter"
        assert after_damage_target_state == 'targeted', "Expected perception state to remain 'targeted' after taking damage" # type: ignore
        assert after_damage_state_vector['is_target'] == True, "Expected state_vector to have 'is_target' remain True after taking damage"
        assert after_damage_hp == 70, "Expected hp to be 70 after taking 30 damage"
        assert after_damage_max_hp == 100, "Expected max_hp to remain 100 after taking damage"

        assert final_hp == after_damage_hp, "Expected hp to remain unchanged after action_locked state"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    # Atavise
    finally:
        pass

def test_entity_targeting_entity():
    try:
        # Arrange
        store = GameStore()
        store.atlas = Atlas(store=store)
        tile_layout = store.atlas.active.get_tile_layout('floor')
        if tile_layout is not None:
            tile_layout[0:10,0:10] = True
        store.atlas.active.set_tiles(tile_layout, graphic_name='floor')
        store.portfolio = DummyPortfolio() # type: ignore

        targeter = TargetingEntity(store=store, name='targeting_entity')
        target = DummyTarget()
        target.location = TileCoordinate.from_tuple((10,0))

        store.portfolio.live_actors = [target] # type: ignore

        # Act 
        initial_target = targeter.target # Expect None
        initial_targeter_state = targeter.focus.state # type: ignore | Expect 'unknown'
        initial_targeter_state_vector = targeter.state_vector.copy()

        targeter.location = TileCoordinate.from_tuple((0,0))
        targeter.update()
        set_location_targeter_state = targeter.focus.state # type: ignore | Expect 'idle'
        set_location_state_vector = targeter.state_vector.copy()

        targeter.target = target # type: ignore
        targeter.update()
        with_target_state = targeter.focus.state # type: ignore | Expect 'searching'
        with_target_state_vector = targeter.state_vector.copy()

        target.location = TileCoordinate.from_tuple((6,0))
        targeter.update()
        closer_target_state = targeter.focus.state # type: ignore | Expect 'tracking'
        closer_target_state_vector = targeter.state_vector.copy()

        target.location = TileCoordinate.from_tuple((1,0))
        target.target = targeter # type: ignore
        targeter.update()
        closest_target_state = targeter.focus.state # type: ignore | Expect 'targeting'
        closest_target_state_vector = targeter.state_vector.copy()
        
        targeter.clear_target()
        targeter.update()
        cleared_target = targeter.target
        cleared_targeter_state = targeter.focus.state # type: ignore

        target.location = TileCoordinate.from_tuple((6,6))
        targeter.acquire_target()
        targeter.update()
        acquired_target = targeter.target
        acquired_targeter_state = targeter.focus.state # type: ignore

        targeter.action_locked = True
        targeter.hp = 10
        final_hp = targeter.hp

        # Assert
        assert isinstance(targeter, TargetingEntity), "Expected targeter to be instance of TargetingEntity"
        assert isinstance(targeter, BaseGameEntity), "Expected targeter to be instance of BaseGameEntity"
        assert isinstance(targeter, BaseParentState), "Expected targeter to be an instance of BaseParentState"
        assert isinstance(targeter, GameEntity), "Expected target to duck type to GameEntity"
        assert isinstance(targeter, EntityParentState), "Expected target to duck type to EntityParentState"

        assert len(targeter._substates_manifest) == 2, "Expected two substates in _substates_manifest"
        assert isinstance(targeter.substates[0], BaseGameSubState), "Expected first substate to be instance of BaseGameSubState"
        assert isinstance(targeter.substates[1], TargetingSubState), "Expected second substate to be instance of TargetingSubState"

        assert initial_target == None, "Expected initial target to be None"
        assert initial_targeter_state == 'unknown', "Expected initial focus state to be 'unknown'" # type: ignore
        assert initial_targeter_state_vector == {'on_map': False, 'target_in_fov': False, 'target_is_hostile': False, 'has_target': False}, "Expected initial state_vector to have 'on_map' set to False, 'target_in_fov' set to False, and 'target_is_hostile' set to False"

        assert set_location_targeter_state == 'idle', "Expected focus state to be 'idle' after setting location" # type: ignore
        assert set_location_state_vector['on_map'] == True, "Expected state_vector to have 'on_map' set to True after setting location"

        assert with_target_state == 'searching', "Expected focus state to be 'searching' after setting target" # type: ignore
        assert with_target_state_vector['target_in_fov'] == False, "Expected state_vector to have 'target_in_fov' set to False after setting target"
        assert with_target_state_vector['target_is_hostile'] == False, "Expected state_vector to have 'target_is_hostile' set to False after setting target"
        assert with_target_state_vector['has_target'] == True, "Expected state_vector to have 'has_target' set to True after setting target"

        assert closer_target_state == 'tracking', "Expected focus state to be 'tracking' after moving target closer" # type: ignore
        assert closer_target_state_vector['target_in_fov'] == True, "Expected state_vector to have 'target_in_fov' set to True after moving target closer"
        assert closer_target_state_vector['target_is_hostile'] == False, "Expected state_vector to have 'target_is_hostile' set to False after moving target closer"
        assert closer_target_state_vector['has_target'] == True, "Expected state_vector to have 'has_target' set to True after moving target closer"

        assert closest_target_state == 'targeting', "Expected focus state to be 'targeting' after moving target into hostile range" # type: ignore
        assert closest_target_state_vector['target_in_fov'] == True, "Expected state_vector to have 'target_in_fov' set to True after moving target into hostile range"
        assert closest_target_state_vector['target_is_hostile'] == True, "Expected state_vector to have 'target_is_hostile' set to True after moving target into hostile range"
        assert closest_target_state_vector['has_target'] == True, "Expected state_vector to have 'has_target' set to True after moving target into hostile range"

        assert cleared_target == None, "Expected target to be None after clearing target"
        assert cleared_targeter_state == 'idle', "Expected focus state to be 'idle' after clearing target" # type: ignore

        assert acquired_target == target, "Expected acquired target to be the targetable_target after acquiring target"
        assert acquired_targeter_state == 'tracking', "Expected focus state to be 'tracking' after acquiring a non-hostile target" # type: ignore

        assert final_hp == targeter.hp, "Expected hp to remain unchanged after action_locked state"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    # Atavise
    finally:
        pass

class TestTargetInFov:
    """Tests for TargetingEntity.target_in_fov property"""
    
    def test_target_in_fov_when_target_is_none(self):
        """Should return False when target is None"""
        entity = TargetingEntity()
        entity.target = None
        assert entity.target_in_fov is False
    
    def test_target_in_fov_when_target_location_is_none(self):
        """Should return False when target location is None"""
        entity = TargetingEntity()
        target = TargetableEntity()
        target.location = None
        entity.target = target
        assert entity.target_in_fov is False
    
    def test_target_in_fov_when_visible_tiles_is_not_ndarray(self):
        """Should return False when visible_tiles is not an ndarray"""
        entity = TargetingEntity()
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((5, 5))
        entity.target = target
        entity._visible_tiles = None
        
        assert entity.target_in_fov is False
    
    def test_target_in_fov_when_target_is_visible(self):
        """Should return True when target is in FOV"""
        entity = TargetingEntity()
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((5, 5))
        entity.target = target
        
        # Mock is_location_in_fov to return True
        with patch.object(entity, '_visible_tiles', np.zeros((10, 10))):
            with patch.object(entity, 'is_location_in_fov', return_value=True):
                assert entity.target_in_fov is True
    
    def test_target_in_fov_when_target_is_not_visible(self):
        """Should return False when target is not in FOV"""
        entity = TargetingEntity()
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((5, 5))
        entity.target = target
        
        # Mock is_location_in_fov to return False
        with patch.object(entity, '_visible_tiles', np.zeros((10, 10))):
            with patch.object(entity, 'is_location_in_fov', return_value=False):
                assert entity.target_in_fov is False
    
    def test_target_in_fov_calls_is_location_in_fov_with_target_location(self):
        """Should call is_location_in_fov with target's location"""
        entity = TargetingEntity()
        target = TargetableEntity()
        target_location = TileCoordinate.from_tuple((5, 5))
        target.location = target_location
        entity.target = target
        
        with patch.object(entity, '_visible_tiles', np.zeros((10, 10))):
            with patch.object(entity, 'is_location_in_fov', return_value=True) as mock_is_location:
                _ = entity.target_in_fov
                mock_is_location.assert_called_once_with(target_location)

class TestDistanceToTarget:
    """Tests for TargetingEntity.distance_to_target property"""
    
    def test_distance_to_target_same_location(self):
        """Test distance when target is at same location"""
        entity = TargetingEntity()
        entity.location = TileCoordinate.from_tuple((5, 5))
        
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((5, 5))
        entity.target = target
        
        assert entity.distance_to_target == 0
    
    def test_distance_to_target_horizontal(self):
        """Test distance calculation for horizontal movement"""
        entity = TargetingEntity()
        entity.location = TileCoordinate.from_tuple((0, 0))
        
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((5, 0))
        entity.target = target
        
        assert entity.distance_to_target == 5
    
    def test_distance_to_target_vertical(self):
        """Test distance calculation for vertical movement"""
        entity = TargetingEntity()
        entity.location = TileCoordinate.from_tuple((0, 0))
        
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((0, 7))
        entity.target = target
        
        assert entity.distance_to_target == 7
    
    def test_distance_to_target_diagonal(self):
        """Test Chebyshev distance for diagonal movement"""
        entity = TargetingEntity()
        entity.location = TileCoordinate.from_tuple((0, 0))
        
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((3, 4))
        entity.target = target
        
        # Chebyshev distance is max(abs(dx), abs(dy))
        assert entity.distance_to_target == 4
    
    def test_distance_to_target_negative_coordinates(self):
        """Test distance with negative coordinate differences"""
        entity = TargetingEntity()
        entity.location = TileCoordinate.from_tuple((10, 10))
        
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((3, 5))
        entity.target = target
        
        assert entity.distance_to_target == 7
    
    def test_distance_to_target_no_target(self):
        """Test distance when no target is set"""
        entity = TargetingEntity()
        entity.location = TileCoordinate.from_tuple((5, 5))
        entity.target = None
        
        assert entity.distance_to_target == 9999
    
    def test_distance_to_target_no_location(self):
        """Test distance when entity has no location"""
        entity = TargetingEntity()
        entity.location = None
        
        target = TargetableEntity()
        target.location = TileCoordinate.from_tuple((5, 5))
        entity.target = target
        
        assert entity.distance_to_target == 9999
    
    def test_distance_to_target_no_target_location(self):
        """Test distance when target has no location"""
        entity = TargetingEntity()
        entity.location = TileCoordinate.from_tuple((5, 5))
        
        target = TargetableEntity()
        target.location = None
        entity.target = target
        
        assert entity.distance_to_target == 9999
    
    def test_distance_to_target_all_none(self):
        """Test distance when everything is None"""
        entity = TargetingEntity()
        entity.location = None
        entity.target = None
        
        assert entity.distance_to_target == 9999

class TestUpdateVisibleTiles:
    
    def test_update_visible_tiles_with_no_store(self):
        """Test that visible_tiles is None when store is not set"""
        entity = TargetingEntity()
        entity.update_visible_tiles()
        assert entity.visible_tiles is None
    
    def test_update_visible_tiles_with_no_atlas(self):
        """Test that visible_tiles is None when store has no atlas"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = None
        entity.update_visible_tiles()
        assert entity.visible_tiles is None
    
    def test_update_visible_tiles_with_no_location(self):
        """Test that visible_tiles is None when entity has no location"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        entity.store.atlas.active.blocks_vision = np.zeros((10, 10), dtype=bool)
        entity.location = None
        entity.update_visible_tiles()
        assert entity.visible_tiles is None
    
    def test_update_visible_tiles_with_non_ndarray_blocking_tiles(self):
        """Test that visible_tiles is None when blocking_tiles is not an ndarray"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        entity.store.atlas.active.blocks_vision = "not an array"
        entity.location = TileCoordinate.from_tuple((5, 5))
        entity.update_visible_tiles()
        assert entity.visible_tiles is None
    
    @patch('entity_componentslibrary.compute_fov')
    def test_update_visible_tiles_success(self, mock_compute_fov):
        """Test successful computation of visible tiles"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        
        blocking_tiles = np.zeros((20, 20), dtype=bool)
        blocking_tiles[10, 10] = True
        entity.store.atlas.active.blocks_vision = blocking_tiles
        
        entity.location = TileCoordinate.from_tuple((5, 5))
        entity._fov_radius = 6
        
        expected_visible = np.ones((20, 20), dtype=bool)
        mock_compute_fov.return_value = expected_visible
        
        entity.update_visible_tiles()
        
        mock_compute_fov.assert_called_once()
        call_args = mock_compute_fov.call_args
        
        # Verify inverted blocking_tiles was passed
        np.testing.assert_array_equal(call_args[0][0], ~blocking_tiles)
        assert call_args[0][1] == (5, 5)
        assert call_args[1]['radius'] == 6
        assert entity.visible_tiles is expected_visible
    
    @patch('entity_componentslibrary.compute_fov')
    def test_update_visible_tiles_with_custom_fov_radius(self, mock_compute_fov):
        """Test that custom fov_radius is used in compute_fov"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        entity.store.atlas.active.blocks_vision = np.zeros((20, 20), dtype=bool)
        entity.location = TileCoordinate.from_tuple((10, 10))
        entity._fov_radius = 12
        
        mock_compute_fov.return_value = np.ones((20, 20), dtype=bool)
        
        entity.update_visible_tiles()
        
        assert mock_compute_fov.call_args[1]['radius'] == 12
    
    @patch('entity_componentslibrary.compute_fov')
    @patch('entity_componentslibrary.libtcodpy')
    def test_update_visible_tiles_uses_restrictive_fov(self, mock_libtcodpy, mock_compute_fov):
        """Test that FOV_RESTRICTIVE algorithm is used"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        entity.store.atlas.active.blocks_vision = np.zeros((20, 20), dtype=bool)
        entity.location = TileCoordinate.from_tuple((5, 5))
        
        mock_compute_fov.return_value = np.ones((20, 20), dtype=bool)
        
        entity.update_visible_tiles()
        
        assert mock_compute_fov.call_args[1]['algorithm'] == mock_libtcodpy.FOV_RESTRICTIVE

class TestIsLocationInFov:
    
    def test_returns_false_when_visible_tiles_is_none(self):
        entity = TargetingEntity()
        entity.visible_tiles = None
        location = TileCoordinate.from_tuple((5, 5))
        
        assert entity.is_location_in_fov(location) is False
    
    def test_returns_false_when_visible_tiles_is_not_ndarray(self):
        entity = TargetingEntity()
        entity.visible_tiles = [[True, False], [False, True]]  # type: ignore
        location = TileCoordinate.from_tuple((0, 0))
        
        assert entity.is_location_in_fov(location) is False
    
    def test_returns_false_when_location_is_none(self):
        entity = TargetingEntity()
        entity.visible_tiles = np.zeros((10, 10), dtype=bool)
        
        assert entity.is_location_in_fov(None) is False
    
    def test_returns_true_when_location_is_visible(self):
        entity = TargetingEntity()
        visible_tiles = np.zeros((10, 10), dtype=bool)
        visible_tiles[5, 3] = True
        entity.visible_tiles = visible_tiles
        location = TileCoordinate.from_tuple((5, 3))
        
        with patch.object(entity, 'update_visible_tiles'):
            result = entity.is_location_in_fov(location)
        
        assert result is True
    
    def test_returns_false_when_location_is_not_visible(self):
        entity = TargetingEntity()
        visible_tiles = np.zeros((10, 10), dtype=bool)
        visible_tiles[5, 3] = False
        entity.visible_tiles = visible_tiles
        location = TileCoordinate.from_tuple((5, 3))
        
        with patch.object(entity, 'update_visible_tiles'):
            result = entity.is_location_in_fov(location)
        
        assert result is False
    
    def test_calls_update_visible_tiles(self):
        entity = TargetingEntity()
        visible_tiles = np.ones((10, 10), dtype=bool)
        entity.visible_tiles = visible_tiles
        location = TileCoordinate.from_tuple((2, 2))
        
        with patch.object(entity, 'update_visible_tiles') as mock_update:
            entity.is_location_in_fov(location)
            mock_update.assert_called_once()
    
    def test_handles_edge_coordinates(self):
        entity = TargetingEntity()
        visible_tiles = np.zeros((10, 10), dtype=bool)
        visible_tiles[0, 0] = True
        visible_tiles[9, 9] = True
        entity.visible_tiles = visible_tiles
        
        with patch.object(entity, 'update_visible_tiles'):
            assert entity.is_location_in_fov(TileCoordinate.from_tuple((0, 0))) is True
            assert entity.is_location_in_fov(TileCoordinate.from_tuple((9, 9))) is True
            assert entity.is_location_in_fov(TileCoordinate.from_tuple((0, 9))) is False
            
class TestIsLocationInEarshot:
    
    def test_returns_false_when_earshot_tiles_is_none(self):
        entity = TargetingEntity()
        entity.earshot_tiles = None
        location = TileCoordinate.from_tuple((5, 5))
        
        assert entity.is_location_in_earshot(location) is False
    
    def test_returns_false_when_earshot_tiles_is_not_ndarray(self):
        entity = TargetingEntity()
        entity.earshot_tiles = [] #type: ignore
        location = TileCoordinate.from_tuple((5, 5))
        
        assert entity.is_location_in_earshot(location) is False
    
    def test_returns_false_when_location_is_none(self):
        entity = TargetingEntity()
        entity.earshot_tiles = np.zeros((10, 10), dtype=bool)
        
        assert entity.is_location_in_earshot(None) is False
    
    def test_returns_true_when_location_is_in_earshot(self):
        entity = TargetingEntity()
        entity.earshot_tiles = np.zeros((10, 10), dtype=bool)
        entity.earshot_tiles[5, 5] = True
        location = TileCoordinate.from_tuple((5, 5))
        
        with patch.object(entity, 'update_earshot_tiles'):
            result = entity.is_location_in_earshot(location)
        
        assert result is True
    
    def test_returns_false_when_location_is_not_in_earshot(self):
        entity = TargetingEntity()
        entity.earshot_tiles = np.zeros((10, 10), dtype=bool)
        entity.earshot_tiles[5, 5] = False
        location = TileCoordinate.from_tuple((5, 5))
        
        with patch.object(entity, 'update_earshot_tiles'):
            result = entity.is_location_in_earshot(location)
        
        assert result is False
    
    def test_calls_update_earshot_tiles_when_earshot_tiles_is_ndarray(self):
        entity = TargetingEntity()
        entity.earshot_tiles = np.zeros((10, 10), dtype=bool)
        entity.earshot_tiles[5, 5] = True
        location = TileCoordinate.from_tuple((5, 5))
        
        with patch.object(entity, 'update_earshot_tiles') as mock_update:
            entity.is_location_in_earshot(location)
            mock_update.assert_called_once()
    
    def test_accesses_correct_array_indices(self):
        entity = TargetingEntity()
        entity.earshot_tiles = np.zeros((10, 10), dtype=bool)
        entity.earshot_tiles[3, 7] = True
        location = TileCoordinate.from_tuple((3, 7))
        
        with patch.object(entity, 'update_earshot_tiles'):
            result = entity.is_location_in_earshot(location)
        
        assert result is True
    
    def test_handles_boundary_coordinates(self):
        entity = TargetingEntity()
        entity.earshot_tiles = np.zeros((10, 10), dtype=bool)
        entity.earshot_tiles[0, 0] = True
        entity.earshot_tiles[9, 9] = True
        
        with patch.object(entity, 'update_earshot_tiles'):
            assert entity.is_location_in_earshot(TileCoordinate.from_tuple((0, 0))) is True
            assert entity.is_location_in_earshot(TileCoordinate.from_tuple((9, 9))) is True

class TestTilesInRange:
    """Test suite for TargetingEntity.tiles_in_range method"""
    
    def test_tiles_in_range_no_store(self):
        """Test tiles_in_range returns None when entity has no store"""
        entity = TargetingEntity()
        entity.store = None
        entity.location = TileCoordinate.from_tuple((5, 5))
        
        result = entity.tiles_in_range(radius=6)
        
        assert result is None
    
    def test_tiles_in_range_no_atlas(self):
        """Test tiles_in_range returns None when store has no atlas"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = None
        entity.location = TileCoordinate.from_tuple((5, 5))
        
        result = entity.tiles_in_range(radius=6)
        
        assert result is None
    
    def test_tiles_in_range_no_location(self):
        """Test tiles_in_range returns None when entity has no location"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        entity.store.atlas.active.blocks_vision = np.array([[False, True], [True, False]])
        entity.location = None
        
        result = entity.tiles_in_range(radius=6)
        
        assert result is None
    
    def test_tiles_in_range_blocking_tiles_not_ndarray(self):
        """Test tiles_in_range returns None when blocks_vision is not an ndarray"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        entity.store.atlas.active.blocks_vision = [[False, True], [True, False]]
        entity.location = TileCoordinate.from_tuple((5, 5))
        
        result = entity.tiles_in_range(radius=6)
        
        assert result is None
    
    @patch('entity_componentslibrary.compute_fov')
    def test_tiles_in_range_success(self, mock_compute_fov):
        """Test tiles_in_range successfully computes FOV"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        blocking_tiles = np.array([[False, True], [True, False]])
        entity.store.atlas.active.blocks_vision = blocking_tiles
        entity.location = TileCoordinate.from_tuple((5, 5))
        
        expected_fov = np.array([[True, False], [False, True]])
        mock_compute_fov.return_value = expected_fov
        
        result = entity.tiles_in_range(radius=6)
        
        mock_compute_fov.assert_called_once()
        call_args = mock_compute_fov.call_args
        assert np.array_equal(call_args[0][0], ~blocking_tiles)
        assert call_args[0][1] == (5, 5)
        assert call_args[1]['radius'] == 6
        assert np.array_equal(result, expected_fov) # type: ignore
    
    @patch('entity_componentslibrary.compute_fov')
    def test_tiles_in_range_different_radius(self, mock_compute_fov):
        """Test tiles_in_range with different radius values"""
        entity = TargetingEntity()
        entity.store = Mock()
        entity.store.atlas = Mock()
        entity.store.atlas.active = Mock()
        blocking_tiles = np.array([[False, True], [True, False]])
        entity.store.atlas.active.blocks_vision = blocking_tiles
        entity.location = TileCoordinate.from_tuple((3, 7))
        
        expected_fov = np.array([[True, True], [True, True]])
        mock_compute_fov.return_value = expected_fov
        
        result = entity.tiles_in_range(radius=10)
        
        call_args = mock_compute_fov.call_args
        assert call_args[0][1] == (3, 7)
        assert call_args[1]['radius'] == 10

def test_entity_combat_entity():
    try:
        # Arrange
        store = GameStore()
        store.atlas = Atlas(store=store)
        tile_layout = store.atlas.active.get_tile_layout('floor')
        if tile_layout is not None:
            tile_layout[0:10,0:10] = True
        store.atlas.active.set_tiles(tile_layout, graphic_name='floor')
        store.portfolio = DummyPortfolio() # type: ignore

        combatant = CombatEntity(store=store, name='combatant_entity')
        combatant.hp = 100
        combatant.max_hp = 100
        combatant.focus.threat_level_threshold = 9999 # type: ignore

        target = DummyTarget()
        target.location = TileCoordinate.from_tuple((10,0))
        target.hp = 100
        target.max_hp = 100

        store.portfolio.live_actors = [target] # type: ignore

        # Act
        initial_target = combatant.target # Expect None
        initial_focus_state = combatant.focus.state # type: ignore | Expect 'unknown'
        initial_combat_state = combatant.combat.state # type: ignore | Expect 'unknown'
        initial_state_vector = combatant.state_vector.copy()
        initial_combatant_hp = combatant.hp
        initial_combatant_max_hp = combatant.max_hp
        initial_target_hp = target.hp
        initial_target_max_hp = target.max_hp

        combatant.location = TileCoordinate.from_tuple((0,0))
        target.location = TileCoordinate.from_tuple((6,6))
        combatant.update()
        set_location_focus_state = combatant.focus.state # type: ignore | Expect 'idle'
        set_location_combat_state = combatant.combat.state # type: ignore | Expect 'peaceful'
        set_location_state_vector = combatant.state_vector.copy()

        combatant.set_target(target) # type: ignore
        target.location = TileCoordinate.from_tuple((3,3))
        combatant.update()
        with_target_focus_state = combatant.focus.state # type: ignore | Expect 'tracking'
        with_target_combat_state = combatant.combat.state # type: ignore | Expect 'peaceful'
        with_target_state_vector = combatant.state_vector.copy()

        target.location = TileCoordinate.from_tuple((1,1))
        combatant.update()
        moved_target_focus_state = combatant.focus.state # type: ignore | Expect 'tracking'
        moved_target_combat_state = combatant.combat.state # type: ignore | Expect 'disengaged'
        moved_target_state_vector = combatant.state_vector.copy()

        combatant.focus.threat_level_threshold = 100 # type: ignore
        target.target = combatant # type: ignore
        combatant.update()
        high_threat_focus_state = combatant.focus.state # type: ignore | Expect 'targeting'
        high_threat_combat_state = combatant.combat.state # type: ignore | Expect 'fighting'
        high_threat_state_vector = combatant.state_vector.copy()

        target.take_damage(combatant.attack())
        combatant.update()
        post_attack_focus_state = combatant.focus.state # type: ignore | Expect 'targeting'
        post_attack_combat_state = combatant.combat.state # type: ignore | Expect 'fighting'
        post_attack_state_vector = combatant.state_vector.copy()
        post_attack_target_hp = target.hp
        post_attack_combatant_hp = combatant.hp

        combatant.take_damage(10 - combatant.defend())
        combatant.update()
        post_defense_focus_state = combatant.focus.state # type: ignore | Expect 'targeting'
        post_defense_combat_state = combatant.combat.state # type: ignore | Expect 'fighting'
        post_defense_state_vector = combatant.state_vector.copy()
        post_defense_combatant_hp = combatant.hp

        combatant.action_locked = True
        combatant.hp = 10
        final_hp = combatant.hp

        # Assert
        assert isinstance(combatant, CombatEntity), "Expected combatant to be instance of CombatEntity"
        assert isinstance(combatant, BaseGameEntity), "Expected combatant to be instance of BaseGameEntity"
        assert isinstance(combatant, BaseParentState), "Expected combatant be an instance of BaseParentState"
        assert isinstance(combatant, GameEntity), "Expected combatant to duck type to GameEntity"
        assert isinstance(combatant, EntityParentState), "Expected combatant to duck type to EntityParentState"

        assert len(combatant._substates_manifest) == 4, "Expected four substates in _substates_manifest"
        assert isinstance(combatant.substates[0], BaseGameSubState), "Expected first substate to be instance of BaseGameSubState"
        assert isinstance(combatant.substates[1], TargetedSubState), "Expected second substate to be instance of TargetedSubState"
        assert isinstance(combatant.substates[2], TargetingSubState), "Expected third substate to be instance of TargetingSubState"
        assert isinstance(combatant.substates[3], CombatSubState), "Expected fourth substate to be instance of CombatSubState"

        assert initial_target == None, "Expected initial target to be None"
        assert initial_focus_state == 'unknown', "Expected initial focus state to be 'unknown'" # type: ignore
        assert initial_combat_state == 'unknown', "Expected initial combat state to be 'unknown'" # type: ignore
        assert initial_state_vector == {'on_map': False, 'is_target': False, 'has_target': False, 'target_in_fov': False, 'target_is_hostile': False, 'in_melee_range': False}, "Expected initial state_vector to have 'on_map' set to False, 'has_target' set to False, 'target_in_fov' set to False, and 'target_is_hostile' set to False"
        assert initial_combatant_hp == 100, "Expected initial combatant hp to be 100"
        assert initial_combatant_max_hp == 100, "Expected initial combatant max_hp to be 100"
        assert initial_target_hp == 100, "Expected initial target hp to be 100"
        assert initial_target_max_hp == 100, "Expected initial target max_hp to be 100"

        assert set_location_focus_state == 'idle', "Expected focus state to be 'idle' after setting location" # type: ignore
        assert set_location_combat_state == 'peaceful', "Expected combat state to be 'peaceful' after setting location" # type: ignore
        assert set_location_state_vector['on_map'] == True, "Expected state_vector to have 'on_map' set to True after setting location"
        
        assert with_target_focus_state == 'tracking', "Expected focus state to be 'tracking' after setting target" # type: ignore
        assert with_target_combat_state == 'peaceful', "Expected combat state to be 'peaceful' after setting target" # type: ignore
        assert with_target_state_vector['has_target'] == True, "Expected state_vector to have 'has_target' set to True after setting target"

        assert moved_target_focus_state == 'tracking', "Expected focus state to be 'tracking' after moving target closer" # type: ignore
        assert moved_target_combat_state == 'disengaged', "Expected combat state to be 'disengaged' after moving target closer" # type: ignore
        assert moved_target_state_vector['has_target'] == True, "Expected state_vector to have 'has_target' set to True after moving target closer"

        assert high_threat_focus_state == 'targeting', "Expected focus state to be 'targeting' after raising threat level" # type: ignore
        assert high_threat_combat_state == 'fighting', "Expected combat state to be 'fighting' after raising threat level" # type: ignore
        assert high_threat_state_vector['target_is_hostile'] == True, "Expected state_vector to have 'target_is_hostile' set to True after raising threat level"
        assert high_threat_state_vector['in_melee_range'] == True, "Expected state_vector to have 'in_melee_range' set to True after raising threat level"

        assert post_attack_focus_state == 'targeting', "Expected focus state to remain 'targeting' after attacking" # type: ignore
        assert post_attack_combat_state == 'fighting', "Expected combat state to remain 'fighting' after attacking" # type: ignore
        assert post_attack_state_vector['target_is_hostile'] == True, "Expected state_vector to have 'target_is_hostile' remain True after attacking"
        assert post_attack_state_vector['in_melee_range'] == True, "Expected state_vector to have 'in_melee_range' remain True after attacking"
        assert post_attack_target_hp == 90, "Expected target hp to be 90 (100 - 10 attack) after taking damage"
        assert post_attack_combatant_hp == 100, "Expected combatant hp to remain 100 after attacking"

        assert post_defense_focus_state == 'targeting', "Expected focus state to remain 'targeting' after defending" # type: ignore
        assert post_defense_combat_state == 'fighting', "Expected combat state to remain 'fighting' after defending" # type: ignore
        assert post_defense_state_vector['target_is_hostile'] == True, "Expected state_vector to have 'target_is_hostile' remain True after defending"
        assert post_defense_state_vector['in_melee_range'] == True, "Expected state_vector to have 'in_melee_range' remain True after defending"
        assert post_defense_combatant_hp == 95, "Expected combatant hp to be 95 (100 - 10 attack + 5 defense) after taking damage"

        assert final_hp == post_defense_combatant_hp, "Expected hp to remain unchanged after action_locked state"

    except AssertionError as e:
        pytest.fail(str(e))
    
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_entity_character():
    try:
        # Arrange
        character = Character(name='character_entity', symbol='@', color=(255, 255, 255))
        character.hp = 100
        character.max_hp = 100

        # Act
        initial_blocks_movement = character.blocks_movement
        initial_invulnerable = character.is_invulnerable
        initial_symbol = character.symbol
        initial_color = character.color
        initial_name = character.name
        character.location = TileCoordinate.from_tuple((0,0))
        character.update()
        initial_health_state = character.health.state # type: ignore | Expect 'healthy'
        initial_is_alive = character.is_alive

        character.take_damage(35)
        character.update()
        injured_health_state = character.health.state # type: ignore | Expect 'injured'

        character.take_damage(45)
        character.update()
        critical_health_state = character.health.state # type: ignore | Expect 'critical'

        character.take_damage(20)
        character.update()
        unconscious_health_state = character.health.state # type: ignore | Expect 'unconscious'

        character.die()
        character.update()
        dead_health_state = character.health.state # type: ignore | Expect 'dead'

        after_death_blocks_movement = character.blocks_movement
        after_death_invulnerable = character.is_invulnerable
        after_death_is_alive = character.is_alive
        after_death_symbol = character.symbol
        after_death_color = character.color
        after_death_name = character.name

        character.action_locked = True
        character.hp = 10
        final_hp = character.hp

        # Assert
        assert isinstance(character, Character), "Expected character to be instance of Character"
        assert isinstance(character, CombatEntity), "Expected character to be instance of CombatEntity"
        assert isinstance(character, TargetingEntity), "Expected character to be instance of TargetingEntity"
        assert isinstance(character, TargetableEntity), "Expected character to be instance of TargetableEntity"
        assert isinstance(character, MobileEntity), "Expected character to be instance of MobileEntity"
        assert isinstance(character, BaseGameEntity), "Expected character to be instance of BaseGameEntity"
        assert isinstance(character, BaseParentState), "Expected character be an instance of BaseParentState"
        assert isinstance(character, GameEntity), "Expected character to duck type to GameEntity"
        assert isinstance(character, EntityParentState), "Expected character to duck type to EntityParentState"

        assert len(character._substates_manifest) == 6, "Expected six substates in _substates_manifest"
        assert isinstance(character.substates[0], BaseGameSubState), "Expected first substate to be instance of BaseGameSubState"
        assert isinstance(character.substates[1], TargetedSubState), "Expected second substate to be instance of TargetedSubState"
        assert isinstance(character.substates[2], TargetingSubState), "Expected third substate to be instance of TargetingSubState"
        assert isinstance(character.substates[3], CombatSubState), "Expected fourth substate to be instance of CombatSubState"
        assert isinstance(character.substates[4], CharacterHealthSubState), "Expected fifth substate to be instance of CharacterHealthSubState"
        assert isinstance(character.substates[5], CollisionSubState), "Expected sixth substate to be instance of CollisionSubState"

        assert initial_blocks_movement == True, "Expected blocks_movement to be True initially"
        assert initial_invulnerable == False, "Expected is_invulnerable to be False initially"
        assert initial_symbol == '@', "Expected initial symbol to be '@'"
        assert initial_color == (255, 255, 255), "Expected initial color to be white"
        assert initial_name == 'character_entity', "Expected initial name to be 'character_entity'"
        assert initial_health_state == 'healthy', "Expected health state to be 'healthy' initially"
        assert initial_is_alive == True, "Expected is_alive to be True initially"

        assert injured_health_state == 'injured', "Expected health state to be 'injured' after taking 35 damage"
        assert critical_health_state == 'critical', "Expected health state to be 'critical' after taking additional 45 damage"
        assert unconscious_health_state == 'unconscious', "Expected health state to be 'unconscious' after taking additional 20 damage"
        assert dead_health_state == 'dead', "Expected health state to be 'dead' after death"

        assert after_death_blocks_movement == False, "Expected blocks_movement to be False after death"
        assert after_death_invulnerable == True, "Expected is_invulnerable to be True after death"
        assert after_death_symbol == '%', "Expected symbol to change to '%' after death"
        assert after_death_color == (191, 0, 0), "Expected color to change to red after death"
        assert after_death_name == 'remains of character_entity', "Expected name to change to 'remains of character_entity' after death"
        assert after_death_is_alive == False, "Expected is_alive to be False after death"

        assert final_hp == None, "Expected hp to be the death value of None after action_locked state"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    # Atavise
    finally:
        pass

def test_entity_player_character():
    try:
        player = PlayerCharacter(name='player_entity', symbol='@', color=(0, 255, 0))
        assert isinstance(player, PlayerCharacter), "Expected player to be instance of PlayerCharacter"
    
    except AssertionError as e:
        pytest.fail(str(e))
    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    finally:
        pass

def test_entity_ai_character():
    try:
        # Arrange
        store = GameStore()
        store.atlas = Atlas(store=store)
        tile_layout = store.atlas.active.get_tile_layout('floor')
        if tile_layout is not None:
            tile_layout[0:10,0:10] = True
        store.atlas.active.set_tiles(tile_layout, graphic_name='floor')
        map_size = store.atlas.active.grid.size
        store.portfolio = DummyPortfolio() # type: ignore
        
        character = AICharacter(store=store, name='character_entity', symbol='@', color=(255, 255, 255), ai=SubLoopHandler(behaviors={investigate,}))
        character.location = TileCoordinate.from_tuple((0,0), parent_map_size=map_size)
        character.ai.start()  # type: ignore | Expect LoopHandler to have start() method
        target = DummyTarget()
        target.location = TileCoordinate.from_tuple((3,0), parent_map_size=map_size)
        character.set_target(target) # type: ignore
        character.hp = 100
        character.max_hp = 100

        # Act
        initial_path = character.path
        initial_state = character.focus.state  # type: ignore | Expect 'tracking'
        character.set_path_to_target()
        after_set_path = character.path
        after_set_state = character.focus.state  # type: ignore | Expect 'tracking'
        actions_queue_size = character.ai.actions.qsize() if character.ai else None
        state_changed = character.focus.state_changed  # type: ignore

        initial_ai = character.ai
        character.die()
        after_death_ai = character.ai

        character.action_locked = True
        character.hp = 10
        final_hp = character.hp

        # Assert
        assert isinstance(character, AICharacter), "Expected character to be instance of AICharacter"
        assert isinstance(character, CombatEntity), "Expected character to be instance of CombatEntity"
        assert isinstance(character, TargetingEntity), "Expected character to be instance of TargetingEntity"
        assert isinstance(character, TargetableEntity), "Expected character to be instance of TargetableEntity"
        assert isinstance(character, MobileEntity), "Expected character to be instance of MobileEntity"
        assert isinstance(character, BaseGameEntity), "Expected character to be instance of BaseGameEntity"
        assert isinstance(character, BaseParentState), "Expected character be an instance of BaseParentState"
        assert isinstance(character, GameEntity), "Expected character to duck type to GameEntity"
        assert isinstance(character, EntityParentState), "Expected character to duck type to EntityParentState"

        assert len(character._substates_manifest) == 6, "Expected six substates in _substates_manifest"
        assert isinstance(character.substates[0], BaseGameSubState), "Expected first substate to be instance of BaseGameSubState"
        assert isinstance(character.substates[1], TargetedSubState), "Expected second substate to be instance of TargetedSubState"
        assert isinstance(character.substates[2], TargetingSubState), "Expected third substate to be instance of TargetingSubState"
        assert isinstance(character.substates[3], CombatSubState), "Expected fourth substate to be instance of CombatSubState"
        assert isinstance(character.substates[4], CharacterHealthSubState), "Expected fifth substate to be instance of CharacterHealthSubState"
        assert isinstance(character.substates[5], CollisionSubState), "Expected sixth substate to be instance of CollisionSubState"
        assert actions_queue_size == 1, "Expected AI actions queue size to be 1 after setting path to target"
        
        assert initial_path == [], "Expected initial path to be empty list"
        assert initial_state == 'tracking', "Expected initial focus state to be 'tracking'"  # type: ignore
        assert len(after_set_path) > 1, "Expected path to be set after calling set_path_to_target()"
        assert after_set_path[0] == character.location, "Expected first element of path to be character's current location"
        assert after_set_state == 'tracking', "Expected focus state to remain 'tracking' after setting path"  # type: ignore
        assert state_changed == False, "Expected state_changed to be False after setting path"

        assert isinstance(initial_ai, SubLoopHandler), "Expected initial AI to be BaseLoopHandler()"
        assert after_death_ai == None, "Expected AI to be None after death"
        assert final_hp == None, "Expected hp to be the death value of None after action_locked state"

    except AssertionError as e:
        pytest.fail(str(e))

    except Exception as e:
        pytest.fail(f"Test failed due to unexpected error: {e}")
    
    finally:
        pass

def test_entity_mob_character():
    pytest.skip()
