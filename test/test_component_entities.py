import pytest
from sys import path
path.append('c:\\Users\\jason\\workspaces\\repos\\jrl\\src')
import numpy as np
from transitions import Machine 

from core_components.entities.base  import BaseGameSubState, BaseGameEntity, BaseParentState
from core_components.entities.library import TargetedSubState, TargetingSubState, CombatSubState
from core_components.entities.types import GameEntity, EntityParentState
from core_components.maps.tiles.base import TileCoordinate
from core_components.store import GameStore

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
    pytest.skip()

def test_entity_targetable_entity():
    pytest.skip()

def test_entity_targeting_entity():
    pytest.skip()

def test_entity_combat_entity():
    pytest.skip()

def test_entity_character():
    pytest.skip()

def test_entity_player_character():
    pytest.skip()

def test_entity_ai_character():
    pytest.skip()

def test_entity_mob_character():
    pytest.skip()
